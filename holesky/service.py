from datetime import datetime

from eigenda_utils import disperse_to_eigenda, retrieve_from_eigenda
from chain_utils import read_store_details, store_on_chain, verify_on_chain
from zarr_utils import get_dataset_bytes

CARBON_DATASETS = ["agb-quarterly", "deforestation-quarterly"]
dev = False
# dev_flag = "dev"
# dev_proof = "hello_proof.json"
dev_flag = "carbon-dataset-dev"
dev_proof = "carbon_dataset_proof.json"


def disperse_dataset(dataset_name: str, cid: str, data: bytes):
    """ Disperse the data to eigenda and store the result on chain
        If data is None, retrieve from IPFS

        Parameters
        ----------
        dataset_name : str
            The name of the dataset
        cid : str
            The CID of the head of the dataset
        data : bytes
            The data to store
    """
    if dev:
        import json
        result = json.load(open(f'attestations/{dev_proof}', 'r'))
        dataset_name = dev_flag
    else:
        result = disperse_to_eigenda(dataset_name, data)
    print(store_on_chain(dataset_name, cid, result))


def retrieve_dataset(dataset_name: str):
    """ Retrieve data from eigenda
    
        Parameters
        ----------
        dataset_name : str
            The name of the dataset

        Returns
        -------
        dict
            The data retrieved from eigenda
    """
    if dev:
        dataset_name = dev_flag
    storage_details = read_store_details(dataset_name)
    result = retrieve_from_eigenda(storage_details['batch_header_hash'], storage_details['blob_index'])
    return {
        "status": "success", 
        "time": datetime.now(), 
        "dataset": dataset_name,
        "data": result,
    }


def verify_dataset(dataset_name: str):
    """ Verify data on chain
    
        Parameters
        ----------
        dataset_name : str
            The name of the dataset
    """
    if dev:
        dataset_name = dev_flag
    print(verify_on_chain(dataset_name))

        
def update_dataset(datasets: list = CARBON_DATASETS, time_range_delta: int = 90):
    """ Update all datasets with most recent data
    
        Parameters
        ----------
        datasets : list
            The list of dataset names to update
        time_range_delta : int, optional
            The number of days to go back in time to get data, by default 30

        Returns
        -------
        dict
            The status of the update
    """
    for ds_name in datasets:
        head_cid, ds_bytes = get_dataset_bytes(ds_name, time_range_delta)
        disperse_dataset(ds_name, head_cid, ds_bytes)
        verify_dataset(ds_name)
    return {
        "status": "success", 
        "time": datetime.now(), 
        "time_range_delta": time_range_delta,
        "datasets": datasets,
    }
