import os
import json
import time

from flask import Flask, request
import dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

print("Loading .env file", flush=True)
dotenv.load_dotenv()

account_name = os.getenv("STORAGE_ACCOUNT_NAME")
container_name = os.getenv("STORAGE_ACCOUNT_CONTAINER_NAME")
credential = DefaultAzureCredential()
account_url = f"https://{account_name}.blob.core.windows.net"

connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
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
      blob_client.upload_blob(data=json.dumps(order), overwrite=True)

    return json.dumps({'success': True}), 200, {
        'Content-Type': 'application/json'}

print("Starting receipt service", flush=True)
app.run(port=8001, host="0.0.0.0")
