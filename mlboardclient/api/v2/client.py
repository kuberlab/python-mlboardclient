
import os

import six

from mlboardclient.api import context
from mlboardclient.api import httpclient
from mlboardclient.api.v2 import apps
from mlboardclient.api.v2 import datasets
from mlboardclient.api.v2 import keys
from mlboardclient.api.v2 import servings
from mlboardclient.api.v2 import tasks
from mlboardclient import utils


DEFAULT_BASE_URL = 'http://mlboard-v2.kuberlab:8082/api/v2'


class Client(object):
    def __init__(self, base_url, workspace_id=None, workspace_name=None,
                 project_name=None, kuberlab_api_url=None, **kwargs):
        # We get the session at this point, as some instances of session
        # objects might have mutexes that can't be deep-copied.
        session = kwargs.pop('session', None)

        if workspace_id and project_name:
            self.app_id = '%s-%s' % (workspace_id, project_name)
        else:
            self.app_id = None

        self.ctx = context.MlboardContext(
            workspace_id=workspace_id,
            project_name=project_name,
            workspace=workspace_name,
            app_id=self.app_id,
            kuberlab_api_url=kuberlab_api_url,
        )

        if base_url and not isinstance(base_url, six.string_types):
            raise RuntimeError('Mlboard url should be a string.')

        if not base_url:
            base_url = DEFAULT_BASE_URL

        http_client = httpclient.HTTPClient(
            base_url, session=session, **kwargs
        )
        self.http_client = http_client

        # Create all resource managers.
        self.tasks = tasks.TaskManager(http_client)
        self.servings = servings.ServingManager(http_client)
        self.apps = apps.AppsManager(http_client, self.ctx)
        self.keys = keys.KeysManager(http_client)
        self.datasets = datasets.DatasetsManager(http_client)

    def update_task_info(self, data, app_name=None,
                         task_name=None, build_id=None):
        # Alias for self.tasks.update_task_info

        if self.app_id and not app_name:
            app_name = self.app_id

        return self.tasks.update_task_info(
            data, app_name=app_name,
            task_name=task_name, build_id=build_id
        )

    def model_upload(self, model_name, version, path,
                     workspace=None, project_name=None, auto_create=True,
                     include_directory=False):
        if not self.ctx.kuberlab_api_url:
            cloud_dealer_url = os.environ.get('CLOUD_DEALER_URL')
        else:
            cloud_dealer_url = self.ctx.kuberlab_api_url

        if not cloud_dealer_url:
            raise RuntimeError(
                'To perform this operation CLOUD_DEALER_URL'
                ' environment var must be filled.'
            )

        key = self.keys.create()

        if not project_name:
            if not self.ctx.project_name:
                project_name = os.environ.get('PROJECT_NAME')
            else:
                project_name = self.ctx.project_name

            if not project_name:
                raise RuntimeError('project name required')

        if not workspace:
            if not self.ctx.workspace:
                workspace = os.environ.get('WORKSPACE_NAME')
            else:
                workspace = self.ctx.workspace

            if not workspace:
                raise RuntimeError('workspace required')

        # POST /api/v0.2/workspace/{workspace}/mlmodels/{mlmodel}/
        # versions/{version}/upload?secret=xxx&mlapp=name
        url = (
            '%s/workspace/%s/mlmodel/%s/versions/'
            '%s/upload?secret=%s&mlapp=%s&create=%s' % (
                cloud_dealer_url, workspace, model_name,
                version, key.key_id, project_name, str(auto_create).lower()
            )
        )

        stream = utils.stream_targz(path, include_directory=include_directory)

        resp = self.http_client.crud_provider.post(
            url,
            # data=form_data,
            files={'model': ('%s.tar.gz' % model_name, stream)}
        )

        self.keys.delete(key.key_id)

        if resp.status_code >= 400:
            raise RuntimeError('%s: %s' % (resp.status_code, resp.content))
