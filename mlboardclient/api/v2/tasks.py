
import six
import time
import yaml

from mlboardclient.api import base
from mlboardclient import exceptions as exc
from mlboardclient import utils

urlparse = six.moves.urllib.parse


def build_aware(func):
    def decorator(self, *args, **kwargs):
        if not hasattr(self, 'build'):
            raise exc.MlboardClientException('Task has no build yet')
        return func(self, *args, **kwargs)
    return decorator


class Task(base.Resource):
    resource_name = 'Task'

    def __init__(self, manager, data):
        super(Task, self).__init__(manager, data)
        if hasattr(self, 'config'):
            self.config = self.config
            self.config_raw = yaml.safe_dump(
                self.config, default_flow_style=False
            )

        if not hasattr(self, 'status'):
            self.status = 'undefined'

    def __str__(self):
        if not hasattr(self, 'build'):
            build = None
        else:
            build = self.build

        return (
            '<Task name=%s build=%s status=%s>'
            % (self.name, build, self.status)
        )

    def __repr__(self):
        return self.__str__()

    def _update_attrs(self, new_task):
        if hasattr(new_task, 'build'):
            self.build = new_task.build
            self.status = new_task.status
            self.completed = new_task.completed
        return self

    def start(self):
        task = self.manager.create(self.app, self.config)
        return self._update_attrs(task)

    @build_aware
    def refresh(self):
        task = self.manager.get(self.app, self.name, self.build)
        return self._update_attrs(task)

    def wait(self, timeout=1800):
        @utils.timeout(seconds=timeout)
        @build_aware
        def _wait(self):
            while not self.completed:
                time.sleep(2)
                self.refresh()
            return self

        return _wait(self)

    def run(self):
        self.start()
        return self.wait()

    def logs(self):
        self.manager.logs(self.app, self.name, self.build)


class TaskManager(base.ResourceManager):
    resource_class = Task

    def list(self, app):
        url = '/apps/%s/tasks' % app

        return self._list(url, response_key=None)

    def get(self, app, task, build):
        self._ensure_not_empty(app=app, task=task, build=build)

        return self._get('/apps/%s/tasks/%s/%s' % (app, task, build))

    def create(self, app, config):
        self._ensure_not_empty(app=app)

        # If the specified definition is actually a file, read in the
        # definition file
        if isinstance(config, dict):
            definition = yaml.dump(config)
        else:
            definition = utils.get_contents_if_file(config)

        resp = self.http_client.post(
            '/apps/%s/tasks' % app,
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def logs(self, app, task, build):
        url = '/apps/%s/tasks/%s/%s/logs' % (app, task, build)

        resp = self.http_client.get(url)
        return base.extract_json(resp, None)
