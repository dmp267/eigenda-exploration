# flask app
import os
from flask import Flask, jsonify

from utils import disperse_data, retrieve_data

app = Flask(__name__)


@app.route('/disperse', methods=['POST'])
def disperse(data):
    if type(data) == str:
        data = data.encode()
    result = disperse_data(data)
    return jsonify(result)


@app.route('/retrieve', methods=['GET'])
def retrieve(data):
    batch_header_hash = data.get('batch_header_hash')
    blob_index = data.get('blob_index')
    result = retrieve_data(batch_header_hash, blob_index)
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000)
