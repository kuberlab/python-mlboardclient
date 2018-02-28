
import copy
import os

import requests

import logging


CACERT = 'cacert'
CERT_FILE = 'cert'
CERT_KEY = 'key'
INSECURE = 'insecure'

LOG = logging.getLogger(__name__)


def log_request(func):
    def decorator(self, *args, **kwargs):
        resp = func(self, *args, **kwargs)
        LOG.debug(
            "HTTP %s %s %d", resp.request.method, resp.url, resp.status_code
        )
        return resp
    return decorator


class HTTPClient(object):
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.session = kwargs.pop('session', None)
        self.cacert = kwargs.get(CACERT)
        self.insecure = kwargs.get(INSECURE, False)
        self.ssl_options = {}

        if self.session:
            self.crud_provider = self.session
        else:
            self.crud_provider = requests

        if self.base_url.startswith('https'):
            if self.cacert and not os.path.exists(self.cacert):
                raise ValueError('Unable to locate cacert file '
                                 'at %s.' % self.cacert)

            if self.cacert and self.insecure:
                LOG.warning('Client is set to not verify even though '
                            'cacert is provided.')

            # These are already set by the session, so it's not needed
            if not self.session:
                if self.insecure:
                    self.ssl_options['verify'] = False
                else:
                    if self.cacert:
                        self.ssl_options['verify'] = self.cacert
                    else:
                        self.ssl_options['verify'] = True

                self.ssl_options['cert'] = (
                    kwargs.get(CERT_FILE),
                    kwargs.get(CERT_KEY)
                )

    @log_request
    def get(self, url, headers=None):
        options = self._get_request_options('get', headers)

        return self.crud_provider.get(self.base_url + url, **options)

    @log_request
    def post(self, url, body, headers=None):
        options = self._get_request_options('post', headers)

        return self.crud_provider.post(self.base_url + url,
                                       data=body, **options)

    @log_request
    def post_file(self, url, form_data, filename, file_or_data):
        return self.crud_provider.post(
            self.base_url + url,
            data=form_data,
            files={'file': (filename, file_or_data)}
        )

    @log_request
    def put(self, url, body, headers=None):
        options = self._get_request_options('put', headers)

        return self.crud_provider.put(self.base_url + url,
                                      data=body, **options)

    @log_request
    def delete(self, url, headers=None):
        options = self._get_request_options('delete', headers)

        return self.crud_provider.delete(self.base_url + url,
                                         **options)

    def _get_request_options(self, method, headers):
        headers = self._update_headers(headers)

        if method in ['post', 'put']:
            content_type = headers.get('content-type', 'application/json')
            headers['content-type'] = content_type

        options = copy.deepcopy(self.ssl_options)
        options['headers'] = headers

        return options

    def _update_headers(self, headers):
        if not headers:
            headers = {}

        return headers
