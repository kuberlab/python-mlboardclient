
from mlboardclient.api.v2 import client as client_v2


def Client(base_url=client_v2.DEFAULT_BASE_URL):
    return client_v2.Client(base_url=base_url)


def update_task_info(data, app_name=None, task_name=None, build_id=None):
    return Client().tasks.update_task_info(
        data, app_name=app_name, task_name=task_name, build_id=build_id
    )
