
from mlboardclient.api import base


class Key(base.Resource):
    resource_name = 'Key'


class KeysManager(base.ResourceManager):
    resource_class = Key

    def create(self):
        resp = self.http_client.post(
            '/keys',
            '{}',
            headers={'content-type': 'application/json'}
        )

        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def check(self, id):
        self._ensure_not_empty(id=id)

        return self._get('/keys/%s' % id)

    def delete(self, id):
        self._ensure_not_empty(id=id)

        self._delete('/keys/%s' % id)
