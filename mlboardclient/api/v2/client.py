import logging
import os

import six

from mlboardclient.api import context
from mlboardclient.api import httpclient
from mlboardclient.api.v2 import apps
from mlboardclient.api.v2 import datasets
from mlboardclient.api.v2 import keys
from mlboardclient.api.v2 import servings
from mlboardclient.api.v2 import tasks


LOG = logging.getLogger(__name__)
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
        self.servings = servings.ServingManager(http_client)
        self.apps = apps.AppsManager(http_client, self.ctx)
        self.tasks = tasks.TaskManager(http_client, self.apps)
        self.keys = keys.KeysManager(http_client)
        self.datasets = datasets.DatasetsManager(http_client)

    def update_task_info(self, data, app_name=None,
                         task_name=None, build_id=None, fail_on_error=False):
        # Alias for self.tasks.update_task_info

        if self.app_id and not app_name:
            app_name = self.app_id

        try:
            return self.tasks.update_task_info(
                data, app_name=app_name,
                task_name=task_name, build_id=build_id,
            )
        except Exception as e:
            if fail_on_error:
                raise e
            else:
                LOG.warning(e)

    def _get_app_id(self):
        if not self.ctx.workspace_id:
            workspace_id = os.environ.get('WORKSPACE_ID')
        else:
            workspace_id = self.ctx.workspace_id

        if workspace_id and self._get_project_name():
            return '{}-{}'.format(workspace_id, self._get_project_name())

        return None

    def _get_project_name(self):
        if not self.ctx.project_name:
            project_name = os.environ.get('PROJECT_NAME')
        else:
            project_name = self.ctx.workspace

        return project_name

    def _get_serving_spec(self, app_id):
        app = self.apps.get(app_id)
        servings = app.servings
        if len(servings) == 0:
            return

        serving = servings[0]
        return serving.config

    def model_upload(self, model_name, version, path,
                     workspace=None, auto_create=True, spec=None):
        if not workspace:
            if not self.ctx.workspace:
                workspace = os.environ.get('WORKSPACE_NAME')
            else:
                workspace = self.ctx.workspace

            if not workspace:
                raise RuntimeError('workspace required')

        app_id = self._get_app_id()
        if not spec and app_id:
            spec = self._get_serving_spec(app_id)

        self.datasets.push(
            workspace,
            model_name,
            version,
            path,
            type='model',
            create=auto_create,
            spec=spec,
        )
