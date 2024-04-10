import grpc
import subprocess

from disperser.disperser_pb2 import DisperseBlobRequest, DisperseBlobResponse, GetBlobStatusRequest, GetBlobStatusResponse
from disperser.disperser_pb2_grpc import DisperserStub


def encode_data(data):
    result = subprocess.run(["tools/kzgpad/bin/kzgpad", "-e", data], capture_output=True, text=True)
    return result.stdout.strip()
    

def main(data):
    channel = grpc.secure_channel("disperser-holesky.eigenda.xyz:443", grpc.ssl_channel_credentials())
    stub = DisperserStub(channel)

    encoded_data = encode_data(data)   
    request = DisperseBlobRequest(data=encoded_data)

    response = stub.DisperseBlob(request)
    print(response)

    try:
        request = GetBlobStatusRequest(request_id=response.request_id)
        response = stub.GetBlobStatus(request)
        print(response)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main("hello world")