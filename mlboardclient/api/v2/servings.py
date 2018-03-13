import os
import six

from mlboardclient.api import base
from mlboardclient import utils

urlparse = six.moves.urllib.parse


class Serving(base.Resource):
    resource_name = 'Serving'


class ServingManager(base.ResourceManager):
    resource_class = Serving

    def create(self, app, config):
        self._ensure_not_empty(app=app)

        # If the specified definition is actually a file, read in the
        # definition file
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

    def delete(self, app, task, build):
        self._ensure_not_empty(app=app, task=task, build=build)

        self._delete('/apps/%s/tasks/%s/%s/serve' % (app, task, build))

    def call(self, serving_name, model_name, data,
             signature=None, version=None, port=None, namespace=None):
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

        if not namespace:
            raise RuntimeError('namespace parameter required.')
        if not port:
            port = '9000'

        serving_addr = '%s.%s' % (serving_name, namespace)

        resp = self.http_client.post(
            url,
            data,
            headers={'Proxy_addr': serving_addr, 'Proxy_port': port}
        )
        # Need extract json?
        return resp
