# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: sync.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'sync.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nsync.proto\"T\n\x0b\x44\x61taPackage\x12\x1e\n\x08messages\x18\x01 \x03(\x0b\x32\x0c.MessageData\x12\x13\n\x0b\x64\x65leted_ids\x18\x02 \x03(\t\x12\x10\n\x08read_ids\x18\x03 \x03(\t\"p\n\x0bMessageData\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06sender\x18\x02 \x01(\t\x12\x11\n\trecipient\x18\x03 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\x12\x0e\n\x06status\x18\x05 \x01(\t\x12\x11\n\ttimestamp\x18\x06 \x01(\x01\"6\n\x0cSyncResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t\"\x07\n\x05\x45mpty2\x88\x01\n\x08\x44\x61taSync\x12\'\n\x08\x46ullSync\x12\x0c.DataPackage\x1a\r.SyncResponse\x12.\n\x0fIncrementalSync\x12\x0c.DataPackage\x1a\r.SyncResponse\x12#\n\x0bGetFullData\x12\x06.Empty\x1a\x0c.DataPackageb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'sync_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_DATAPACKAGE']._serialized_start=14
  _globals['_DATAPACKAGE']._serialized_end=98
  _globals['_MESSAGEDATA']._serialized_start=100
  _globals['_MESSAGEDATA']._serialized_end=212
  _globals['_SYNCRESPONSE']._serialized_start=214
  _globals['_SYNCRESPONSE']._serialized_end=268
  _globals['_EMPTY']._serialized_start=270
  _globals['_EMPTY']._serialized_end=277
  _globals['_DATASYNC']._serialized_start=280
  _globals['_DATASYNC']._serialized_end=416
# @@protoc_insertion_point(module_scope)
