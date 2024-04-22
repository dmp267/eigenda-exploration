# flask app
import os
from flask import request, Flask, jsonify

from utils import pull_ipfs, push_eigenda, pull_eigenda
from sc_utils import get_store_details, store_onchain, verify_onchain


app = Flask(__name__)


@app.route('/disperse/<cid>', methods=['GET', 'POST'])
def disperse(cid: str):
    print(f'cid: {cid}')
    ipfs_data = pull_ipfs(cid)
    print(f'ipfs_data: {ipfs_data.decode()}')
    result = push_eigenda(ipfs_data)
    # store_onchain(cid, result)
    return jsonify(result)


@app.route('/retrieve/<cid>', methods=['GET', 'POST'])
def retrieve(cid: str):
    try:
        storage_details = get_store_details(cid)
        result = pull_eigenda(storage_details['batch_header_hash'], storage_details['blob_index'])
        return jsonify(result)
    except Exception as e:
        print(f'data with CID {cid} not yet found in storage')
        return jsonify(f"Error: {e}")


@app.route('/verify/<cid>', methods=['GET', 'POST'])
def verify(cid: str):
    try:
        print(verify_onchain(cid))
        return jsonify("success")
    except Exception as e:
        print(f'data with CID {cid} not yet found in storage')
        return jsonify(f"Error: {e}")


@app.route('/health', methods=['GET'])
def health():
    return jsonify("Healthy")


if __name__ == '__main__':
    app.run(port=5000)
