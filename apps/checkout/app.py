import json
import time
import os
import sys
import requests
from opentelemetry import trace

# Configure Azure Monitor
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
from azure_monitor_config import configure_azure_monitor_telemetry
from otel_helper import OTelHelper

configure_azure_monitor_telemetry()

# Initialize OpenTelemetry helper
otel_helper = OTelHelper()

cnt = 0
while(True):
  print('Ordering item: ' + str(cnt), flush=True)

  order = {'orderId': cnt}

  # Define callback function for order processing
  def process_order(order_data):
    headers = {
      'content-type': 'application/json',
    }
    
    result = requests.post(
        url='http://%s/orders' % (os.getenv('SERVICE_ORDER_PROCESSOR_API_NAME')),
        data=json.dumps(order_data),
        headers=headers
    )
    return result

  # Execute order processing with tracing
  otel_helper.execute_with_span(
      callback=process_order,
      span_attributes={'order.id': order.get('orderId', 'unknown')},
      order_data=order
  )

  print('Order passed: ' + json.dumps(order), flush=True)
  time.sleep(60)
  cnt += 1