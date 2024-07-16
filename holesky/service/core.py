import json
import math
from datetime import datetime

from data.dclimate_zarr_client import geo_temporal_query
from storage.eigenda import disperse_to_eigenda, confirm_dispersal, retrieve_from_eigenda
from verification.onchain import store_on_chain, read_store_details, verify_on_chain

# CONSTANTS
FLOAT_MULTIPLIER = 1e18
SEQUESTRATION_RATIO = 0.47
PROJECT_STORAGE = 'data/projects'

# DEFAULTS
MOCK_STORAGE = 'storage/attestations/holesky-852.json'


def format_float(n):
    # truncate to 3 decimals and add commas
    return "{:,}".format(round(n, 3))


def format_power(n):
    exponent = int(math.log10(n))
    return f"10^{exponent}"


def string_to_timestamp(time):
    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S").timestamp()


def get_most_recent_data(polygon_kwargs: dict, spatial_agg_kwargs: dict, temporal_agg_kwargs: dict):
    missing_data = True
    current_year = datetime.now().year
    current_month = datetime.now().month
    # 1 - 4 - 7 - 10
    latest_potential_update = current_month - ((current_month - 1) % 3)
    start = datetime(current_year, latest_potential_update, 1)
    end = datetime(current_year, latest_potential_update, 2)
    while missing_data:
        print(f'requesting data for {start} to {end}')
        try:
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
            missing_data = False
        except Exception as e:
            print(f'Error: {str(e)}')
            carry_over = start.month - 3 < 1
            new_year = start.year - carry_over
            new_month = start.month - 3 + (12 * carry_over)

            start = start.replace(year=new_year, month=new_month)
            end = end.replace(year=new_year, month=new_month)
            continue
    return agb_head_cid, agb_agg_query, deforestation_head_cid, deforestation_agg_query


def query_data(polygon_kwargs: dict, spatial_agg_kwargs: dict, temporal_agg_kwargs: dict, start: datetime = None, end: datetime = None):
    if start is None or end is None:
        agb_head_cid, agb_agg_query, deforestation_head_cid, deforestation_agg_query = get_most_recent_data(polygon_kwargs, spatial_agg_kwargs, temporal_agg_kwargs)
    else:
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
        "summary": f'Above ground biomass measured at {format_float(agb_agg_query["data"][0])} {agb_agg_query["unit of measurement"]}, deforestation measured at {format_float(deforestation_agg_query["data"][0])} {deforestation_agg_query["unit of measurement"]}, and carbon sequestration measured at {format_float(agb_agg_query["data"][0] * SEQUESTRATION_RATIO)} {agb_agg_query["unit of measurement"]} as of {agb_agg_query["times"][0]}.',
        "timestamps_ms": [int(string_to_timestamp(agb_agg_query['times'][i]) * 1e3) for i in range(len(agb_agg_query['data']))],
        "agb": {
            "data": [int(agb_agg_query['data'][i] * FLOAT_MULTIPLIER) for i in range(len(agb_agg_query['data']))],
            "unit": f"{agb_agg_query['unit of measurement']} / {format_power(int(FLOAT_MULTIPLIER))}",
            "head_cid": agb_head_cid,
        },
        "deforestation": {
            # "timestamps_ms": [int(string_to_timestamp(deforestation_agg_query['times'][i]) * 1e3) for i in range(len(deforestation_agg_query['data']))],
            "data": [int(deforestation_agg_query['data'][i] * FLOAT_MULTIPLIER) for i in range(len(deforestation_agg_query['data']))],
            # "timestamps_ms": int(string_to_timestamp(deforestation_agg_query['times'][0]) * 1e3),
            # "data": int(deforestation_agg_query['data'][0] * FLOAT_MULTIPLIER),
            "unit": f"{deforestation_agg_query['unit of measurement']} / {format_power(int(FLOAT_MULTIPLIER))}",
            "head_cid": deforestation_head_cid,
        },
        "sequestration": {
            "data": [int(agb_agg_query['data'][i] * FLOAT_MULTIPLIER * SEQUESTRATION_RATIO) for i in range(len(agb_agg_query['data']))],
            # "data": int(agb_agg_query['data'][0] * FLOAT_MULTIPLIER * SEQUESTRATION_RATIO),
            "unit": f"{agb_agg_query['unit of measurement']} / {format_power(int(FLOAT_MULTIPLIER))}"
        },
    }
    print(f'data: {results}')
    return results


def start_store_data(data: str):
    if type(data) == dict:
        data = json.dumps(data)
    if type(data) == str:
        data = data.encode()
    # if mock_storage:
    #     result = json.load(open(MOCK_STORAGE, 'r'))
    #     receipt = {
    #         "blockHash": "dd674a79977aafc3327a819997f200da2653f6638c9d42ef1f5649536174acc0",
    #         "blockNumber": 1756196,
    #         "contractAddress": "null", 
    #         "cumulativeGasUsed": 3738884, 
    #         "effectiveGasPrice": 1148047598, 
    #         "from": "0x9a15e32290A9C2C01f7C8740B4484024aC92F2a1", 
    #         "gasUsed": 949334, 
    #         "logs": [], 
    #         "logsBloom": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 
    #         "status": 1, 
    #         "to": "0x434a156aA863c66FAd723a7e3fb68C317DF5f0b7", 
    #         "transactionHash": "17e1c4dcbf9b9774f9e183423c8fa2d2940e6277e0bb6dcc9d3c4cb2bba1e953", 
    #         "transactionIndex": 21, 
    #         "type": 2
    #     }
    result = disperse_to_eigenda(data)
    print(f'Dispersal: {result}')
    return result


def finish_store_data(project_id: str, dispersal_id: str):
    result = confirm_dispersal(dispersal_id)
    print(f'Confirmation: {result}')
    receipt = store_on_chain(project_id, result)
    verify_on_chain(project_id)
    print(f'On-chain storage receipt: {receipt}')


def retrieve_data(id: str, date: datetime = None):
    verify_on_chain(id)
    store_details = read_store_details(id)
    data = retrieve_from_eigenda(store_details['batch_header_hash'], store_details['blob_index'])
    return json.loads(data)