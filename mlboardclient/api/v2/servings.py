
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

    def list(self, app, task, build):
        self._ensure_not_empty(app=app, task=task, build=build)

        return self._list(
            '/apps/%s/tasks/%s/%s/servings' % (app, task, build)
        )

    def delete(self, app, task, build):
        self._ensure_not_empty(app=app, task=task, build=build)

        self._delete('/apps/%s/tasks/%s/%s/serve' % (app, task, build))
