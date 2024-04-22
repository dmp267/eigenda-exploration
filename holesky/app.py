# flask app
import os
from flask import request, Flask, jsonify

from utils import pull_ipfs, push_eigenda, pull_eigenda

app = Flask(__name__)


@app.route('/disperse/<cid>', methods=['GET', 'POST'])
def disperse(cid: str):
    # print(f'cid: {cid}')
    ipfs_data = pull_ipfs(cid)
    # print(f'ipfs_data: {ipfs_data.decode()}')
    result = push_eigenda(ipfs_data)
    return jsonify(result)


@app.route('/retrieve/<batch_header_hash>/<blob_index>', methods=['GET'])
def retrieve(batch_header_hash: str, blob_index: int):
    result = pull_eigenda(batch_header_hash, blob_index)
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000)
