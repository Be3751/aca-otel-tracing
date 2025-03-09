import json
import time
import logging
import requests
import os

logging.basicConfig(level=logging.INFO)

# TODO: 環境変数にURLを指定する
base_url = os.getenv('BASE_URL', 'http://ca-order-processor-c3xgys6u6lm2y')
headers = {'content-type': 'application/json'}

cnt = 0
while(True):
  print('Ordering item: ' + str(cnt), flush=True)

  order = {'orderId': cnt}

  result = requests.post(
      url='%s/orders' % (base_url),
      data=json.dumps(order),
      headers=headers
  )

  print('Order passed: ' + json.dumps(order), flush=True)
  time.sleep(60)
  cnt += 1