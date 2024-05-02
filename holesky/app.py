from flask import request, Flask, jsonify

from service import CARBON_DATASETS, update_dataset, retrieve_dataset, verify_dataset


app = Flask(__name__)


@app.route('/update', methods=['POST'])
def update(datasets: str = None):
    """ Updates storage of all datasets with most recent data """
    data = request.get_json()
    datasets = data.get('datasets', CARBON_DATASETS)
    result = update_dataset(datasets)
    return jsonify(result)


@app.route('/verify/<dataset_name>', methods=['GET'])
def verify(dataset_name: str):
    """ Verifies dataset storage proof in smart contract """
    result = verify_dataset(dataset_name)
    return jsonify(result)


@app.route('/retrieve/<dataset_name>', methods=['GET'])
def retrieve(dataset_name: str):
    """ Retrieves dataset from data availability network """
    result = retrieve_dataset(dataset_name)
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health():
    """ Health check for service """
    return jsonify("Healthy")


if __name__ == '__main__':
    app.run(port=5000)
