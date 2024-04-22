# flask app
import os
from flask import Flask, jsonify

from utils import pull_ipfs, push_eigenda, pull_eigenda

app = Flask(__name__)


@app.route('/disperse', methods=['POST'])
def disperse(data):
    cid = data.get('cid')
    ipfs_data = pull_ipfs(cid)
    result = push_eigenda(ipfs_data)
    return jsonify(result)


@app.route('/retrieve', methods=['GET'])
def retrieve(data):
    batch_header_hash = data.get('batch_header_hash')
    blob_index = data.get('blob_index')
    result = pull_eigenda(batch_header_hash, blob_index)
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000)
