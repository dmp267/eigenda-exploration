# from flask import request, Flask, jsonify
import json
from http.server import BaseHTTPRequestHandler
import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))
from retrieval_tools import retrieve_data

# app = Flask(__name__)
class Handler(BaseHTTPRequestHandler):


    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()


    def do_POST(self):
        """ Retrieves data from data availability network """
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        content_length = int(self.headers['Content-Length'])
        print(f'content_length: {content_length}')
        post_data = self.rfile.read(content_length)
        
        if not post_data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "no data provided"}).encode())
            return
        try:
            request_data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid json"}).encode())
            return
        
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

# @app.route('/api/retrieve', methods=['POST'])
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

# if __name__ == '__main__':
#     app.run(port=6000)
