import logging

from bayes_opt import bayesian_optimization as bayes


LOG = logging.getLogger(__name__)


class ParamSpecBuilder(object):
    spec = None
    default_bounds = [-10, 10]
    default_type = float
    _last_param = None
    _last_resource = None

    def param(self, name):
        if not self._last_resource:
            raise RuntimeError('First must call resource()!')

        if not self.spec[self._last_resource].get(name):
            self.spec[self._last_resource][name] = {
                'type': self.default_type,
                'bounds': self.default_bounds
            }
        self._last_param = name
        return self

    def resource(self, name):
        if self.spec is None:
            self.spec = {}

        if not self.spec.get(name):
            self.spec[name] = {}
        self._last_resource = name
        return self

    def float(self):
        if not self._last_param:
            raise RuntimeError('First must call param()!')

        self.spec[self._last_resource][self._last_param]['type'] = float
        return self

    def int(self):
        if not self._last_param:
            raise RuntimeError('First must call param()!')

        self.spec[self._last_resource][self._last_param]['type'] = int
        return self

    def bounds(self, min, max):
        if not self._last_param:
            raise RuntimeError('First must call param()!')

        self.spec[self._last_resource][self._last_param]['bounds'] = (min, max)
        return self

    def build(self):
        return self.spec


class Optimizator(object):
    def __init__(self, base_task, target_parameter, param_spec,
                 iterations=10, init_steps=5):
        """Helper for optimize hyper parameters.

        :param base_task: task which parameters to optimize.
        :type base_task: mlboardclient.api.v2.tasks.Task
        :param target_parameter: task-specific parameter to optimize.
          It must be exposed by task in exec_info property
          (via update_task_info() func)
        :param param_spec: Task arguments including their type
          and bounds which will be changed in each task run. Format:

          {
            'my_resource': {
              'param1': {'type': float, 'bounds': (-5, 10)},
              'param2': {'type': int, 'bounds': (-10, 20)}
            }
          }
        """
        self.iterations = iterations
        self.init_steps = init_steps
        # Process param spec.
        self.spec = param_spec
        self.target_parameter = target_parameter
        self.base = base_task.copy()
        # self.executor = executor.TaskExecutor(self.base.manager, 1)
        bayes_spec = {}

        res_keys = list(self.spec.keys())
        if not res_keys:
            raise RuntimeError('Specify at least 1 resource in param_spec!')

        self._resource = res_keys[0]
        for k in self.spec[self._resource]:
            bayes_spec[k] = self.spec[self._resource][k]['bounds']

        self.bo = bayes.BayesianOptimization(self._target_func(), bayes_spec)

    def _target_func(self):
        # Generate target func from spec.
        def target(**params):
            t = self.base.copy()
            res_args = t.resource(self._resource).get('args', {})
            
            # Explicit params type casting.
            for k in self.spec[self._resource]:
                _type = self.spec[self._resource][k]['type']
                if k in params:
                    params[k] = _type(params[k])
            
            res_args.update(dict(**params))
            t.resource(self._resource)['args'] = res_args

            # self.executor.put(t)
            # self.executor.wait()
            t.start()
            t.wait()

            if t.status != 'Succeeded':
                msg = 'Task completed with status %s.' % t.status
                LOG.error(msg)
                LOG.error('logs:')
                logs = t.logs()
                for k in logs:
                    print('=' * 53)
                    print('logs of pod %s' % k)
                    print('=' * 53)
                    print(logs[k])
                    print('')

                raise RuntimeError(msg)

            if not t.exec_info:
                raise RuntimeError(
                    'Task must expose variables via '
                    'mlboardclient.api.client.Client().update_task_info()'
                    ' in exec_info property!'
                )

            return t.exec_info.get(self.target_parameter)

        return target

    def run(self):
        self.bo.maximize(init_points=self.init_steps, n_iter=self.iterations)

        return self.bo.res
