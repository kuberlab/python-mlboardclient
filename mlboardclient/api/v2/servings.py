import base64
import os
import re
import six
import yaml

from mlboardclient import api
from mlboardclient.api import base
from mlboardclient import utils

urlparse = six.moves.urllib.parse
ws_pattern = re.compile('^[0-9]+-')


class Serving(base.Resource):
    resource_name = 'Serving'

    def __init__(self, manager, data):
        super(Serving, self).__init__(manager, data)

        if isinstance(self.config, six.string_types):
            self.config = yaml.safe_load(self.config)

    def start(self, task_name, build):
        self.config['taskName'] = task_name
        self.config['build'] = build
        serv = self.manager.create(self.app, self.config)
        serv.config = yaml.safe_load(serv.config)
        return serv

    def stop(self):
        task = self.config.get('taskName') or getattr(self, 'task', '')
        if not (task or self.config.get('build')):
            raise RuntimeError(
                'Serving is not pointed to any task/build.'
                ' config["taskName"] and config["build"] must be filled.'
            )

        self.manager.delete(self.app, task, self.config['build'])
        delattr(self, 'status')

    def get_name(self):
        if not hasattr(self, 'build') or not hasattr(self, 'serving'):
            return self.name

        ws_part = ws_pattern.findall(self.app)
        if len(ws_part) != 1:
            return self.name

        project_name = self.app[len(ws_part[0]):]
        return '%s-%s-%s-%s' % (project_name, self.name, self.task, self.build)

    def logs(self):
        task = self.config.get('taskName') or getattr(self, 'serving', '')
        if not (task or self.config.get('build')):
            raise RuntimeError(
                'Serving is not pointed to any task/build.'
                ' config["taskName"] and config["build"] must be filled.'
            )

        return self.manager.logs(self.app, task, self.config['build'])


class ServingList(list):
    def get(self, name):
        for s in self:
            if s.name == name:
                return Serving(s.manager, s.to_dict())


class ServingManager(base.ResourceManager):
    resource_class = Serving

    @staticmethod
    def _preprocess_config(config):
        c = config
        if not c.get('args'):
            return

        args = c['args']
        if isinstance(args, six.string_types):
            c['command'] = '%s %s' % (c.get('command', ''), c['args'])
        elif isinstance(args, dict):
            args_str = ' '.join(
                ['--%s=%s' % (k, v) for k, v in args.items()]
            )
            c['command'] = '%s %s' % (c.get('command', ''), args_str)
        del c['args']

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
            '/apps/%s/servings' % app,
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def list(self, app, task):
        self._ensure_not_empty(app=app, task=task)

        return self._list(
            '/apps/%s/tasks/%s/servings' % (app, task)
        )

    def logs(self, app, task, build):
        url = '/apps/%s/tasks/%s/%s/serve/logs' % (
            app, task, build
        )
        resp = self.http_client.get(url)
        return base.extract_json(resp, None)

    def delete(self, app, task, build):
        self._ensure_not_empty(app=app, task=task, build=build)

        self._delete('/apps/%s/tasks/%s/%s/serve' % (app, task, build))

    def call(self, serving_name, model_name, data,
             signature=None, version=None, port=None, namespace=None,
             serving_address=None):
        """Call specific serving with given data.

        :param serving_name: Serving name
        :param model_name: Model name which will be used in model.spec.name
          in tensorflow request
        :param signature:
        :param version: model_version
        :param port: Serving port (int)
        :param data: Should be in the form:
        {
          "features": [  # Required if not inputs
            {"x": {"Float": 55}},
            {"x": {"Float": 40}}
          ],
          "inputs": { # Required if not features
            "input_key": {"dtype": 7, "data": "string"}
          },
          "out_filter": ["string"], # Optional
          "out_mime_type": "image/png", # Optional
        }
        "dtype" is from mlboardclient.api
        :param namespace: kubernetes namespace
        :return:
        """
        url = '/tfproxy/%s' % model_name
        if signature:
            url += '/%s' % signature
        if version:
            url += '/%s' % version
        if not namespace:
            # Try to get namespace from env.
            ws_name = os.environ.get('WORKSPACE_NAME')
            ws_id = os.environ.get('WORKSPACE_ID')
            namespace = '%s-%s' % (ws_id, ws_name) if ws_id else None

        # Preprocess input
        if isinstance(data, dict) and data.get('inputs'):
            if isinstance(data['inputs'], dict):
                for k, v in data['inputs'].items():
                    if not isinstance(v, dict):
                        continue

                    if v.get('dtype') == api.DT_STRING:
                        v['data'] = base64.encodestring(
                            v.get('data', '')).decode()

        if not namespace and not serving_address:
            raise RuntimeError('namespace parameter required.')
        elif serving_address:
            serving_addr = serving_address
        else:
            serving_addr = '%s.%s' % (serving_name, namespace)

        if not port:
            port = '9000'

        resp = self.http_client.post(
            url,
            data,
            headers={
                'Proxy-addr': serving_addr,
                'Proxy-port': str(port),
                'Content-Type': 'application/json'
            }
        )
        # Need extract json?
        return resp
