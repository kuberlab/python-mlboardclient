
import six

from mlboardclient.api import httpclient
from mlboardclient.api.v2 import apps
from mlboardclient.api.v2 import servings
from mlboardclient.api.v2 import tasks


DEFAULT_BASE_URL = 'http://mlboard-v2.kuberlab:8082/api/v2'


class Client(object):
    def __init__(self, base_url, **kwargs):
        # We get the session at this point, as some instances of session
        # objects might have mutexes that can't be deep-copied.
        session = kwargs.pop('session', None)

        if base_url and not isinstance(base_url, six.string_types):
            raise RuntimeError('Mlboard url should be a string.')

        if not base_url:
            base_url = DEFAULT_BASE_URL

        http_client = httpclient.HTTPClient(
            base_url, session=session, **kwargs
        )

        # Create all resource managers.
        self.tasks = tasks.TaskManager(http_client)
        self.servings = servings.ServingManager(http_client)
        self.apps = apps.AppsManager(http_client)
