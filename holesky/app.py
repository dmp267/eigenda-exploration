from datetime import datetime
from flask import request, Flask, jsonify
from werkzeug.utils import secure_filename

from service.core import parse_kml_file, query_polygon_carbon, store_data, retrieve_data, allowed_file, PROJECT_STORAGE

# CONSTANTS
FLOAT_MULTIPLIER = 1e3
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data/uploads"

error_response = {
    "status": "",
    "agb": {
        "time": 0,
        "data": 0,
        "unit": "",
        "head_cid": ""
    },
    "deforestation": {
        "time": 0,
        "data": 0,
        "unit": "",
        "head_cid": ""
    }
}


@app.route('/demo', methods=['POST'])
def demo():
    """ Accepts and parses KML upload for polygon boundaries and queries 
        and aggregates the most recent carbon data for the specified area 

        example request:

        curl -X POST -H "Content-Type: application/json" -d '{"filename": "852.kml"}' http://127.0.0.1:5000/store
    """
    data = request.get_json()
    print('running chainlink demo query')
    filename = secure_filename(data.get('filename', '852.kml'))
    file = f'{PROJECT_STORAGE}/{filename}'
    if file and allowed_file(filename):
        try:
            polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs = parse_kml_file(file)
            results = query_polygon_carbon(polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs)
        except Exception as e:
            error_response['status'] = f'error: {str(e)}'
            return jsonify(error_response), 400

        output = {
            # string status
            "status": "success",
            "agb": {
                # uint timestamp
                "time": int(datetime.strptime(results['agb']['times'][0], "%Y-%m-%dT%H:%M:%S").timestamp() * FLOAT_MULTIPLIER),
                # uint agg data
                "data": int(results['agb']['data'][0] * FLOAT_MULTIPLIER),
                # string unit
                "unit": results['agb']['unit of measurement'],
                # string head_cid
                "head_cid": results['agb-head-cid']
            },
            "deforestation": {
                # uint timestamp
                "time": int(datetime.strptime(results['deforestation']['times'][0], "%Y-%m-%dT%H:%M:%S").timestamp() * FLOAT_MULTIPLIER),
                # uint agg data
                "data": int(results['deforestation']['data'][0] * FLOAT_MULTIPLIER),
                # string unit
                "unit": results['deforestation']['unit of measurement'],
                # string head_cid
                "head_cid": results['deforestation-head-cid'],
            }
        }
        return jsonify(output)
    error_response['status'] = 'error: Invalid file type'
    return jsonify(error_response), 400


@app.route('/query', methods=['POST'])
def query():
    """ Accepts and parses KML upload for polygon boundaries and queries 
        and aggregates the most recent carbon data for the specified area 

        example request:

        curl -X POST -F "file=@data/projects/852.kml" http://127.0.0.1:5000/query
    """
    if 'file' not in request.files:
        error_response['status'] = 'error: No file provided'
        return jsonify(error_response), 400
    file = request.files['file']
    if file.filename == '':
        error_response['status'] = 'error: No filename'
        return jsonify(error_response), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = f'{app.config["UPLOAD_FOLDER"]}/{filename}'
        file.save(file_path)
        try:
            polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs = parse_kml_file(file_path)
            results = query_polygon_carbon(polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs)

            output = {
                # string status
                "status": "success",
                "agb": {
                    # uint timestamp in ms
                    "timestamp_ms": int(datetime.strptime(results['agb']['times'][0], "%Y-%m-%dT%H:%M:%S").timestamp() * FLOAT_MULTIPLIER),
                    # uint agg data
                    "data": int(results['agb']['data'][0] * FLOAT_MULTIPLIER),
                    # string unit
                    "unit": f"{results['agb']['unit of measurement']} / 1000",
                    # string head_cid
                    "head_cid": results['agb-head-cid']
                },
                "deforestation": {
                    # uint timestamp
                    "timestamp (ms)": int(datetime.strptime(results['deforestation']['times'][0], "%Y-%m-%dT%H:%M:%S").timestamp() * FLOAT_MULTIPLIER),
                    # uint agg data
                    "data": int(results['deforestation']['data'][0] * FLOAT_MULTIPLIER),
                    # string unit
                    "unit": f"{results['deforestation']['unit of measurement']} / 1000",
                    # string head_cid
                    "head_cid": results['deforestation-head-cid'],
                }
            }
            return jsonify(output)
        except Exception as e:
            error_response['status'] = f'error: {str(e)}'
            return jsonify(error_response), 400
        
    error_response['status'] = 'error: Invalid file type'
    return jsonify(error_response), 400


@app.route('/store', methods=['POST'])
def store():
    """ Stores receieved data on the data availability network 
        and stores the proof details on the blockchain

        example request:

        curl -X POST -H "Content-Type: application/json" -d '{"project_name": "project-852-holesky", "cid": "bafyreifuh56spzd6rpn3yldxcrfibcjducrjm7ikmbf62s6c3txfpm366m", "data": {"agb":{"data":638312500,"head_cid":"bafyreifuh56spzd6rpn3yldxcrfibcjducrjm7ikmbf62s6c3txfpm366m","timestamp_ms":1672549200000,"unit":"tonne/hectare / 1000"},"deforestation":{"data":9926329,"head_cid":"bafyreicv7xwwcz4qdo3lz4okefdplq47b5mcs32oiragaxbchtjwya57je","timestamp (ms)":1672549200000,"unit":"decameter**2/hectare / 1000"},"status":"success"}}' http://127.0.0.1:5000/store
    """
    data = request.get_json()
    # mock data availability storage for demo because of finalization delay
    result = store_data(data['project_name'], data['cid'], data['data'], mock_storage=True)
    return jsonify(result)


@app.route('/retrieve/<project_name>', methods=['GET'])
def retrieve(project_name: str):
    """ Retrieves data from data availability network 
    
        example request:

        curl -X GET http://127.0.0.1:5000/retrieve/project-852-holesky
    """
    result = retrieve_data(project_name)
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health():
    """ Health check for service """
    return jsonify("Healthy")


if __name__ == '__main__':
    app.run(port=5000)