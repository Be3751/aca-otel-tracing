import json
import os

import dotenv
import requests
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

dotenv.load_dotenv()
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
otlp_endpoint = os.getenv("OTLP_EXPORT_ENDPOINT")

# Set up OTLP exporter if endpoint is provided
if otlp_endpoint:
    provider = TracerProvider()
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)

# Configure Azure Monitor telemetry exporter
configure_azure_monitor(
  connection_string=connection_string
)
tracer = trace.get_tracer(__name__)

# Import Flask after running configure_azure_monitor()
from flask import Flask, request

app = Flask(__name__)

@app.route('/orders', methods=['POST'])
def getOrder():
    order = request.json
    print('Order received : ' + json.dumps(order), flush=True)
    
    traceparent = request.headers.get('traceparent')
    headers = {
        'content-type': 'application/json',
        'traceparent': traceparent
    }

    # Invoking a service
    with tracer.start_as_current_span('order') as span:
        result = requests.post(
            url='http://%s/orders' % (os.getenv('SERVICE_RECEIPT_API_NAME')),
            data=json.dumps(order),
            headers=headers
        )
        span.set_attribute("order.id", order.get("id", "unknown"))

    print(f"Request was sent to receipt: result = {result}", flush=True)

    return json.dumps({'success': True}), 200, {
        'ContentType': 'application/json'}
   
app.run(port=8001, host="0.0.0.0")
