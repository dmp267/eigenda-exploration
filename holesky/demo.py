import datetime
import json

from data.dclimate_zarr_client import geo_temporal_query
from data.parser import parse_kwargs
from storage.eigenda import disperse_to_eigenda, retrieve_from_eigenda
from verification.onchain import store_on_chain, read_store_details, verify_on_chain

# CONSTANTS
START = datetime.datetime(2021, 12, 31)
END = datetime.datetime(2024, 1, 1)
FILENAME = "data/shapefiles/852.kml"
PROJECT_NAME = "852-holesky"


def get_query_args(file: str):
    kwargs = parse_kwargs(file)
    polygon_kwargs = kwargs["polygon_kwargs"]
    spatial_agg_kwargs = kwargs["spatial_agg_kwargs"]
    temporal_agg_kwargs = kwargs["temporal_agg_kwargs"]
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


def store_data(project_name: str, cid: str, data: str):
    if not type(data) == bytes:
        data = data.encode()
    result = disperse_to_eigenda(project_name, data, "storage/attestations/852-holesky.json")
    print(f'Storage: {result}')
    receipt = store_on_chain(project_name, cid, result)
    return receipt


def retrieve_data(id: str):
    print(verify_on_chain(id))
    store_details = read_store_details(id)
    data = retrieve_from_eigenda(store_details['batch_header_hash'], store_details['blob_index'])
    return data


if __name__ == "__main__":
    polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs = get_query_args(FILENAME)

    agb_head_cid, agb_agg_query = query("agb-quarterly", polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs, START, END)
    print(f'AGB head CID: {agb_head_cid}')

    deforestation_head_cid, deforestation_agg_query = query("deforestation-quarterly", polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs, START, END)
    print(f'Deforestation head CID: {deforestation_head_cid}')

    results = {
        'agb': agb_agg_query,
        'deforestation': deforestation_agg_query
    }
    print(f'Results: {results}')

    data_to_store = json.dumps(results).encode()
    print(f'Data to store: {data_to_store}')
    
    # receipt = store_data(f'{PROJECT_NAME}', agb_head_cid, data_to_store)
    # print(f'Storage receipt: {receipt}')
    
    # data = retrieve_data(f'{PROJECT_NAME}')
    # print(f'Retrieved data: {json.loads(data.decode())}')