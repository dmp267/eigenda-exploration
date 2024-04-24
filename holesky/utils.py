import os
import time
import subprocess
import grpc
import json
import ipfshttpclient, multiaddr

from protobufs.disperser.disperser_pb2 import DisperseBlobRequest, BlobStatusRequest, RetrieveBlobRequest
from protobufs.disperser.disperser_pb2_grpc import DisperserStub


BYTES_PER_SYMBOL = 32
HOST = "0.0.0.0"
PORT = 5001
DISPERSER = "disperser-holesky.eigenda.xyz:443"

channel = grpc.secure_channel(DISPERSER, grpc.ssl_channel_credentials())
stub = DisperserStub(channel)
daemon = multiaddr.Multiaddr(f'/dns4/{HOST}/tcp/{PORT}/http')
client = ipfshttpclient.connect(daemon, timeout=None, session=True)


def retrieve_from_ipfs(cid: str):
    try:
        data = client.cat(cid)
        return data
    except Exception as e:
        print(f'error pulling ipfs cid {cid}: {e}')
        raise e


# helper functions for guaranteeing the validity of the data to be dispersed to EigenDA
# converted from go example at https://docs.eigenlayer.xyz/eigenda/rollup-guides/blob-encoding
def convert_by_padding_empty_byte(data):
    """
    Convert data by padding an empty byte at the front of every 31 bytes.
    This ensures every 32 bytes are within the valid range of a field element for bn254 curve.
    """
    parse_size = BYTES_PER_SYMBOL - 1
    data_size = len(data)
    data_len = (data_size + parse_size - 1) // parse_size
    
    valid_data = bytearray(data_len * BYTES_PER_SYMBOL)
    valid_end = len(valid_data)
    
    for i in range(data_len):
        start = i * parse_size
        end = (i + 1) * parse_size
        if end > data_size:
            end = data_size
            valid_end = end - start + 1 + i * BYTES_PER_SYMBOL
        
        # With big endian, setting the first byte to 0 ensures data is within the valid range
        valid_data[i * BYTES_PER_SYMBOL] = 0
        valid_data[i * BYTES_PER_SYMBOL + 1: (i + 1) * BYTES_PER_SYMBOL] = data[start: end]
    
    return bytes(valid_data[: valid_end])


def remove_empty_byte_from_padded_bytes(data):
    """
    Remove the first byte from every 32 bytes, reversing the change made by convert_by_padding_empty_byte.
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
    repo_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    parent = os.path.dirname(repo_root)
    grandparent = os.path.dirname(parent)
    if 'eigenda' in os.listdir(parent):
        path = os.path.join(parent, 'eigenda/tools/kzgpad/bin/kzgpad')
    else:
        path = os.path.join(grandparent, 'Layr-Labs/eigenda/tools/kzgpad/bin/kzgpad')
    return path


def encode_for_dispersal(data: bytes):
    path = find_kzgpad()
    result = subprocess.run([path, "-e", data], capture_output=True, text=True).stdout.strip()
    result_bytes = bytes(result, "utf-8")
    valid_bytes = convert_by_padding_empty_byte(result_bytes)
    return valid_bytes


def decode_retrieval(data: bytes):
    reconverted_data = remove_empty_byte_from_padded_bytes(data)
    reconverted_str = reconverted_data.decode("utf-8")
    path = find_kzgpad()
    result = subprocess.run([path, "-d", "-"], input=reconverted_str, capture_output=True, text=True).stdout.strip()
    return result
    

def transform_response(info):
    if len(info.blob_header.blob_quorum_params) > 1:
        blob_quorum_params = []
        for params in info.blob_header.blob_quorum_params:
            adversary_threshold_percentage = int(params.adversary_threshold_percentage)
            confirmation_threshold_percentage = int(params.confirmation_threshold_percentage)
            chunk_length = int(params.chunk_length)
            if hasattr(params, 'quorum_number'):
                quorum_number = int(params.quorum_number)
            else:
                quorum_number = 0
            bqp = {"quorum_number": quorum_number,
                   "adversary_threshold_percentage": adversary_threshold_percentage, 
                   "confirmation_threshold_percentage": confirmation_threshold_percentage, 
                   "chunk_length": chunk_length}
            blob_quorum_params.append(bqp)
    else:
        if type(info.blob_verification_proof.blob_quorum_params) != list:
            blob_quorum_params = [info.blob_verification_proof.blob_quorum_params]
        else:
            blob_quorum_params = info.blob_verification_proof.blob_quorum_params
    proof_details = {
        "blob_header": {
            "commitment": {
                "x": int.from_bytes(info.blob_header.commitment.x, "big"),
                "y": int.from_bytes(info.blob_header.commitment.y, "big"),
            },
            "data_length": int(info.blob_header.data_length),
            "blob_quorum_params": blob_quorum_params,
        },
        "blob_verification_proof": {
            "batch_id": info.blob_verification_proof.batch_id,
            "blob_index": info.blob_verification_proof.blob_index,
            "batch_metadata": {
                "batch_header": {
                    "batch_root": info.blob_verification_proof.batch_metadata.batch_header.batch_root.hex(),
                    "quorum_numbers": info.blob_verification_proof.batch_metadata.batch_header.quorum_numbers.hex(),
                    "quorum_signed_percentages": info.blob_verification_proof.batch_metadata.batch_header.quorum_signed_percentages.hex(),
                    "reference_block_number": int(info.blob_verification_proof.batch_metadata.batch_header.reference_block_number),
                },
                "signatory_record_hash": info.blob_verification_proof.batch_metadata.signatory_record_hash.hex(),
                "fee": info.blob_verification_proof.batch_metadata.fee.hex(),
                "confirmation_block_number": int(info.blob_verification_proof.batch_metadata.confirmation_block_number),
                "batch_header_hash": info.blob_verification_proof.batch_metadata.batch_header_hash.hex()
            },
            "inclusion_proof": info.blob_verification_proof.inclusion_proof.hex(),
            "quorum_indexes": info.blob_verification_proof.quorum_indexes.hex(),
        }
    }
    return proof_details


def disperse_to_eigenda(cid: str, data: bytes):
    encoded_data = encode_for_dispersal(data)   
    disperse_request = DisperseBlobRequest(data=encoded_data)

    disperse_response = stub.DisperseBlob(disperse_request)
    print(disperse_response)

    processing = True
    result = ''
    while processing:
        status_request = BlobStatusRequest(request_id=disperse_response.request_id)
        status_response = stub.GetBlobStatus(status_request)
        print(f'status_response: {"CONFIRMED" if status_response == 2 else "PROCESSING"}')
        if status_response.status == 2: # CONFIRMED
            processing = False
            print(status_response)
            result = transform_response(status_response.info)
            json.dump(result, open(f'attestations/{cid}.json', 'w'))
        else:
            print('sleeping')
            time.sleep(60)

    return result


def retrieve_from_eigenda(batch_header_hash: str, blob_index: int):
    retrieve_request = RetrieveBlobRequest(batch_header_hash=batch_header_hash, blob_index=blob_index)
    retrieve_response = stub.RetrieveBlob(retrieve_request)
    print(retrieve_response)

    stored_data = bytes(retrieve_response.data)
    result = decode_retrieval(stored_data)
    return result