# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from mlboardclient.ml_serving_utils import predict_pb2 as predict__pb2


class PredictServiceStub(object):
  """The greeting service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Predict = channel.unary_unary(
        '/tensorflow.serving.PredictionService/Predict',
        request_serializer=predict__pb2.PredictRequest.SerializeToString,
        response_deserializer=predict__pb2.PredictResponse.FromString,
        )
    self.Test = channel.unary_unary(
        '/tensorflow.serving.PredictionService/Test',
        request_serializer=predict__pb2.TestRequest.SerializeToString,
        response_deserializer=predict__pb2.TestResponse.FromString,
        )


class PredictServiceServicer(object):
  """The ml serving service definition.
  """

  def Predict(self, request, context):
    """Does a prediction (model inference).
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Test(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_PredictServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Predict': grpc.unary_unary_rpc_method_handler(
          servicer.Predict,
          request_deserializer=predict__pb2.PredictRequest.FromString,
          response_serializer=predict__pb2.PredictResponse.SerializeToString,
      ),
      'Test': grpc.unary_unary_rpc_method_handler(
          servicer.Test,
          request_deserializer=predict__pb2.TestRequest.FromString,
          response_serializer=predict__pb2.TestResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'tensorflow.serving.PredictionService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
