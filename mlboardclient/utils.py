import errno
import functools
import json
import logging
import os
import signal

import six
from six.moves.urllib import parse
from six.moves.urllib import request
import yaml

from mlboardclient import exceptions

if six.PY2:
    import subprocess32 as subprocess
else:
    import subprocess


LOG = logging.getLogger(__name__)


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


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise exceptions.TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            if seconds > 0:
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                if seconds > 0:
                    signal.alarm(0)
            return result

        return functools.wraps(func)(wrapper)

    return decorator


def execute_command(cmd, dirname=None, timeout=300,
                    stdout_control=True):
    msg = 'Execute command'
    if dirname:
        msg += ' in DIR=%s' % dirname

    LOG.debug('%s: %s' % (msg, ' '.join(cmd)))

    if not dirname:
        dirname = os.getcwd()

    if stdout_control:
        out = subprocess.PIPE
    else:
        out = None

    p = subprocess.Popen(
        cmd,
        stdout=out,
        stderr=subprocess.PIPE,
        cwd=dirname
    )

    stdout, stderr = p.communicate(timeout=timeout)
    return stdout, stderr, p.returncode


def stream_targz(path):
    if not os.path.exists(path):
        raise RuntimeError('%s: No such file or directory' % path)

    if os.path.isdir(path):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        cmd = ['tar', 'czf', '-', basename]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=dirname)

        return p.stdout
    else:
        return open(path, 'rb')

def env_value(name,default_value=None):
    val = os.environ.get(name)
    if val is None or val=='':
        return default_value
    else:
        return val