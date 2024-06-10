import datetime
import json

from data.dclimate_zarr_client import geo_temporal_query
from data.parser import parse_kwargs
from storage.eigenda import disperse_to_eigenda, retrieve_from_eigenda
from verification.onchain import store_on_chain, read_store_details, verify_on_chain

# CONSTANTS
PROJECTS = 'data/projects'
# PARAMS
START = datetime.datetime(2023, 1, 1)
END = datetime.datetime(2023, 2, 1)
FILE = '852.kml'


def get_query_args(file: str):
    kwargs = parse_kwargs(file)
    polygon_kwargs = kwargs['polygon_kwargs']
    spatial_agg_kwargs = kwargs['spatial_agg_kwargs']
    temporal_agg_kwargs = kwargs['temporal_agg_kwargs']
    return polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs


def query(dataset_name: str, polygon_kwargs: dict, spatial_agg_kwargs: dict, temporal_agg_kwargs: dict, start: datetime, end: datetime):
    head_cid, agg_query = geo_temporal_query(
        dataset_name=dataset_name,
        polygon_kwargs=polygon_kwargs, 
        spatial_agg_kwargs=spatial_agg_kwargs,
        temporal_agg_kwargs=temporal_agg_kwargs,
        time_range=[start, end]
    )
    return head_cid, agg_query


def store_data(project_name: str, cid: str, data: str, checkpoint: str = ''):
    if not type(data) == bytes:
        data = data.encode()
    if checkpoint:
        result = json.load(open(checkpoint, 'r'))
    else:
        result = disperse_to_eigenda(project_name, data)
    print(f'Storage: {result}')
    receipt = store_on_chain(project_name, cid, result)
    return receipt


def retrieve_data(id: str):
    verify_on_chain(id)
    store_details = read_store_details(id)
    data = retrieve_from_eigenda(store_details['batch_header_hash'], store_details['blob_index'])
    return data


if __name__ == '__main__':
    polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs = get_query_args(f'{PROJECTS}/{FILE}')

    agb_head_cid, agb_agg_query = query("agb-quarterly", polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs, START, END)
    deforestation_head_cid, deforestation_agg_query = query("deforestation-quarterly", polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs, START, END)
    print(f'AGB head CID: {agb_head_cid}')
    print(f'Deforestation head CID: {deforestation_head_cid}')

    results = {
        'agb': agb_agg_query,
        'deforestation': deforestation_agg_query
    }
    print(f'Results: {results}')
    data_to_store = json.dumps(results).encode()

    project_name = f'{FILE.split(".")[0]}-holesky-demo'
    checkpoint = f'storage/attestations/{project_name}.json'

    # receipt = store_data(f'{project_name}', agb_head_cid, data_to_store, checkpoint)
    receipt = store_data(f'{project_name}', agb_head_cid, data_to_store)
    print(f'Storage receipt: {receipt}')
    
    data = retrieve_data(f'{project_name}')
    print(f'Retrieved data: {json.loads(data)}')