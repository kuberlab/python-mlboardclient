# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: predict.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from mlboardclient.ml_serving_utils import tensor_pb2 as tensor__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='predict.proto',
  package='ml_serving',
  syntax='proto3',
  serialized_options=_b('\n\036io.kuberlab.ml_serving.predictB\014PredictProtoP\001\242\002\003KLB'),
  serialized_pb=_b('\n\rpredict.proto\x12\nml_serving\x1a\x0ctensor.proto\"B\n\tModelSpec\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\x05\x12\x16\n\x0esignature_name\x18\x03 \x01(\t\"\xd2\x01\n\x0ePredictRequest\x12)\n\nmodel_spec\x18\x01 \x01(\x0b\x32\x15.ml_serving.ModelSpec\x12\x36\n\x06inputs\x18\x02 \x03(\x0b\x32&.ml_serving.PredictRequest.InputsEntry\x12\x15\n\routput_filter\x18\x03 \x03(\t\x1a\x46\n\x0bInputsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12&\n\x05value\x18\x02 \x01(\x0b\x32\x17.ml_serving.TensorProto:\x02\x38\x01\"&\n\x0fPredictJSONData\x12\x13\n\x0bjson_string\x18\x01 \x01(\x0c\"\xc0\x01\n\x0fPredictResponse\x12)\n\nmodel_spec\x18\x02 \x01(\x0b\x32\x15.ml_serving.ModelSpec\x12\x39\n\x07outputs\x18\x01 \x03(\x0b\x32(.ml_serving.PredictResponse.OutputsEntry\x1aG\n\x0cOutputsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12&\n\x05value\x18\x02 \x01(\x0b\x32\x17.ml_serving.TensorProto:\x02\x38\x01\"\x1e\n\x0bTestRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x1f\n\x0cTestResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2\xe1\x01\n\x11PredictionService\x12\x44\n\x07Predict\x12\x1a.ml_serving.PredictRequest\x1a\x1b.ml_serving.PredictResponse\"\x00\x12I\n\x0bPredictJSON\x12\x1b.ml_serving.PredictJSONData\x1a\x1b.ml_serving.PredictJSONData\"\x00\x12;\n\x04Test\x12\x17.ml_serving.TestRequest\x1a\x18.ml_serving.TestResponse\"\x00\x42\x36\n\x1eio.kuberlab.ml_serving.predictB\x0cPredictProtoP\x01\xa2\x02\x03KLBb\x06proto3')
  ,
  dependencies=[tensor__pb2.DESCRIPTOR,])




_MODELSPEC = _descriptor.Descriptor(
  name='ModelSpec',
  full_name='ml_serving.ModelSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='ml_serving.ModelSpec.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='ml_serving.ModelSpec.version', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature_name', full_name='ml_serving.ModelSpec.signature_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=43,
  serialized_end=109,
)


_PREDICTREQUEST_INPUTSENTRY = _descriptor.Descriptor(
  name='InputsEntry',
  full_name='ml_serving.PredictRequest.InputsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='ml_serving.PredictRequest.InputsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='ml_serving.PredictRequest.InputsEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=252,
  serialized_end=322,
)

_PREDICTREQUEST = _descriptor.Descriptor(
  name='PredictRequest',
  full_name='ml_serving.PredictRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model_spec', full_name='ml_serving.PredictRequest.model_spec', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='inputs', full_name='ml_serving.PredictRequest.inputs', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='output_filter', full_name='ml_serving.PredictRequest.output_filter', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_PREDICTREQUEST_INPUTSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=112,
  serialized_end=322,
)


_PREDICTJSONDATA = _descriptor.Descriptor(
  name='PredictJSONData',
  full_name='ml_serving.PredictJSONData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='json_string', full_name='ml_serving.PredictJSONData.json_string', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=324,
  serialized_end=362,
)


_PREDICTRESPONSE_OUTPUTSENTRY = _descriptor.Descriptor(
  name='OutputsEntry',
  full_name='ml_serving.PredictResponse.OutputsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='ml_serving.PredictResponse.OutputsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='ml_serving.PredictResponse.OutputsEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=486,
  serialized_end=557,
)

_PREDICTRESPONSE = _descriptor.Descriptor(
  name='PredictResponse',
  full_name='ml_serving.PredictResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model_spec', full_name='ml_serving.PredictResponse.model_spec', index=0,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='outputs', full_name='ml_serving.PredictResponse.outputs', index=1,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_PREDICTRESPONSE_OUTPUTSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=365,
  serialized_end=557,
)


_TESTREQUEST = _descriptor.Descriptor(
  name='TestRequest',
  full_name='ml_serving.TestRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='ml_serving.TestRequest.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=559,
  serialized_end=589,
)


_TESTRESPONSE = _descriptor.Descriptor(
  name='TestResponse',
  full_name='ml_serving.TestResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='ml_serving.TestResponse.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=591,
  serialized_end=622,
)

