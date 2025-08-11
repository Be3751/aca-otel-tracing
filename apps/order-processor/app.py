import json
import os
import sys
import requests
from opentelemetry import trace
from opentelemetry.propagate import inject, extract

# Configure Azure Monitor
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
from azure_monitor_config import configure_azure_monitor_telemetry
from otel_helper import OTelHelper

configure_azure_monitor_telemetry()

# Initialize OpenTelemetry helper
otel_helper = OTelHelper()

tracer = trace.get_tracer(__name__)

# Import Flask after running configure_azure_monitor()
from flask import Flask, request

app = Flask(__name__)

@app.route('/orders', methods=['POST'])
def getOrder():
    order = request.json
    print('Order received : ' + json.dumps(order), flush=True)

    # Define callback function for order processing
    def process_order(order_data):
        headers = {
            'content-type': 'application/json',
        }

        result = requests.post(
            url='http://%s/orders' % (os.getenv('SERVICE_RECEIPT_API_NAME')),
            data=json.dumps(order_data),
            headers=headers
        )
        
        print(f"Request was sent to receipt: result = {result}", flush=True)
        return result

    otel_helper.execute_with_span(
        callback=process_order,
        span_attributes={'order.id': order.get('orderId', 'unknown')},
        order_data=order
    )

    return json.dumps({'success': True}), 200, {
        'ContentType': 'application/json'}
   
app.run(port=8001, host="0.0.0.0")
