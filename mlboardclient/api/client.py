
from mlboardclient.api.v2 import client as client_v2


def Client(base_url=client_v2.DEFAULT_BASE_URL):
    return client_v2.Client(base_url=base_url)
