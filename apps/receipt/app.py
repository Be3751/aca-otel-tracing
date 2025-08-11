import os
import json
import time
import sys

# Telemetry exported by Azure SDK will be automatically captured
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import get_tracer, SpanContext, SpanKind, TraceFlags
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry import context as otel_context
from opentelemetry.propagate import extract

# Configure Azure Monitor
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
from azure_monitor_config import configure_azure_monitor_telemetry
from otel_helper import OTelHelper

configure_azure_monitor_telemetry()

# Initialize OpenTelemetry helper
otel_helper = OTelHelper()

account_name = os.getenv("STORAGE_ACCOUNT_NAME", "local-storage")
container_name = os.getenv("STORAGE_ACCOUNT_CONTAINER_NAME", "local-container")
account_url = f"https://{account_name}.blob.core.windows.net"
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

# Configure Azure monitor collection telemetry pipeline
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

    # Initialize blob storage clients only if not skipping blob upload
    skip_blob_upload = os.getenv('SKIP_BLOB_UPLOAD', 'false').lower() == 'true'
    
    if not skip_blob_upload:
        blob_service_client = BlobServiceClient(account_url, credential=credential)
        container_client = blob_service_client.get_container_client(container=container_name)
        blob_client = container_client.get_blob_client(filename)
    else:
        blob_client = None

    # Define callback function for blob upload processing
    def process_blob_upload(order_data):
        # Check if we should skip blob upload in local environment
        if skip_blob_upload:
            print(f"[LOCAL MODE] Skipping blob upload for: {filename}", flush=True)
            print(f"[LOCAL MODE] Would have uploaded order: {json.dumps(order_data)}", flush=True)
        else:
            blob_client.upload_blob(data=json.dumps(order_data), overwrite=True)
            print(f"Order uploaded to blob storage: {filename}", flush=True)
        
        return True

    otel_helper.execute_with_span(
        callback=process_blob_upload,
        span_attributes={'order.id': order.get('orderId', 'unknown'), 'blob.filename': filename},
        order_data=order,
    )

    return json.dumps({'success': True}), 200, {
        'Content-Type': 'application/json'}

print("Starting receipt service", flush=True)
app.run(port=8002, host="0.0.0.0")