_PREDICTREQUEST_INPUTSENTRY.fields_by_name['value'].message_type = tensor__pb2._TENSORPROTO
_PREDICTREQUEST_INPUTSENTRY.containing_type = _PREDICTREQUEST
_PREDICTREQUEST.fields_by_name['model_spec'].message_type = _MODELSPEC
_PREDICTREQUEST.fields_by_name['inputs'].message_type = _PREDICTREQUEST_INPUTSENTRY
_PREDICTRESPONSE_OUTPUTSENTRY.fields_by_name['value'].message_type = tensor__pb2._TENSORPROTO
_PREDICTRESPONSE_OUTPUTSENTRY.containing_type = _PREDICTRESPONSE
_PREDICTRESPONSE.fields_by_name['model_spec'].message_type = _MODELSPEC
_PREDICTRESPONSE.fields_by_name['outputs'].message_type = _PREDICTRESPONSE_OUTPUTSENTRY
DESCRIPTOR.message_types_by_name['ModelSpec'] = _MODELSPEC
DESCRIPTOR.message_types_by_name['PredictRequest'] = _PREDICTREQUEST
DESCRIPTOR.message_types_by_name['PredictJSONData'] = _PREDICTJSONDATA
DESCRIPTOR.message_types_by_name['PredictResponse'] = _PREDICTRESPONSE
DESCRIPTOR.message_types_by_name['TestRequest'] = _TESTREQUEST
DESCRIPTOR.message_types_by_name['TestResponse'] = _TESTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ModelSpec = _reflection.GeneratedProtocolMessageType('ModelSpec', (_message.Message,), {
  'DESCRIPTOR' : _MODELSPEC,
  '__module__' : 'predict_pb2'
  # @@protoc_insertion_point(class_scope:ml_serving.ModelSpec)
  })
_sym_db.RegisterMessage(ModelSpec)

PredictRequest = _reflection.GeneratedProtocolMessageType('PredictRequest', (_message.Message,), {

  'InputsEntry' : _reflection.GeneratedProtocolMessageType('InputsEntry', (_message.Message,), {
    'DESCRIPTOR' : _PREDICTREQUEST_INPUTSENTRY,
    '__module__' : 'predict_pb2'
    # @@protoc_insertion_point(class_scope:ml_serving.PredictRequest.InputsEntry)
    })
  ,
  'DESCRIPTOR' : _PREDICTREQUEST,
  '__module__' : 'predict_pb2'
  # @@protoc_insertion_point(class_scope:ml_serving.PredictRequest)
  })
_sym_db.RegisterMessage(PredictRequest)
_sym_db.RegisterMessage(PredictRequest.InputsEntry)

PredictJSONData = _reflection.GeneratedProtocolMessageType('PredictJSONData', (_message.Message,), {
  'DESCRIPTOR' : _PREDICTJSONDATA,
  '__module__' : 'predict_pb2'
  # @@protoc_insertion_point(class_scope:ml_serving.PredictJSONData)
  })
_sym_db.RegisterMessage(PredictJSONData)

PredictResponse = _reflection.GeneratedProtocolMessageType('PredictResponse', (_message.Message,), {

  'OutputsEntry' : _reflection.GeneratedProtocolMessageType('OutputsEntry', (_message.Message,), {
    'DESCRIPTOR' : _PREDICTRESPONSE_OUTPUTSENTRY,
    '__module__' : 'predict_pb2'
    # @@protoc_insertion_point(class_scope:ml_serving.PredictResponse.OutputsEntry)
    })
  ,
  'DESCRIPTOR' : _PREDICTRESPONSE,
  '__module__' : 'predict_pb2'
  # @@protoc_insertion_point(class_scope:ml_serving.PredictResponse)
  })
_sym_db.RegisterMessage(PredictResponse)
_sym_db.RegisterMessage(PredictResponse.OutputsEntry)

TestRequest = _reflection.GeneratedProtocolMessageType('TestRequest', (_message.Message,), {
  'DESCRIPTOR' : _TESTREQUEST,
  '__module__' : 'predict_pb2'
  # @@protoc_insertion_point(class_scope:ml_serving.TestRequest)
  })
_sym_db.RegisterMessage(TestRequest)

TestResponse = _reflection.GeneratedProtocolMessageType('TestResponse', (_message.Message,), {
  'DESCRIPTOR' : _TESTRESPONSE,
  '__module__' : 'predict_pb2'
  # @@protoc_insertion_point(class_scope:ml_serving.TestResponse)
  })
_sym_db.RegisterMessage(TestResponse)


DESCRIPTOR._options = None
_PREDICTREQUEST_INPUTSENTRY._options = None
_PREDICTRESPONSE_OUTPUTSENTRY._options = None

_PREDICTIONSERVICE = _descriptor.ServiceDescriptor(
  name='PredictionService',
  full_name='ml_serving.PredictionService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=625,
  serialized_end=850,
  methods=[
  _descriptor.MethodDescriptor(
    name='Predict',
    full_name='ml_serving.PredictionService.Predict',
    index=0,
    containing_service=None,
    input_type=_PREDICTREQUEST,
    output_type=_PREDICTRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='PredictJSON',
    full_name='ml_serving.PredictionService.PredictJSON',
    index=1,
    containing_service=None,
    input_type=_PREDICTJSONDATA,
    output_type=_PREDICTJSONDATA,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Test',
    full_name='ml_serving.PredictionService.Test',
    index=2,
    containing_service=None,
    input_type=_TESTREQUEST,
    output_type=_TESTRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_PREDICTIONSERVICE)

DESCRIPTOR.services_by_name['PredictionService'] = _PREDICTIONSERVICE

# @@protoc_insertion_point(module_scope)
