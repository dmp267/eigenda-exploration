from flask import request, Flask, jsonify
from werkzeug.utils import secure_filename

from service.core import query_data, start_store_data, finish_store_data, retrieve_data
from service.utils import allowed_file, download_file, parse_file, cleanup_file, convert_to_datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data/uploads"
app.config["DEV"] = False
# mock data availability storage for demo because of finalization delay


@app.route('/disperse', methods=['POST'])
def disperse():
    """ Accepts IPFS CID of KML, downloads and parses polygon boundaries, queries 
        and aggregates the carbon data for the specified area and time range,
        stores the data on EigenDA network

        example request:

        curl -H "Content-Type: application/json" -d '{
            "project_id": "holesky-852-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", 
            "file_cid": "QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", 
            "file_type": "kml", 
            "start": "2010-01-01", 
            "end": "2023-12-32"
        }' http://127.0.0.1:6000/disperse | jq
    """
    data = request.get_json()
    project_id = data.get('project_id', 'holesky-852-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb')
    cid = data.get('cid', 'QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb')
    ftype = data.get('ftype', 'kml')
    start = convert_to_datetime(data.get('start', '2010-01-01'))
    end = convert_to_datetime(data.get('end', '2023-12-32'))

    filename = secure_filename(f'{project_id}.{ftype}')
    if not allowed_file(filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    file_data = download_file(cid)
    if not file_data:
        return jsonify({f'No data found for {cid}'}), 400
    
    file_path = f'{app.config["UPLOAD_FOLDER"]}/{filename}'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(file_data.decode())
        f.close()
    try:
        polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs = parse_file(file_path)
        query_result = query_data(polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs, start, end)
        dispersal_id = start_store_data(query_result)
        cleanup_file(file_path)
        return jsonify({
            "result": {
                "dispersal_id": dispersal_id,
                "head_cid": query_result['agb']['head_cid']}
            })
    except Exception as e:
        return jsonify({f'error: {str(e)}'}), 400


@app.route('/confirm', methods=['POST'])
def confirm():
    """ Stores the proof details on the blockchain after confirmation
        of dispersal on EigenDA network

        example request:

        curl -H "Content-Type: application/json" -d '{"project_id": "holesky-852-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", "cid": "QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", "dispersal_id": }' http://127.0.0.1:6000/store | jq
    """
    data = request.get_json()
    project_id = data.get('project_id', 'holesky-852-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb')
    head_cid = data.get('head_cid', 'QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb')
    dispersal_id = data.get('dispersal_id', '')
    try:
        finish_store_data(project_id, head_cid, dispersal_id)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/retrieve/', methods=['POST'])
def retrieve():
    """ Retrieves data from data availability network 
    
        example request:

        curl -H "Content-Type: application/json" -d '{"project_id": "852-holesky-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb"}' http://127.0.0.1:5000/retrieve | jq
    """
    data = request.get_json()
    # date = convert_to_datetime(data.get('date', '2023-12-31'))
    project_id = data.get('project_id', '852-holesky-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLk')
    try:
        result = retrieve_data(project_id)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/health', methods=['GET'])
def health():
    """ Health check for service """
    return jsonify("Healthy")


if __name__ == '__main__':
    app.run(port=5000)