import json
import time
import logging
import requests
import os

import dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

dotenv.load_dotenv()
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

configure_azure_monitor(
  connection_string=connection_string
)
tracer = trace.get_tracer(__name__)
traceparent_version = "00"
traceparent_trace_flags = "01"

logging.basicConfig(level=logging.INFO)

cnt = 0
while(True):
  print('Ordering item: ' + str(cnt), flush=True)

  order = {'orderId': cnt}

  with tracer.start_as_current_span('order') as span:
    span_context = span.get_span_context()
    trace_id = int(span_context.trace_id)
    span_id = int(span_context.span_id)
    trace_id_hex = hex(trace_id)
    span_id_hex = hex(span_id)
    trace_id_hex_value = trace_id_hex[2:]
    span_id_hex_value = span_id_hex[2:]
    traceparent = f"{traceparent_version}-{trace_id_hex_value}-{span_id_hex_value}-{traceparent_trace_flags}"

    headers = {
      'content-type': 'application/json',
      'traceparent': traceparent
    }
    result = requests.post(
        url='http://%s/orders' % (os.getenv('SERVICE_ORDER_PROCESSOR_API_NAME')),
        data=json.dumps(order),
        headers=headers
    )

  print('Order passed: ' + json.dumps(order), flush=True)
  time.sleep(60)
  cnt += 1