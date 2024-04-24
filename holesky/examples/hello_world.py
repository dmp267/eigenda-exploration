import os
import sys
import time
import grpc
import json
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from protobufs.disperser.disperser_pb2 import DisperseBlobRequest, BlobStatusRequest, RetrieveBlobRequest
from protobufs.disperser.disperser_pb2_grpc import DisperserStub
from utils import decode_retrieval, encode_for_dispersal, transform_response

# REQUEST_ID = b"957434148dfb72996233652510c80d0aaa257d8f3958acee0eb3b50b4ec43c3c-313731323737333839323439343139383234312f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# REQUEST_ID = b"6bd58d333d752fe4937659a990bd60c24f5bd76b05e4741f8259118ed7fbbff5-313731323835303830363037343239333034372f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# REQUEST_ID = b"80149141b656911db81389d184239a82edad4e70ce2e6c2e045afd96611b30f8-313731333338373039343937383835313931392f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# REQUEST_ID = b"9337afb558a5d44d2bb22b9cb34dd2e9e02e848f768f947e26791045c8a6f908-313731333930363138343935373830333030382f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
# REQUEST_ID = b"e0bcabee67409aa522d7158be31a8f1fd82cc6644e20aa2e4353f06db7fc6284-313731333930393133303034323735333337392f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
REQUEST_ID = b"10b19f63c54527fa238af4bce0387b40990a6ff36acdbdd9b611895b99c2986d-313731333936383832393436393631303935392f302f33332f312f33332fe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


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
        else:
            print('sleeping')
            time.sleep(60)

    final_status = transform_response(status_response.info)
    json.dump(final_status, open('attestations/hello_proof.json', 'w'))

    batch_header_hash = status_response.info.blob_verification_proof.batch_metadata.batch_header_hash
    blob_index = status_response.info.blob_verification_proof.blob_index

    retrieve_request = RetrieveBlobRequest(batch_header_hash=batch_header_hash, blob_index=blob_index)
    retrieve_response = stub.RetrieveBlob(retrieve_request)
    print(retrieve_response)

    stored_data = bytes(retrieve_response.data)
    result = decode_retrieval(stored_data)
    print(result)


if __name__ == "__main__":
    dev = True
    main(b"Goodmorning America!", dev=dev)