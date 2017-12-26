
import copy
import json


class Resource(object):
    resource_name = 'Something'
    defaults = {}

    def __init__(self, manager, data):
        self.manager = manager
        self._data = data
        self._set_defaults()
        self._set_attributes()

    def _set_defaults(self):
        for k, v in self.defaults.items():
            if k not in self._data:
                self._data[k] = v

    def _set_attributes(self):
        for k, v in self._data.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass

    def to_dict(self):
        return copy.deepcopy(self._data)

    def __str__(self):
        vals = ", ".join(["%s='%s'" % (n, v)
                          for n, v in self._data.items()])
        return "%s [%s]" % (self.resource_name, vals)


def _check_items(obj, searches):
    try:
        return all(getattr(obj, attr) == value for (attr, value) in searches)
    except AttributeError:
        return False


def extract_json(response, response_key):
    if response_key is not None:
        return get_json(response)[response_key]
    else:
        return get_json(response)


class ResourceManager(object):
    resource_class = None

    def __init__(self, http_client):
        self.http_client = http_client

    def find(self, **kwargs):
        return [i for i in self.list() if _check_items(i, kwargs.items())]

    def _ensure_not_empty(self, **kwargs):
        for name, value in kwargs.items():
            if value is None or (isinstance(value, str) and len(value) == 0):
                raise APIException(
                    400,
                    '%s is missing field "%s"' %
                    (self.resource_class.__name__, name)
                )

    def _copy_if_defined(self, data, **kwargs):
        for name, value in kwargs.items():
            if value is not None:
                data[name] = value

    def _create(self, url, data, response_key=None, dump_json=True):
        if dump_json:
            data = json.dumps(data)

        resp = self.http_client.post(url, data)

        if resp.status_code != 201:
            self._raise_api_exception(resp)

        return self.resource_class(self, extract_json(resp, response_key))

    def _update(self, url, data, response_key=None, dump_json=True):
        if dump_json:
            data = json.dumps(data)

        resp = self.http_client.put(url, data)

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return self.resource_class(self, extract_json(resp, response_key))

    def _list(self, url, response_key=None):
        resp = self.http_client.get(url)

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return [self.resource_class(self, resource_data)
                for resource_data in extract_json(resp, response_key)]

    def _get(self, url, response_key=None):
        resp = self.http_client.get(url)

        if resp.status_code == 200:
            return self.resource_class(self, extract_json(resp, response_key))
        else:
            self._raise_api_exception(resp)

    def _delete(self, url):
        resp = self.http_client.delete(url)

        if resp.status_code != 204:
            self._raise_api_exception(resp)

    def _plurify_resource_name(self):
        return self.resource_class.resource_name + 's'

    @staticmethod
    def _raise_api_exception(resp):
        try:
            error_data = (resp.headers.get("Server-Error-Message", None) or
                          get_json(resp).get("message"))
        except ValueError:
            error_data = resp.content
        raise APIException(error_code=resp.status_code,
                           error_message=error_data)


def get_json(response):
    """Gets JSON representation of response.

    This method provided backward compatibility with old versions
    of requests library.
    """
    json_field_or_function = getattr(response, 'json', None)

    if callable(json_field_or_function):
        return response.json()
    else:
        return json.loads(response.content)


class APIException(Exception):
    def __init__(self, error_code=None, error_message=None):
        super(APIException, self).__init__(error_message)
        self.error_code = error_code
        self.error_message = error_message
