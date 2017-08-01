
import six

from mlboardclient.api import base

urlparse = six.moves.urllib.parse


class Task(base.Resource):
    resource_name = 'Task'


class TaskManager(base.ResourceManager):
    resource_class = Task

    def list(self, app):
        url = '/apps/%s/tasks' % app

        return self._list(url, response_key=None)

    def get(self, app, task, build):
        self._ensure_not_empty(app=app, task=task, build=build)

        return self._get('/apps/%s/tasks/%s/%s' % (app, task, build))
