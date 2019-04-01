import grpc
from mlboardclient.ml_serving_utils import predict_pb2
from mlboardclient.ml_serving_utils import predict_pb2_grpc
from mlboardclient.ml_serving_utils import tensor_util


MAX_LENGTH = 67108864  # 64 MB
opts = [
    ('grpc.max_send_message_length', MAX_LENGTH),
    ('grpc.max_receive_message_length', MAX_LENGTH)
]


def get_stub(addr):
    channel = grpc.insecure_channel(addr, options=opts)

    stub = predict_pb2_grpc.PredictServiceStub(channel)
    return stub


def predict_grpc(data, serv_addr):
    inputs = {}
    for k, v in data.items():
        tensor_proto = tensor_util.make_tensor_proto(v)
        inputs[k] = tensor_proto

    with grpc.insecure_channel(serv_addr, options=opts) as channel:
        stub = predict_pb2_grpc.PredictServiceStub(channel)
        response = stub.Predict(predict_pb2.PredictRequest(inputs=inputs))

    outputs = {}
    for k, v in response.outputs.items():
        outputs[k] = tensor_util.make_ndarray(v)

    return outputs
