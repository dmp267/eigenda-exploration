# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from protobufs.disperser import disperser_pb2 as disperser_dot_disperser__pb2


class DisperserStub(object):
    """Disperser defines the public APIs for dispersing blobs.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.DisperseBlob = channel.unary_unary(
                '/disperser.Disperser/DisperseBlob',
                request_serializer=disperser_dot_disperser__pb2.DisperseBlobRequest.SerializeToString,
                response_deserializer=disperser_dot_disperser__pb2.DisperseBlobReply.FromString,
                )
        self.DisperseBlobAuthenticated = channel.stream_stream(
                '/disperser.Disperser/DisperseBlobAuthenticated',
                request_serializer=disperser_dot_disperser__pb2.AuthenticatedRequest.SerializeToString,
                response_deserializer=disperser_dot_disperser__pb2.AuthenticatedReply.FromString,
                )
        self.GetBlobStatus = channel.unary_unary(
                '/disperser.Disperser/GetBlobStatus',
                request_serializer=disperser_dot_disperser__pb2.BlobStatusRequest.SerializeToString,
                response_deserializer=disperser_dot_disperser__pb2.BlobStatusReply.FromString,
                )
        self.RetrieveBlob = channel.unary_unary(
                '/disperser.Disperser/RetrieveBlob',
                request_serializer=disperser_dot_disperser__pb2.RetrieveBlobRequest.SerializeToString,
                response_deserializer=disperser_dot_disperser__pb2.RetrieveBlobReply.FromString,
                )


class DisperserServicer(object):
    """Disperser defines the public APIs for dispersing blobs.
    """

    def DisperseBlob(self, request, context):
        """This API accepts blob to disperse from clients.
        This executes the dispersal async, i.e. it returns once the request
        is accepted. The client could use GetBlobStatus() API to poll the the
        processing status of the blob.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DisperseBlobAuthenticated(self, request_iterator, context):
        """DisperseBlobAuthenticated is similar to DisperseBlob, except that it requires the
        client to authenticate itself via the AuthenticationData message. The protoco is as follows:
        1. The client sends a DisperseBlobAuthenticated request with the DisperseBlobRequest message
        2. The Disperser sends back a BlobAuthHeader message containing information for the client to
        verify and sign.
        3. The client verifies the BlobAuthHeader and sends back the signed BlobAuthHeader in an
        	  AuthenticationData message.
        4. The Disperser verifies the signature and returns a DisperseBlobReply message.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetBlobStatus(self, request, context):
        """This API is meant to be polled for the blob status.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RetrieveBlob(self, request, context):
        """This retrieves the requested blob from the Disperser's backend.
        This is a more efficient way to retrieve blobs than directly retrieving
        from the DA Nodes (see detail about this approach in
        api/proto/retriever/retriever.proto).
        The blob should have been initially dispersed via this Disperser service
        for this API to work.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DisperserServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'DisperseBlob': grpc.unary_unary_rpc_method_handler(
                    servicer.DisperseBlob,
                    request_deserializer=disperser_dot_disperser__pb2.DisperseBlobRequest.FromString,
                    response_serializer=disperser_dot_disperser__pb2.DisperseBlobReply.SerializeToString,
            ),
            'DisperseBlobAuthenticated': grpc.stream_stream_rpc_method_handler(
                    servicer.DisperseBlobAuthenticated,
                    request_deserializer=disperser_dot_disperser__pb2.AuthenticatedRequest.FromString,
                    response_serializer=disperser_dot_disperser__pb2.AuthenticatedReply.SerializeToString,
            ),
            'GetBlobStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetBlobStatus,
                    request_deserializer=disperser_dot_disperser__pb2.BlobStatusRequest.FromString,
                    response_serializer=disperser_dot_disperser__pb2.BlobStatusReply.SerializeToString,
            ),
            'RetrieveBlob': grpc.unary_unary_rpc_method_handler(
                    servicer.RetrieveBlob,
                    request_deserializer=disperser_dot_disperser__pb2.RetrieveBlobRequest.FromString,
                    response_serializer=disperser_dot_disperser__pb2.RetrieveBlobReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'disperser.Disperser', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Disperser(object):
    """Disperser defines the public APIs for dispersing blobs.
    """

    @staticmethod
    def DisperseBlob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/disperser.Disperser/DisperseBlob',
            disperser_dot_disperser__pb2.DisperseBlobRequest.SerializeToString,
            disperser_dot_disperser__pb2.DisperseBlobReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DisperseBlobAuthenticated(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/disperser.Disperser/DisperseBlobAuthenticated',
            disperser_dot_disperser__pb2.AuthenticatedRequest.SerializeToString,
            disperser_dot_disperser__pb2.AuthenticatedReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetBlobStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/disperser.Disperser/GetBlobStatus',
            disperser_dot_disperser__pb2.BlobStatusRequest.SerializeToString,
            disperser_dot_disperser__pb2.BlobStatusReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RetrieveBlob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/disperser.Disperser/RetrieveBlob',
            disperser_dot_disperser__pb2.RetrieveBlobRequest.SerializeToString,
            disperser_dot_disperser__pb2.RetrieveBlobReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
