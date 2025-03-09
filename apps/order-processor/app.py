import json
import os

from flask import Flask, request
import requests

app = Flask(__name__)

base_url = os.getenv('BASE_URL', 'http://ca-receipt-c3xgys6u6lm2y')
content_type = "application/json"

@app.route('/orders', methods=['POST'])
def getOrder():
    order = request.json
    print('Order received : ' + json.dumps(order), flush=True)
    
    # traceparent = request.headers.get('traceparent')
    headers = {
        'content-type': content_type,
        # 'traceparent': traceparent
    }

    # Invoking a service
    result = requests.post(
        url='%s/orders' % (base_url),
        data=json.dumps(order),
        headers=headers
    )

    print(f"Request was sent to receipt: result = {result}", flush=True)

    return json.dumps({'success': True}), 200, {
        'ContentType': 'application/json'}
   
app.run(port=8001, host="0.0.0.0")
