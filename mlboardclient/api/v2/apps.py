import os

import copy
import six

from mlboardclient.api import base
from mlboardclient.api.v2 import tasks
from mlboardclient import utils


urlparse = six.moves.urllib.parse


class App(base.Resource):
    resource_name = 'App'

    def __init__(self, manager, data):
        super(App, self).__init__(manager, data)
        if hasattr(self, 'configuration'):
            self.config = self.configuration

        self._task_manager = tasks.TaskManager(self.manager.http_client)

    def _task_from_config(self, task_raw_dict):
        task_dict = {
            'name': task_raw_dict['name'],
            'app': self.name,
            'config': copy.deepcopy(task_raw_dict)
        }
        task_dict['config']['revision'] = copy.deepcopy(
            self.config.get('revision')
        )
        return self._task_manager.resource_class(
            self._task_manager, task_dict
        )

    @property
    def tasks(self):
        tasks_from_config = self.config['spec']['tasks']

        res = tasks.TaskList()
        for t in tasks_from_config:
            res.append(self._task_from_config(t))

        return res

    def task(self, task_name):
        tasks_from_config = self.config['spec']['tasks']
        for t in tasks_from_config:
            if t['name'] == task_name:
                return self._task_from_config(t)

        return None

    def get_tasks(self):
        return self._task_manager.list(self.name)

    def get_task(self, task, build):
        return self._task_manager.get(self.name, task, build)


class AppsManager(base.ResourceManager):
    resource_class = App

    def create(self, name, config):
        self._ensure_not_empty(name=name)

        # If the specified definition is actually a file, read in the
        # definition file
        definition = utils.get_contents_if_file(config)

        resp = self.http_client.post(
            '/apps',
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def list(self):
        return self._list('/apps', response_key='apps')

    def get(self, name=None):
        # if name is empty it means code is
        # running inside kuberlab ML-task container
        # and will be picked up from env vars.
        if not name:
            project = os.environ.get('PROJECT_NAME')
            workspace = os.environ.get('WORKSPACE_ID')
            if project and workspace:
                name = workspace + '-' + project

        self._ensure_not_empty(name=name)

        return self._get('/apps/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/apps/%s' % name)
