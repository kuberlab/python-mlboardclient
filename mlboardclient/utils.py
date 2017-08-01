import json
import os
import yaml

from six.moves.urllib import parse
from six.moves.urllib import request

from mlboardclient import exceptions


def do_action_on_many(action, resources, success_msg, error_msg):
    """Helper to run an action on many resources."""
    failure_flag = False

    for resource in resources:
        try:
            action(resource)
            print(success_msg % resource)
        except Exception as e:
            failure_flag = True
            print(e)

    if failure_flag:
        raise exceptions.MlboardClientException(error_msg)


def load_content(content):
    if content is None or content == '':
        return dict()

    try:
        data = yaml.safe_load(content)
    except Exception:
        data = json.loads(content)

    return data


def load_file(path):
    with open(path, 'r') as f:
        return load_content(f.read())


def get_contents_if_file(contents_or_file_name):
    """Get the contents of a file.

    If the value passed in is a file name or file URI, return the
    contents. If not, or there is an error reading the file contents,
    return the value passed in as the contents.

    For example, a workflow definition will be returned if either the
    workflow definition file name, or file URI are passed in, or the
    actual workflow definition itself is passed in.
    """
    try:
        if parse.urlparse(contents_or_file_name).scheme:
            definition_url = contents_or_file_name
        else:
            path = os.path.abspath(contents_or_file_name)
            definition_url = parse.urljoin(
                'file:',
                request.pathname2url(path)
            )
        return request.urlopen(definition_url).read().decode('utf8')
    except Exception:
        return contents_or_file_name


def load_json(input_string):
    try:
        with open(input_string) as fh:
            return json.load(fh)
    except IOError:
        return json.loads(input_string)
