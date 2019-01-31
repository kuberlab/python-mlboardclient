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


def stream_targz(path, include_directory=False):
    if not os.path.exists(path):
        raise RuntimeError('%s: No such file or directory' % path)

    if os.path.isdir(path):
        if include_directory:
            dirname = os.path.dirname(path)
            basename = os.path.basename(path)
        else:
            basename = '.'
            dirname = path

        cmd = ['tar', 'czf', '-', basename]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=dirname)

        return p.stdout
    else:
        return open(path, 'rb')


def env_value(name, default_value=None):
    val = os.environ.get(name)
    if not val:
        return default_value
    else:
        return val


def setup_tf_distributed(mode, worker_names='worker', ps_names='ps', chief_name='chief'):
    workers = env_value('{}_NODES'.format(worker_names.upper()), '')
    ps = env_value('{}_NODES'.format(ps_names.upper()), '')
    ps_spec = ps.split(',')
    worker_spec = workers.split(',')
    offsets = {}
    for i, w in enumerate(worker_spec):
        if not w in offsets:
            offsets[w] = i
    task_index = int(env_value('REPLICA_INDEX', '0'))

    cluster = {chief_name: [worker_spec[0]] if len(worker_spec) > 0 else [],
               'ps': ps_spec,
               'worker': worker_spec[1:] if len(worker_spec) > 1 else []}

    if mode == 'worker':
        if task_index == 0:
            task = {'type': chief_name, 'index': 0}
        else:
            task = {'type': 'worker', 'index': task_index - 1}
    elif mode == 'ps':
        task = {'type': 'ps', 'index': task_index}
    elif mode == 'eval':
        if len(cluster['chief']) < 1 or len(cluster['ps']) < 1:
            cluster = {'chief': ['fake_worker1:2222'], 'ps': ['fake_ps:2222'], 'worker': ['fake_worker2:2222']}
        task = {'type': 'evaluator', 'index': task_index}
    else:
        RuntimeError('Supported mode (worker, ps, eval)')

    tf_config = {
        'cluster': cluster,
        'task': task}

    if chief_name == 'master':
        tf_config['environment'] = 'cloud'

    tf_config = json.dumps(tf_config)

    return tf_config

