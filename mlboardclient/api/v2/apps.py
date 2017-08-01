
import yaml
import six

from mlboardclient.api import base
from mlboardclient import utils


urlparse = six.moves.urllib.parse


class App(base.Resource):
    resource_name = 'App'

    def __init__(self, manager, data):
        super(App, self).__init__(manager, data)
        if hasattr(self, 'config'):
            self.config_raw = self.config
            self.config = yaml.safe_load(self.config_raw)


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
