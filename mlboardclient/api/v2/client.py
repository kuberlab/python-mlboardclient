
import os

import six

from mlboardclient.api import httpclient
from mlboardclient.api.v2 import apps
from mlboardclient.api.v2 import datasets
from mlboardclient.api.v2 import keys
from mlboardclient.api.v2 import servings
from mlboardclient.api.v2 import tasks
from mlboardclient import utils


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
        self.http_client = http_client

        # Create all resource managers.
        self.tasks = tasks.TaskManager(http_client)
        self.servings = servings.ServingManager(http_client)
        self.apps = apps.AppsManager(http_client)
        self.keys = keys.KeysManager(http_client)
        self.datasets = datasets.DatasetsManager(http_client)

    def model_upload(self, model_name, version, path,
                     workspace=None, project_name=None, auto_create=True):
        cloud_dealer_url = os.environ.get('CLOUD_DEALER_URL')
        if not cloud_dealer_url:
            raise RuntimeError(
                'To perform this operation CLOUD_DEALER_URL'
                ' environment var must be filled.'
            )

        key = self.keys.create()

        if not project_name:
            project_name = os.environ.get('PROJECT_NAME')
            if not project_name:
                raise RuntimeError('project name required')

        if not workspace:
            workspace = os.environ.get('WORKSPACE_NAME')
            if not workspace:
                raise RuntimeError('workspace required')

        # POST /api/v0.2/workspace/{workspace}/mlmodels/{mlmodel}/
        # versions/{version}/upload?secret=xxx&mlapp=name
        url = (
            '%s/workspace/%s/mlmodels/%s/versions/'
            '%s/upload?secret=%s&mlapp=%s&create=%s' % (
                cloud_dealer_url, workspace, model_name,
                version, key.key_id, project_name, str(auto_create).lower()
            )
        )

        stream = utils.stream_targz(path)

        resp = self.http_client.crud_provider.post(
            url,
            # data=form_data,
            files={'model': ('%s.tar.gz' % model_name, stream)}
        )

        self.keys.delete(key.key_id)

        if resp.status_code >= 400:
            raise RuntimeError('%s: %s' % (resp.status_code, resp.content))
