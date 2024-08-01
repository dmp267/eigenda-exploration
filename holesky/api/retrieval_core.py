import json
import os
import subprocess
import grpc
from datetime import datetime
from web3 import Web3

from protobufs.disperser.disperser_pb2 import RetrieveBlobRequest
from protobufs.disperser.disperser_pb2_grpc import DisperserStub

# CONSTANTS
BYTES_PER_SYMBOL = 32
DISPERSER = "disperser-holesky.eigenda.xyz:443"

VERIFIER_CONTRACT_ADDRESS = os.environ.get('VERIFIER_CONTRACT_ADDRESS', '0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B')
RPC_URL = os.environ.get('RPC_URL', "https://ethereum-holesky-rpc.publicnode.com")
ABI = json.load(open('abi/ProjectStorageVerifier.sol/ProjectStorageVerifier.json'))['abi']

channel = grpc.secure_channel(DISPERSER, grpc.ssl_channel_credentials())
stub = DisperserStub(channel)

web3 = Web3(Web3.HTTPProvider(RPC_URL))
chainId = web3.eth.chain_id


def remove_empty_byte_from_padded_bytes(data):
    """
    Remove the first byte from every 32 bytes, reversing the change made by convert_by_padding_empty_byte.
    
    Parameters:
        data (bytes): The data to convert.

    Returns:
        bytes: The converted data.
    """
    parse_size = BYTES_PER_SYMBOL
    data_size = len(data)
    data_len = (data_size + parse_size - 1) // parse_size
    
    put_size = BYTES_PER_SYMBOL - 1
    valid_data = bytearray(data_len * put_size)
    valid_len = len(valid_data)
    
    for i in range(data_len):
        start = i * parse_size + 1
        end = (i + 1) * parse_size
        if end > data_size:
            end = data_size
            valid_len = end - start + i * put_size
        valid_data[i * put_size: (i + 1) * put_size] = data[start: end]
    return bytes(valid_data[: valid_len])


def find_kzgpad():
    """
    Find the path to the kzgpad binary.

    Returns:
        str: The path to the kzgpad binary.
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    parent = os.path.dirname(repo_root)
    grandparent = os.path.dirname(parent)
    if 'eigenda' in os.listdir(parent):
        path = os.path.join(parent, 'eigenda/tools/kzgpad/bin/kzgpad')
    else:
        path = os.path.join(grandparent, 'Layr-Labs/eigenda/tools/kzgpad/bin/kzgpad')
    return path


def decode_retrieval(data: bytes):
    """
    Decode data retrieved from EigenDA.
    See here for details: https://docs.eigenlayer.xyz/eigenda/rollup-guides/blob-encoding.
    This reverts the encoding done by encode_for_dispersal.

    Parameters:
        data (bytes): The data to decode.

    Returns:
        str: The decoded data.
    """
    reconverted_data = remove_empty_byte_from_padded_bytes(data)
    reconverted_str = reconverted_data.decode("utf-8")
    path = find_kzgpad()
    result = subprocess.run([path, "-d", "-"], input=reconverted_str, capture_output=True, text=True).stdout.strip()
    return result


def retrieve_from_eigenda(batch_header_hash: str, blob_index: int):
    """
    Retrieve data from EigenDA.

    Parameters:
        batch_header_hash (str): The batch header hash.
        blob_index (int): The blob index.

    Returns:
        str: The retrieved data.
    """
    retrieve_request = RetrieveBlobRequest(batch_header_hash=batch_header_hash, blob_index=blob_index)
    retrieve_response = stub.RetrieveBlob(retrieve_request)
    stored_data = bytes(retrieve_response.data)
    result = decode_retrieval(stored_data)
    return result


def read_store_details(project_id: str):
    """
    Read the storage details of a carbon monitoring/management project from the smart contract.

    Parameters:
        project_id (str): The name of the project.

    Returns:
        dict: The storage details of the project.
    """
    contract = web3.eth.contract(address=VERIFIER_CONTRACT_ADDRESS, abi=ABI)
    full_detail = contract.functions.readProjectStorageProof(project_id).call()
    storage_detail = full_detail[1]
    result = {
        "last_updated_timestamp": datetime.fromtimestamp(int(storage_detail[0])),
        "blob_index": int(storage_detail[2][1]), 
        "batch_header_hash": storage_detail[1][2]
    }
    print(result)
    return result


def verify_on_chain(project_id: str):
    """
    Verify the storage details of a carbon monitoring/management project on the smart contract.

    Parameters:
        project_id (str): The name of the project.

    Returns:
        bool: The verification status of the project.
    """
    contract = web3.eth.contract(address=VERIFIER_CONTRACT_ADDRESS, abi=ABI)
    verification = contract.functions.verifyProjectStorageProof(project_id).call()
    print(f'Verification for {project_id} complete')
    return verification


def retrieve_data(id: str, date: datetime = None):
    verify_on_chain(id)
    store_details = read_store_details(id)
    data = retrieve_from_eigenda(store_details['batch_header_hash'], store_details['blob_index'])
    return json.loads(data)