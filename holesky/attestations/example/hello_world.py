import time
import grpc

from protobufs.disperser.disperser_pb2 import DisperseBlobRequest, BlobStatusRequest, RetrieveBlobRequest
from protobufs.disperser.disperser_pb2_grpc import DisperserStub
from utils import decode_retrieval, encode_for_dispersal

# REQUEST_ID = b"957434148dfb72996233652510c80d0aaa257d8f3958acee0eb3b50b4ec43c3c-313731323737333839323439343139383234312f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# REQUEST_ID = b"6bd58d333d752fe4937659a990bd60c24f5bd76b05e4741f8259118ed7fbbff5-313731323835303830363037343239333034372f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
REQUEST_ID = b"80149141b656911db81389d184239a82edad4e70ce2e6c2e045afd96611b30f8-313731333338373039343937383835313931392f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def main(data: bytes, dev: bool = False):
    channel = grpc.secure_channel("disperser-holesky.eigenda.xyz:443", grpc.ssl_channel_credentials())
    stub = DisperserStub(channel)

    if not dev:
        encoded_data = encode_for_dispersal(data)   
        disperse_request = DisperseBlobRequest(data=encoded_data)

        disperse_response = stub.DisperseBlob(disperse_request)
        print(disperse_response)

    processing = True

    while processing:
        if dev:
            status_request = BlobStatusRequest(request_id=REQUEST_ID)
        else:
            status_request = BlobStatusRequest(request_id=disperse_response.request_id)
        status_response = stub.GetBlobStatus(status_request)
        print(f'status_response: {"CONFIRMED" if status_response == 2 else "PROCESSING"}')
        if status_response.status == 2: # CONFIRMED
            processing = False
            print(status_response)
            # write response to text file
            with open('hello_proof.txt', 'w') as f:
                f.write(str(status_response.info))
                f.close()
        else:
            print('sleeping')
            time.sleep(60)

    batch_header_hash = status_response.info.blob_verification_proof.batch_metadata.batch_header_hash
    blob_index = status_response.info.blob_verification_proof.blob_index

    retrieve_request = RetrieveBlobRequest(batch_header_hash=batch_header_hash, blob_index=blob_index)
    retrieve_response = stub.RetrieveBlob(retrieve_request)
    print(retrieve_response)

    stored_data = bytes(retrieve_response.data)
    result = decode_retrieval(stored_data)
    print(result)


if __name__ == "__main__":
    dev = False
    main(b"hello world", dev=dev)