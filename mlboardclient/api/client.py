import requests

from mlboardclient.api.v2 import client as client_v2


def Client(base_url=client_v2.DEFAULT_BASE_URL, workspace_id=None,
           workspace_name=None, project_name=None, token=None,
           kuberlab_api_url=None):

    if token:
        session = requests.Session()
        session.headers['Authorization'] = 'Bearer %s' % token
    else:
        session = None

    return client_v2.Client(
        base_url=base_url,
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        project_name=project_name,
        kuberlab_api_url=kuberlab_api_url,
        session=session,
    )


def update_task_info(data, app_name=None, task_name=None, build_id=None):
    return Client().tasks.update_task_info(
        data, app_name=app_name, task_name=task_name, build_id=build_id
    )
