from flask import Flask, jsonify

from utils import retrieve_from_ipfs, disperse_to_eigenda, retrieve_from_eigenda
from sc_utils import get_store_details, store_on_chain, verify_on_chain


app = Flask(__name__)
dev = False


@app.route('/disperse/<cid>', methods=['GET', 'POST'])
def disperse(cid: str):
    # try:
    print(f'cid: {cid}')
    if dev:
        import json
        result = json.load(open('attestations/hello_proof.json', 'r'))
        print(store_on_chain("dev", result))
    else:
        ipfs_data = retrieve_from_ipfs(cid)
        result = disperse_to_eigenda(cid, ipfs_data)
        print(store_on_chain(cid, result))
    return jsonify(result)
    # except Exception as e:
    #     print(f'error pushing data with CID {cid}')
    #     return jsonify(f"Error: {e}")


@app.route('/retrieve/<cid>', methods=['GET', 'POST'])
def retrieve(cid: str):
    # try:
    if dev:
        cid = "dev"
    storage_details = get_store_details(cid)
    result = retrieve_from_eigenda(storage_details['batch_header_hash'], storage_details['blob_index'])
    return jsonify(result)
    # except Exception as e:
    #     print(f'data with CID {cid} not yet found in storage')
    #     return jsonify(f"Error: {e}")


@app.route('/verify/<cid>', methods=['GET', 'POST'])
def verify(cid: str):
    # try:
    if dev:
        cid = "dev"
    print(verify_on_chain(cid))
    return jsonify("success")
    # except Exception as e:
    #     print(f'erorr verifying data with CID {cid}')
    #     return jsonify(f"Error: {e}")


@app.route('/health', methods=['GET'])
def health():
    return jsonify("Healthy")


if __name__ == '__main__':
    app.run(port=5000)
