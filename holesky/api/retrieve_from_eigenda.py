from flask import request, Flask, jsonify

from retrieval_core import retrieve_data

app = Flask(__name__)


@app.route('/api/retrieve_data', methods=['POST'])
def handle_retrieve_data():
    """ Retrieves data from data availability network """

    request_data = request.get_json()
    project_id = request_data.get('project_id', '')
    if isinstance(project_id, bytes):
        print(f'project_id bytes: {project_id}')
        project_id = project_id.decode()
    if project_id == '':
        return jsonify({"error": "project_id not provided"}), 400
    
    result = retrieve_data(project_id)
    return jsonify(result)


def handler(event, context):
    return app(event, context)