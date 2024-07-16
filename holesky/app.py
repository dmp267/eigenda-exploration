from flask import request, Flask, jsonify
from werkzeug.utils import secure_filename

from service.core import query_data, start_store_data, finish_store_data, retrieve_data
from service.utils import allowed_file, download_file, parse_file, cleanup_file, convert_to_datetime, filter_to_date

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data/uploads"
app.config["DEV"] = True
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
            "start": "2017-12-31", 
            "end": "2023-12-31"
        }' http://127.0.0.1:5000/disperse | jq
    """
    data = request.get_json()['data']
    print('disperse data:', data)
    if app.config["DEV"]:
        dispersal_request_id = 'def2c0c40f6379e8e956f30e10f0a033a643eddf7a4fa6e1ff4ff3eba819e1e8-313732313135363538313332363533353430312f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        head_cid = 'bafyreifuh56spzd6rpn3yldxcrfibcjducrjm7ikmbf62s6c3txfpm366m'
        result = {
            "result": {
                "dispersal_id": dispersal_request_id,
                "head_cid": head_cid
            }
        }
        return jsonify(result)
    else:
        project_id = data.get('project_id', '')
        if isinstance(project_id, bytes):
            print(f'project_id bytes: {project_id}')
            project_id = project_id.decode()
        cid = data.get('cid', 'QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb')
        ftype = data.get('ftype', 'kml')
        start = convert_to_datetime(data.get('start', '2010-01-01'))
        end = convert_to_datetime(data.get('end', '2023-12-31'))

        filename = secure_filename(f'{cid}.{ftype}')
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
            head_cid = query_result['agb']['head_cid']
            result = {
                "result": {
                    "dispersal_id": dispersal_id.decode(),
                    "head_cid": head_cid
                }
            }
            print(result)
            cleanup_file(file_path)
            return jsonify(result)
        except Exception as e:
            return jsonify({f'error: {str(e)}'}), 400


@app.route('/confirm', methods=['POST'])
def confirm():
    """ Stores the proof details on the blockchain after confirmation
        of dispersal on EigenDA network

        example request:

        curl -H "Content-Type: application/json" -d '{"project_id": "holesky-852-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", "dispersal_id": "173342183bb06fa6fe2576b534b3f8c2156713f51c4e465fe9c1efcc86923dd7-313732313037303634323832363139313739392f312f33332f302f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}' http://127.0.0.1:5000/confirm | jq
    """
    data = request.get_json()['data']
    print('confirm data:', data)
    project_id = data.get('project_id', '')
    if isinstance(project_id, bytes):
        print(f'project_id bytes: {project_id}')
        project_id = project_id.decode()
    # head_cid = data.get('head_cid', 'QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb')
    dispersal_id = data.get('dispersal_id', '')
    print(f'Confirming dispersal {dispersal_id} for project {project_id}')
    try:
        finish_store_data(project_id, dispersal_id)
        result = {
            "result": {
                "confirmed": True,
            }
        }
        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({"status": False, "error": str(e)}), 400


@app.route('/retrieve', methods=['POST'])
def retrieve():
    """ Retrieves data from data availability network 
    
        example request:

        curl -H "Content-Type: application/json" -d '{"project_id": "holesky-852-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb"}' http://127.0.0.1:5000/retrieve | jq
    """
    data = request.get_json()['data']
    print(f'Retrieving data for project {data.get("project_id", "")}')
    date = data.get('date', None)
    project_id = data.get('project_id', '852-holesky-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLk')
    if isinstance(project_id, bytes):
        print(f'project_id bytes: {project_id}')
        project_id = project_id.decode()
    result = retrieve_data(project_id)
    if date is not None:
        result = filter_to_date(result, convert_to_datetime(date))
    return jsonify({"result": result})
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 400


@app.route('/health', methods=['GET'])
def health():
    """ Health check for service """
    return jsonify("Healthy")


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    print('running!')