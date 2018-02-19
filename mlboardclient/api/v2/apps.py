
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

    @property
    def tasks(self):
        tasks_from_config = self.config['spec']['tasks']

        res = []
        for t in tasks_from_config:
            task_dict = {
                'name': t['name'],
                'app': self.name,
                'config': copy.deepcopy(t)
            }
            task_dict['config']['revision'] = copy.deepcopy(
                self.config.get('revision')
            )
            res.append(
                self._task_manager.resource_class(
                    self._task_manager, task_dict
                )
            )

        return res

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

    def get(self, name):
        self._ensure_not_empty(name=name)

        return self._get('/apps/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/apps/%s' % name)
