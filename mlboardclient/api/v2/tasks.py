import re
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
    """Task resource class.

    config field contains task configuration including resources config.
    Task config can be rewritten before start using:

     - apply_env()
     - apply_resource_overrides()

    See the corresponding method doc for help.
    Also it is possible to pass additional command arguments as dict:

    >>> task.config['resources'][0]['command']
    u'python my_script.py'
    >>> task.config['resources'][0]['args'] = {
    ...   'var1': 'val', 'batch-size': 23, 'test_arg': 12.2
    ... }
    >>> task.start()
    >>> task.config['resources'][0]['command']
    u'python my_script.py --batch-size 23 --test_arg 12.2 --var1 val'

    Resource args can be also a string:
    >>> task.config['resources'][0]['command']
    u'python my_script.py'
    >>> task.config['resources'][0]['args'] = '--my-super-arg 42; echo "Done!"'
    >>> task.start()
    >>> task.config['resources'][0]['command']
    u'python my_script.py --my-super-arg 42; echo "Done!"'
    """
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

    def wait(self, timeout=1800, delay=3):
        @utils.timeout(seconds=timeout)
        @build_aware
        def _wait(self):
            while not self.completed:
                time.sleep(delay)
                self.refresh()
            return self

        return _wait(self)

    def run(self, timeout=1800, delay=3):
        self.start()
        return self.wait(timeout=timeout, delay=delay)

    def logs(self):
        return self.manager.logs(self.app, self.name, self.build)

    def apply_env(self, envs):
        """Adds/Modifies environment variables for task resources.

        envs parameter must be a list containing env var specs as following:
          ENV_VAR=VALUE

        Example:

        task.apply_env(['MY_VAR=MY-VAL', 'SOME_VAR=expression=22'])

        In the example above variable 'SOME_VAR'
        will be assigned value 'expression=22'.

        :param envs: list of env variables spec.
        """
        apply_env(self, envs)

    def apply_resource_override(self, resource_overrides):
        """Overrides resource-specific config values for given task.

        Resource override spec format:
          <resource-name>.<param>=<value>
          <resource-name>.<key>.<nested-key>=<value>

        It is allowed to pass '*' as resource name: override will be applied
        to all resources:
          *.<key>=<value>

        Examples:

          task.apply_resource_overrides(
            [
              '*.resources.requests.cpu=1000m',
              '*.resources.requests.memory=1Gi'
            ]
          )

          task.apply_resource_overrides(['worker.replicas=3'])

        :param resource_overrides: list of resource override spec.
        :type resource_overrides: list
        """
        apply_resource_overrides(self, resource_overrides)


class TaskList(list):
    def get(self, task_name):
        for t in self:
            if t.name == task_name:
                return Task(t.manager, t.to_dict())


class TaskManager(base.ResourceManager):
    resource_class = Task

    def list(self, app):
        url = '/apps/%s/tasks' % app

        return self._list(url, response_key=None)

    def get(self, app, task, build):
        self._ensure_not_empty(app=app, task=task, build=build)

        return self._get('/apps/%s/tasks/%s/%s' % (app, task, build))

    @staticmethod
    def _preprocess_config(config):
        for r in config['resources']:
            if not r.get('args'):
                continue

            args = r['args']
            if isinstance(args, six.string_types):
                r['command'] = '%s %s' % (r.get('command', ''), r['args'])
            elif isinstance(args, dict):
                args_str = ' '.join(
                    ['--%s %s' % (k, v) for k, v in args.items()]
                )
                r['command'] = '%s %s' % (r.get('command', ''), args_str)
            del r['args']

    def create(self, app, config):
        self._ensure_not_empty(app=app)

        # If the specified definition is actually a file, read in the
        # definition file
        if isinstance(config, dict):
            self._preprocess_config(config)
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


def apply_env(task, envs):
    """Adds/Modifies environment variables for task resources.

    envs parameter must be a list containing env var specs as following:
      ENV_VAR=VALUE

    Example:

    apply_env(task, ['MY_VAR=MY-VAL', 'SOME_VAR=expression=22'])

    In the example above variable 'SOME_VAR'
    will be assigned value 'expression=22'.

    :param task: Task object to modify.
    :type task: Task
    :param envs: list of env variables spec.
    """
    if not envs:
        return

    env_vars = {}
    for e in envs:
        name_value = e.split('=')
        if len(name_value) < 2:
            raise RuntimeError(
                'Invalid env override spec: %s' % e
            )

        name = name_value[0]
        value = '='.join(name_value[1:])
        env_vars[name] = value

    for r in task.config['resources']:
        env_override = env_vars.copy()
        for e in r.get('env', []):
            if e['name'] in env_override:
                e['value'] = env_override.pop(e['name'])

        if not r.get('env'):
            r['env'] = []

        for n, v in env_override.items():
            r['env'].append({'name': n, 'value': v})


def apply_resource_overrides(task, resource_overrides):
    """Overrides resource-specific config values for given task.

    Resource override spec format:
      <resource-name>.<param>=<value>
      <resource-name>.<key>.<nested-key>=<value>

    It is allowed to pass '*' as resource name: override will be applied
    to all resources:
      *.<key>=<value>

    Examples:
      apply_resource_overrides(
        task, [
          '*.resources.requests.cpu=1000m',
          '*.resources.requests.memory=1Gi'
        ]
      )

      apply_resource_overrides(task, ['worker.replicas=3'])

    :param task: Task object to modify.
    :type task: Task
    :param resource_overrides: list of resource override spec.
    :type resource_overrides: list
    """
    if not resource_overrides:
        return

    cfg = task.config
    for override in resource_overrides:
        splitted = override.split('=')
        if len(splitted) < 2:
            raise RuntimeError(
                'Invalid resource override spec: %s' % override
            )
        path = splitted[0]
        value = '='.join(splitted[1:])

        splitted = path.split('.')
        if len(splitted) < 2:
            raise RuntimeError(
                'Invalid resource override path: %s' % path
            )
        resource = splitted[0]
        path = splitted[1:-1]

        for r in cfg['resources']:
            if r['name'] != resource and resource != '*':
                continue
            if r['name'] == resource or resource == '*':
                to_replace = r
                for p in path:
                    inner = to_replace.get(p)
                    if inner is None:
                        to_replace[p] = {}
                    to_replace = to_replace[p]

                v = to_replace.get(splitted[-1])
                if not v:
                    if value.isdigit():
                        to_replace[splitted[-1]] = int(value)
                    elif re.match("^[\.0-9]+$", value):
                        to_replace[splitted[-1]] = float(value)
                    else:
                        to_replace[splitted[-1]] = value
                    break

                if isinstance(to_replace[splitted[-1]], int):
                    to_replace[splitted[-1]] = int(value)
                elif isinstance(to_replace[splitted[-1]], float):
                    to_replace[splitted[-1]] = float(value)
                else:
                    to_replace[splitted[-1]] = value
