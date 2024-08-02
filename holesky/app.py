from flask import request, Flask, jsonify
from werkzeug.utils import secure_filename

from service.core import query_data, start_store_data, finish_store_data, retrieve_data
from service.utils import allowed_file, download_file, parse_file, cleanup_file, convert_to_datetime#, filter_to_date

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
            "project_id": "0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1:QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", 
            "cid": "QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", 
            "start": "1514696400", 
            "end": "1703998800"
        }' http://127.0.0.1:5000/disperse | jq
    """
    data = request.get_json()
    if 'data' in data:
        data = data['data']
    print('disperse data:', data)
    project_id = data.get('project_id', '')
    if project_id == '':
        project_name = data.get('project_name', '')
        project_user = data.get('user', '')
        project_id = f'{project_user}:{project_name}'
    if isinstance(project_id, bytes):
        project_id = project_id.decode()
    print(f'project_id: {project_id}')
    if app.config["DEV"]:
        dispersal_request_id = '173342183bb06fa6fe2576b534b3f8c2156713f51c4e465fe9c1efcc86923dd7-313732323434313032323236303433383038372f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        head_cid = 'bafyreifuh56spzd6rpn3yldxcrfibcjducrjm7ikmbf62s6c3txfpm366m'
        result = {
            "result": {
                "dispersal_id": dispersal_request_id,
                "head_cid": head_cid
            }
        }
        return jsonify(result)
    else:
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
            # project_name = project_id[project_id.find(':')+1:]
            # print(f'project_name: {project_name}')
            dispersal_id = start_store_data(query_result)
            head_cid = query_result['agb']['head_cid']
            result = {
                "result": {
                    # "project_id": project_id,
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

        curl -H "Content-Type: application/json" -d '{"data": {"project_id": "0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1:QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb", "dispersal_id": "4ad3951235de48625212d999085284c13f3bc72070d7b891a68579e572bebe0f-313732323535313337343431323630333838312f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}}' http://127.0.0.1:5000/confirm | jq
    """
    data = request.get_json()
    if 'data' in data:
        data = data['data']
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

        curl -H "Content-Type: application/json" -d '{"project_id": "0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1:QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb"}' http://127.0.0.1:5000/retrieve | jq
        curl -H "Content-Type: application/json" -d '{"project_id": "0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1:QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLkXoSybb"}' http://127.0.0.1:6000/api/retrieve | jq

        curl -H "Content-Type: application/json" -d '{"project_id": "0x2b1a71a9C165F847198F257161D92EDEC54c58D2:Test"}' https://vercel-functions-test-wine.vercel.app/api/retrieve
        curl -H "Content-Type: application/json" -d '{"blob_index": "2437", "batch_header_hash": "0x9ffa72cd303db419944cbb5977dcc7d66ac58901fab9d8d27253b31f196269af"}' https://vercel-functions-test-wine.vercel.app/api/retrieve

        curl -H "Content-Type: application/json" -d '{"blob_index": "5176", "batch_header_hash": "c476ba5b428b95e1b3ca7fd00cea5be389d8f0332602a62d59d0725171ebc9a6"}' https://vercel-functions-test-wine.vercel.app/api/retrieve
    """
    # data = request.get_json()['data']
    data = request.get_json()
    if 'data' in data:
        data = data['data']
    # print(f'Retrieving data for project {data.get("project_id", "")}')
    # date = data.get('date', None)
    project_id = data.get('project_id', '852-holesky-QmNdW3jkAgGLsAzeqHcrMHAoeCq6YpZyQqnG4ZLk')
    if isinstance(project_id, bytes):
        print(f'project_id bytes: {project_id}')
        project_id = project_id.decode()
    result = retrieve_data(project_id)
    # if date is not None:
    #     result = filter_to_date(result, convert_to_datetime(date))
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