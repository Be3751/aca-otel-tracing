import json
import os

import dotenv
import requests
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

dotenv.load_dotenv()
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
