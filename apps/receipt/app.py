import os
import json
import time

from flask import Flask, request
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import dotenv

app = Flask(__name__)

print("Loading .env file", flush=True)
dotenv.load_dotenv()
account_name = os.getenv("STORAGE_ACCOUNT_NAME")
container_name = os.getenv("STORAGE_ACCOUNT_CONTAINER_NAME")
credential = DefaultAzureCredential()
account_url = f"https://{account_name}.blob.core.windows.net"

@app.route('/orders', methods=['POST'])
def getOrder():
    order = request.json
    print('Order received : ' + json.dumps(order), flush=True)

    ut = time.time()
    filename = f"order-{ut}.json"

    blob_service_client = BlobServiceClient(account_url, credential=credential)
    container_client = blob_service_client.get_container_client(container=container_name)

    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(data=json.dumps(order), overwrite=True)

    return json.dumps({'success': True}), 200, {
        'ContentType': 'application/json'}

print("Starting receipt service", flush=True)
app.run(port=8001, host="0.0.0.0")
