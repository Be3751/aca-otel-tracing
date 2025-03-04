import json
import time
import logging
import requests
import os

logging.basicConfig(level=logging.INFO)

# TODO: 環境変数にURLを指定する
base_url = os.getenv('BASE_URL', 'http://ca-order-processor-c3xgys6u6lm2y')
# Adding app id as part of the header
headers = {'content-type': 'application/json'}

while(True):
  for i in range(1, 20):
    print('Ordering item: ' + str(i), flush=True)

    order = {'orderId': i}

    result = requests.post(
        url='%s/orders' % (base_url),
        data=json.dumps(order),
        headers=headers
    )

    print('Order passed: ' + json.dumps(order), flush=True)

    time.sleep(1)
  time.sleep(10)