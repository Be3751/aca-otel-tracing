import os
import json
import time

import dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
# Telemetry exported by Azure SDK will be automatically captured
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
from opentelemetry.trace import get_tracer, SpanContext, SpanKind, TraceFlags
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

print("Loading .env file", flush=True)
dotenv.load_dotenv()

account_name = os.getenv("STORAGE_ACCOUNT_NAME")
container_name = os.getenv("STORAGE_ACCOUNT_CONTAINER_NAME")
account_url = f"https://{account_name}.blob.core.windows.net"
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
otlp_endpoint = os.getenv("OTLP_EXPORT_ENDPOINT")

# Define a custom processor to filter your spans
class SpanFilteringProcessor(SpanProcessor):
  # Prevents exporting spans that are of kind INTERNAL
  def on_start(self, span, parent_context):  # type: ignore
      if span._kind is SpanKind.INTERNAL:
          # The trace flags are set to `DEFAULT`, which means the span is not sampled.
          # Ref: https://www.w3.org/TR/trace-context/?utm_source=chatgpt.com#examples-of-http-traceparent-headers
          span._context = SpanContext(
              span.context.trace_id,
              span.context.span_id,
              span.context.is_remote,
              TraceFlags(TraceFlags.DEFAULT),
              span.context.trace_state,
          )

# Set up OTLP exporter if endpoint is provided
if otlp_endpoint:
    provider = TracerProvider()
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    # Also add the custom span filtering processor
    provider.add_span_processor(SpanFilteringProcessor())
    trace.set_tracer_provider(provider)

# Configure Azure Monitor telemetry exporter
configure_azure_monitor(
  connection_string=connection_string
)
tracer = get_tracer(__name__)

# Import Flask after running configure_azure_monitor()
from flask import Flask, request

app = Flask(__name__)
credential = DefaultAzureCredential()

@app.route('/orders', methods=['POST'])
def getOrder():
    order = request.json
    print('Order received : ' + json.dumps(order), flush=True)

    ut = time.time()
    filename = f"order-{ut}.json"

    blob_service_client = BlobServiceClient(account_url, credential=credential)
    container_client = blob_service_client.get_container_client(container=container_name)

    blob_client = container_client.get_blob_client(filename)

    traceparent = request.headers.get('traceparent')
    carrier = {
      'traceparent': traceparent
    }
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
    with tracer.start_as_current_span('order', context=ctx) as span:
      blob_client.upload_blob(data=json.dumps(order), overwrite=True) # Call will be traced

    return json.dumps({'success': True}), 200, {
        'Content-Type': 'application/json'}

# Requests sent to the flask application will be automatically captured
@app.route("/")
def test():
    return "Test flask request"

# Exceptions that are raised within the request are automatically captured
@app.route("/exception")
def exception():
    raise Exception("Hit an exception")

# Requests sent to this endpoint will not be tracked due to
# flask_config configuration
@app.route("/ignore")
def ignore():
    return "Request received but not tracked."

print("Starting receipt service", flush=True)
app.run(port=8001, host="0.0.0.0")
