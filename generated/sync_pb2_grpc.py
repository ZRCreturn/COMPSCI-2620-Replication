# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import generated.sync_pb2 as sync__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in sync_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class DataSyncStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.FullSync = channel.unary_unary(
                '/DataSync/FullSync',
                request_serializer=sync__pb2.DataPackage.SerializeToString,
                response_deserializer=sync__pb2.SyncResponse.FromString,
                _registered_method=True)
        self.IncrementalSync = channel.unary_unary(
                '/DataSync/IncrementalSync',
                request_serializer=sync__pb2.DataPackage.SerializeToString,
                response_deserializer=sync__pb2.SyncResponse.FromString,
                _registered_method=True)
        self.GetFullData = channel.unary_unary(
                '/DataSync/GetFullData',
                request_serializer=sync__pb2.Empty.SerializeToString,
                response_deserializer=sync__pb2.DataPackage.FromString,
                _registered_method=True)


class DataSyncServicer(object):
    """Missing associated documentation comment in .proto file."""

    def FullSync(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IncrementalSync(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFullData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DataSyncServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FullSync': grpc.unary_unary_rpc_method_handler(
                    servicer.FullSync,
                    request_deserializer=sync__pb2.DataPackage.FromString,
                    response_serializer=sync__pb2.SyncResponse.SerializeToString,
            ),
            'IncrementalSync': grpc.unary_unary_rpc_method_handler(
                    servicer.IncrementalSync,
                    request_deserializer=sync__pb2.DataPackage.FromString,
                    response_serializer=sync__pb2.SyncResponse.SerializeToString,
            ),
            'GetFullData': grpc.unary_unary_rpc_method_handler(
                    servicer.GetFullData,
                    request_deserializer=sync__pb2.Empty.FromString,
                    response_serializer=sync__pb2.DataPackage.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'DataSync', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('DataSync', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class DataSync(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def FullSync(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DataSync/FullSync',
            sync__pb2.DataPackage.SerializeToString,
            sync__pb2.SyncResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def IncrementalSync(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DataSync/IncrementalSync',
            sync__pb2.DataPackage.SerializeToString,
            sync__pb2.SyncResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetFullData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/DataSync/GetFullData',
            sync__pb2.Empty.SerializeToString,
            sync__pb2.DataPackage.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
