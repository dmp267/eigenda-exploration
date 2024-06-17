import datetime
import json

from data.dclimate_zarr_client import geo_temporal_query
from data.parser import parse_kwargs
from storage.eigenda import disperse_to_eigenda, retrieve_from_eigenda
from verification.onchain import store_on_chain, read_store_details, verify_on_chain

# CONSTANTS
PROJECT_STORAGE = 'data/projects'
MOCK_STORAGE = 'storage/attestations/852-holesky-demo.json'


def allowed_file(filename):
    # KML files only
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'kml'


def parse_kml_file(file: str):
    kwargs = parse_kwargs(file)
    polygon_kwargs = kwargs['polygon_kwargs']
    spatial_agg_kwargs = kwargs['spatial_agg_kwargs']
    temporal_agg_kwargs = kwargs['temporal_agg_kwargs']
    return polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs


def query_polygon_carbon(polygon_kwargs: dict, spatial_agg_kwargs: dict, temporal_agg_kwargs: dict, start: datetime = None, end: datetime = None):
    if start is None or end is None:
        # TODO: placeholder, should be most recent that has data, so somewhere in 2023
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 2, 1)

    agb_head_cid, agb_agg_query = geo_temporal_query(
        dataset_name='agb-quarterly',
        polygon_kwargs=polygon_kwargs, 
        spatial_agg_kwargs=spatial_agg_kwargs,
        temporal_agg_kwargs=temporal_agg_kwargs,
        time_range=[start, end]
    )
    deforestation_head_cid, deforestation_agg_query = geo_temporal_query(
        dataset_name='deforestation-quarterly',
        polygon_kwargs=polygon_kwargs, 
        spatial_agg_kwargs=spatial_agg_kwargs,
        temporal_agg_kwargs=temporal_agg_kwargs,
        time_range=[start, end]
    )
    results = {
        'agb-head-cid': agb_head_cid,
        'agb': agb_agg_query,
        'deforestation-head-cid': deforestation_head_cid,
        'deforestation': deforestation_agg_query
    }
    return results


def store_data(project_name: str, cid: str, data: str, mock_storage: bool = False):
    if type(data) == dict:
        data = json.dumps(data)
    if type(data) == str:
        data = data.encode()
    if mock_storage:
        result = json.load(open(MOCK_STORAGE, 'r'))
    else:
        result = disperse_to_eigenda(project_name, data)
    print(f'Dispersal: {result}')
    receipt = store_on_chain(project_name, cid, result)
    print(f'On-chain storage receipt: {receipt}')
    verify_on_chain(project_name)
    return result


def retrieve_data(id: str):
    store_details = read_store_details(id)
    data = retrieve_from_eigenda(store_details['batch_header_hash'], store_details['blob_index'])
    return data