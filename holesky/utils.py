import os
import time
import subprocess
import grpc
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


def pull_ipfs(cid: str):
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


def push_eigenda(data: bytes):
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
            # write response to text file
            result = str(status_response.info)
            with open('proof.txt', 'w') as f:
                f.write(result)
                f.close()
        else:
            print('sleeping')
            time.sleep(60)

    return result


def pull_eigenda(batch_header_hash: str, blob_index: int):
    retrieve_request = RetrieveBlobRequest(batch_header_hash=batch_header_hash, blob_index=blob_index)
    retrieve_response = stub.RetrieveBlob(retrieve_request)
    print(retrieve_response)

    stored_data = bytes(retrieve_response.data)
    result = decode_retrieval(stored_data)
    return result
    