import json
import time
import grpc
import subprocess

from disperser.disperser_pb2 import DisperseBlobRequest, BlobStatusRequest, RetrieveBlobRequest
from disperser.disperser_pb2_grpc import DisperserStub
from pad_one_byte_codec import convert_by_padding_empty_byte, remove_empty_byte_from_padded_bytes

# REQUEST_ID = b"957434148dfb72996233652510c80d0aaa257d8f3958acee0eb3b50b4ec43c3c-313731323737333839323439343139383234312f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# BATCH_HEADER_HASH = b"\325%\242\255~\306\377j\367\005&\027\177\032c#\353\226\267\272\261C\367a\376XOz\225\220w\373"
# BLOB_INDEX = 150


def encode_data(data: bytes):
    result = subprocess.run(["../../../Layr-Labs/eigenda/tools/kzgpad/bin/kzgpad", "-e", data], capture_output=True, text=True).stdout.strip()
    result_bytes = bytes(result, "utf-8")
    valid_bytes = convert_by_padding_empty_byte(result_bytes)
    return valid_bytes


def decode_data(data: bytes):
    reconverted_data = remove_empty_byte_from_padded_bytes(data)
    reconverted_str = reconverted_data.decode("utf-8")
    result = subprocess.run(["../../../Layr-Labs/eigenda/tools/kzgpad/bin/kzgpad", "-d", "-"], input=reconverted_str, capture_output=True, text=True).stdout.strip()
    return result

def main(data: bytes):

    channel = grpc.secure_channel("disperser-holesky.eigenda.xyz:443", grpc.ssl_channel_credentials())
    stub = DisperserStub(channel)

    encoded_data = encode_data(data)   
    disperse_request = DisperseBlobRequest(data=encoded_data)

    disperse_response = stub.DisperseBlob(disperse_request)
    print(disperse_response)

    processing = True

    while processing:
        status_request = BlobStatusRequest(request_id=disperse_response.request_id)
        # status_request = BlobStatusRequest(request_id=REQUEST_ID)
        status_response = stub.GetBlobStatus(status_request)
        print(f'status_response: {"CONFIRMED" if status_response == 2 else "PROCESSING"}')
        if status_response.status == 2: # CONFIRMED
            processing = False
        else:
            print('sleeping')
            time.sleep(20)

    batch_header_hash = status_response.info.blob_verification_proof.batch_metadata.batch_header_hash
    blob_index = status_response.info.blob_verification_proof.blob_index
    # batch_header_hash = BATCH_HEADER_HASH
    # blob_index = BLOB_INDEX

    retrieve_request = RetrieveBlobRequest(batch_header_hash=batch_header_hash, blob_index=blob_index)
    retrieve_response = stub.RetrieveBlob(retrieve_request)
    print(retrieve_response)

    stored_data = bytes(retrieve_response.data)
    result = decode_data(stored_data)
    print(result)


if __name__ == "__main__":
    main(b"hello world")