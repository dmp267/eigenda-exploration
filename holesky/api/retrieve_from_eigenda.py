# from flask import request, Flask, jsonify
import json
from http.server import BaseHTTPRequestHandler

from retrieval_tools import retrieve_data

# app = Flask(__name__)
class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        """ Retrieves data from data availability network """
        request_data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        project_id = request_data.get('project_id', '')
        if isinstance(project_id, bytes):
            project_id = project_id.decode()
        if project_id == '':
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "project_id not provided"}).encode())
            return
        
        result = retrieve_data(project_id)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


# @app.route('/api/retrieve_data', methods=['POST'])
# def handle_retrieve_data():
#     """ Retrieves data from data availability network """

#     request_data = request.get_json()
#     project_id = request_data.get('project_id', '')
#     if isinstance(project_id, bytes):
#         project_id = project_id.decode()
#     if project_id == '':
#         return jsonify({"error": "project_id not provided"}), 400
    
#     result = retrieve_data(project_id)
#     return jsonify(result)


# def handler(event, context):
#     return app(event, context)