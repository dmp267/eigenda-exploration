# import json
import grpc

from protobufs.disperser.disperser_pb2 import RetrieveBlobRequest
from protobufs.disperser.disperser_pb2_grpc import DisperserStub

# CONSTANTS
BYTES_PER_SYMBOL = 32
DISPERSER = "disperser-holesky.eigenda.xyz:443"

channel = grpc.secure_channel(DISPERSER, grpc.ssl_channel_credentials())
stub = DisperserStub(channel)


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
    result = reconverted_data.decode("utf-8")
    return result


def retrieve_from_eigenda(batch_header_hash: bytes, blob_index: int):
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


def retrieve_data(blob_index: int, batch_header_hash: bytes):
    data = retrieve_from_eigenda(batch_header_hash, blob_index)
    return data

    # print(f'data length: {len(data)}')
    # print(f'data type: {type(data)}')
    # json_data = json.loads(data)
    # print(f'json_data: {json_data}')
    # return json_data


# import os
# from datetime import datetime
# from web3 import Web3

# VERIFIER_CONTRACT_ADDRESS = os.environ.get('VERIFIER_CONTRACT_ADDRESS', '0x8032b4DBa3779B6836B4C69203bB1d3b4f92908B')
# RPC_URL = os.environ.get('RPC_URL', "https://ethereum-holesky-rpc.publicnode.com")
# ABI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'abi'))
# ABI = json.load(open(f'{ABI_DIR}/ProjectStorageVerifier.json'))['abi']

# web3 = Web3(Web3.HTTPProvider(RPC_URL))
# chainId = web3.eth.chain_id


# def read_store_details(project_id: str):
#     """
#     Read the storage details of a carbon monitoring/management project from the smart contract.

#     Parameters:
#         project_id (str): The name of the project.

#     Returns:
#         dict: The storage details of the project.
#     """
#     contract = web3.eth.contract(address=VERIFIER_CONTRACT_ADDRESS, abi=ABI)
#     full_detail = contract.functions.readProjectStorageProof(project_id).call()
#     storage_detail = full_detail[1]
#     result = {
#         "last_updated_timestamp": datetime.fromtimestamp(int(storage_detail[0])),
#         "blob_index": int(storage_detail[2][1]), 
#         "batch_header_hash": storage_detail[1][2]
#     }
#     # print(f'storage_detail: {result}')
#     return result


# def verify_on_chain(project_id: str):
#     """
#     Verify the storage details of a carbon monitoring/management project on the smart contract.

#     Parameters:
#         project_id (str): The name of the project.

#     Returns:
#         bool: The verification status of the project.
#     """
#     contract = web3.eth.contract(address=VERIFIER_CONTRACT_ADDRESS, abi=ABI)
#     verification = contract.functions.verifyProjectStorageProof(project_id).call()
#     return verification


# def retrieve_data_2(id: str):
#     """
#     Retrieve data from EigenDA.

#     Parameters:
#         project_id (str): The name of the project.

#     Returns:
#         dict: The retrieved data.
#     """
#     verify_on_chain(id)
#     store_details = read_store_details(id)
#     data = retrieve_from_eigenda(store_details['batch_header_hash'], store_details['blob_index'])
#     print(f'data length: {len(data)}')
#     print(f'data type: {type(data)}')
#     # print(f'json_data: {json_data}')
#     return data