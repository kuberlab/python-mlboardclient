import logging
from os import path

from mlboardclient.api import base
from mlboardclient import utils


LOG = logging.getLogger(__name__)


class Dataset(base.Resource):
    resource_name = 'Dataset'


class DatasetsManager(base.ResourceManager):
    resource_class = Dataset
    base_command = 'kdataset'

    def change(self, root, dataset, version):
        filename = path.join(root, '.%s__%s' % (dataset, version))
        content = open(filename).read()
        LOG.info('Change dataset to %s:%s: %s' % (dataset, version, content))

    def pull(self, workspace, name, version, to_dir, type='dataset', file_name=None):
        cmd = ['pull', workspace, '%s:%s' % (name, version)]
        if file_name:
            cmd += ['-O', file_name]
        cmd += ['--type', type]

        out, err = self._run_kdataset(*cmd, dirname=to_dir, timeout=1800)
        print(out)

    def push(self, workspace, name, version, from_dir,
             type='dataset', create=False, publish=False, force=False,
             chunk_size=None, concurrency=None):
        cmd = ['push', workspace, '%s:%s' % (name, version)]
        if force:
            cmd += ['--force']
        if create:
            cmd += ['--create']
        if publish:
            cmd += ['--publish']
        if chunk_size:
            cmd += ['--chunk-size', str(chunk_size)]
        if concurrency:
            cmd += ['--concurrency', str(concurrency)]

        cmd += ['--type', type]

        self._run_kdataset(
            *cmd, dirname=from_dir, timeout=1800, stdout_control=False
        )

    def list(self, workspace, type='dataset'):
        cmd = ['dataset-list', workspace]
        cmd += ['--type', type]
        out, err = self._run_kdataset(*cmd)
        # DATASETS:
        # dataset1
        # dataset2
        # ...
        return out.split('\n')[1:-1]

    def delete(self, workspace, name, type='dataset'):
        cmd = ['dataset-delete', workspace, name]
        cmd += ['--type', type]
        out, err = self._run_kdataset('dataset-delete', workspace, name)
        print(out)

    def version_list(self, workspace, name, type='dataset'):
        cmd = ['version-list', workspace, name]
        cmd += ['--type', type]
        out, err = self._run_kdataset(*cmd)
        # VERSIONS SIZE
        # 1.0.0    25.052M
        # 1.0.1    34.042K
        # ...
        versions = []
        lines = out.split('\n')
        for l in lines[1:-1]:
            splitted = l.split()
            if len(splitted) != 4:
                raise RuntimeError(
                    'Wrong dataset client/server version. Please update'
                )

            v = splitted[0]
            size = splitted[1]
            versions.append({'version': v, 'size': size})

        return versions

    def version_delete(self, workspace, name, version, type='dataset'):
        cmd = ['version-delete', workspace, '%s:%s' %(name, version)]
        cmd += ['--type', type]
        out, err = self._run_kdataset(*cmd)
        print(out)

    def _run_kdataset(self, *args, **options):
        out, err, code = utils.execute_command(
            [self.base_command] + list(args),
            **options
        )
        if code != 0:
            msg = ''
            if out:
                msg = 'Out=%s; ' % out
            msg += 'Err=%s' % err
            raise RuntimeError(msg)

        if err:
            print(err)

        return out, err
