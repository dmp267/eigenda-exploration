# from flask import request, Flask, jsonify
import json
from http.server import BaseHTTPRequestHandler
import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))
from retrieval_tools import retrieve_data#, retrieve_data_2

# app = Flask(__name__)
class Handler(BaseHTTPRequestHandler):


    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


    def go_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
        response = {'message': 'Hello, world!'}
        self.wfile.write(json.dumps(response).encode())


    def do_POST(self):
        """ Retrieves data from data availability network """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data)
        # project_id = request_data.get('project_id', '')
        # if isinstance(project_id, bytes):
        #     project_id = project_id.decode()
        # if project_id == '':

        blob_index = int(request_data.get('blob_index', ''))
        batch_header_hash = request_data.get('batch_header_hash', '')
        if isinstance(blob_index, str):
            blob_index = int(blob_index)
        if isinstance(batch_header_hash, str):
            # batch_header_hash = batch_header_hash.encode()
            if batch_header_hash.startswith('0x'):
                batch_header_hash = bytes.fromhex(batch_header_hash[2:])
            else:
                batch_header_hash = bytes.fromhex(batch_header_hash)
            # batch_header_hash = bytes.fromhex(batch_header_hash)

        # print(f'blob_index: {blob_index}')
        # print(f'batch_header_hash: {batch_header_hash}')

        result = retrieve_data(blob_index, batch_header_hash)
        # print('final result length:', len(result))
        final_encoded = json.dumps(result).encode()
        print('final_encoded length:', len(final_encoded))
        # else:
        #     result = retrieve_data_2(project_id)


        # if isinstance(project_id, bytes):
        #     project_id = project_id.decode()
        # if project_id == '':
        #     self.send_response(400)
        #     self.end_headers()
        #     self.wfile.write(json.dumps({"error": "project_id not provided"}).encode())
        #     return

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(final_encoded)

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
