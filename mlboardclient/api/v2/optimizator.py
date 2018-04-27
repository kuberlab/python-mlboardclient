import collections
import importlib
import json
import logging
import time

from bayes_opt import bayesian_optimization as bayes

from mlboardclient.api.v2 import executor


LOG = logging.getLogger(__name__)
try:
    skopt = importlib.import_module('skopt')
    space = importlib.import_module('skopt.space')
except ImportError as e:
    LOG.warning(e)
    skopt = None
    space = None

PARAM_SEPARATOR = '|'


def param_name(resource, name):
    return '%s%s%s' % (resource, PARAM_SEPARATOR, name)


def resource_param(param):
    splitted = param.split(PARAM_SEPARATOR)
    return splitted[0], splitted[1]


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


# import math
# def f(x):
#     return math.exp(-(x - 2)**2) + math.exp(-(x - 6)**2/10) + 1 / (x**2 + 1)


class SkoptOptimizator(object):
    """Dummy example:

    >>> def optimize():
    ...   opt = skopt.Optimizer([(-2.0, 10.0)], n_initial_points=5)
    ...   for i in range(0, 15):
    ...     x = opt.ask()
    ...     y = f(x[0])
    ...     t = opt.tell(x, -y)
    ...   print t
    ...   print t.fun
    """

    def __init__(self, base_task, target_parameter, param_spec,
                 iterations=10, init_steps=5,
                 direction='maximize', max_parallel=3):
        self.iterations = iterations
        self.init_steps = init_steps
        # Process param spec.
        self.spec = param_spec
        self.target_parameter = target_parameter
        self.base = base_task.copy()
        self.executor = executor.TaskExecutor(
            self.base.manager,
            max_parallel,
            callback=self._callback_func()
        )
        skopt_spec = []

        # Bayes Opt may only be used for minimize so
        # positive direction is minimize.
        if direction == 'maximize':
            self.sign = -1
        elif direction == 'minimize':
            self.sign = 1
        else:
            RuntimeError('Supported directions only (minimize, maximize)')

        res_keys = list(self.spec.keys())
        if not res_keys:
            raise RuntimeError('Specify at least 1 resource in param_spec!')

        for res in res_keys:
            for k in self.spec[res]:
                if self.spec[res][k]['type'] is float:
                    skopt_spec += [
                        space.Real(
                            self.spec[res][k]['bounds'][0],
                            self.spec[res][k]['bounds'][1],
                            name=param_name(res, k),
                        )
                    ]
                elif self.spec[res][k]['type'] is int:
                    skopt_spec += [
                        space.Integer(
                            self.spec[res][k]['bounds'][0],
                            self.spec[res][k]['bounds'][1],
                            name=param_name(res, k),
                        )
                    ]

        self.last_result = None
        self.best_val = None
        self.best_task = None
        self.space = skopt_spec
        self.target = self._target_func()
        self.opt = skopt.Optimizer(skopt_spec, n_initial_points=init_steps)

    def _target_func(self):
        # Generate target func from spec.
        def target(params_dict):
            t = self.base.copy()

            comment = []

            for param in list(params_dict.keys()):
                res, arg = resource_param(param)
                _type = self.spec[res][arg]['type']
                params_dict[param] = _type(params_dict[param])

                res_args = t.resource(res).get('args', {})
                res_args.update({arg: params_dict[param]})
                t.resource(res)['args'] = res_args

                comment.append('%s=%s' % (arg, params_dict[param]))

            t.config['exec_comment'] = 'Params: ' + '; '.join(comment)
            t._current_args = list(params_dict.values())

            self.executor.put(t)

        return target

    def _callback_func(self):
        def callback(t):
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

            # res = f(*t._current_args)
            # t.update_task_info({'checked_value': float(res)})
            if not t.exec_info:
                raise RuntimeError(
                    'Task must expose variables via '
                    'mlboardclient.api.client.Client().update_task_info()'
                    ' in exec_info property!'
                )

            output = t.exec_info.get(self.target_parameter)
            self.last_result = self.opt.tell(
                t._current_args, output * self.sign
            )
            if ((self.best_val is None) or
                    (output * self.sign < self.best_val * self.sign)):
                self.best_val = output
                self.best_task = t
                kwargs = self._get_named_args(t._current_args)
                LOG.info(
                    'The best value so far: %.6f \nThe best parameters are: %s'
                    % (self.best_val, json.dumps(kwargs))
                )
        return callback

    def _get_named_args(self, args):
        kwargs = collections.OrderedDict()
        for i, arg in enumerate(args):
            kwargs[self.space[i].name] = arg

        return kwargs

    def run(self):
        # All steps in 1
        steps = self.init_steps + self.iterations
        step = 0
        while step < steps:
            if self.executor.error():
                raise RuntimeError('Failed: %s' % self.executor.error())

            if self.executor.is_full():
                time.sleep(3)
                continue

            args = self.opt.ask()
            params = self._get_named_args(args)

            # Target put task to executor and runs it.
            self.target(params)
            step += 1

        self.executor.wait()

        if self.last_result:
            self.last_result.fun *= self.sign

        return {
            'best': self.best_task,
            'best_val': self.last_result.fun,
            'opt_output': self.last_result
        }


class Optimizator(object):
    def __init__(self, base_task, target_parameter, param_spec,
                 iterations=10, init_steps=5, direction='maximize'):
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

        # Bayes Opt may only be used for maximize so
        # positive direction is maximize.
        if direction == 'maximize':
            self.sign = 1
        elif direction == 'minimize':
            self.sign = -1
        else:
            RuntimeError('Supported directions only (minimize, maximize)')

        # Process param spec.
        self.spec = param_spec
        self.target_parameter = target_parameter
        self.base = base_task.copy()
        self.best_task = None
        self.best_val = None
        # self.executor = executor.TaskExecutor(self.base.manager, 1)
        bayes_spec = {}

        res_keys = list(self.spec.keys())
        if not res_keys:
            raise RuntimeError('Specify at least 1 resource in param_spec!')

        for res in res_keys:
            for k in self.spec[res]:
                bayes_spec[param_name(res, k)] = self.spec[res][k]['bounds']

        self.bo = bayes.BayesianOptimization(self._target_func(), bayes_spec)

    def _target_func(self):
        # Generate target func from spec.
        def target(**params_dict):
            t = self.base.copy()

            comment = []

            for param in list(params_dict.keys()):
                res, arg = resource_param(param)
                _type = self.spec[res][arg]['type']
                params_dict[param] = _type(params_dict[param])

                res_args = t.resource(res).get('args', {})
                res_args.update({arg: params_dict[param]})
                t.resource(res)['args'] = res_args

                comment.append('%s=%s' % (arg, params_dict[param]))

            t.config['exec_comment'] = 'Params: ' + '; '.join(comment)
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

            # res = f(*list(params_dict.values()))
            # t.update_task_info({'checked_value': float(res)})

            if not t.exec_info:
                raise RuntimeError(
                    'Task must expose variables via '
                    'mlboardclient.api.client.Client().update_task_info()'
                    ' in exec_info property!'
                )
            result_val = t.exec_info.get(self.target_parameter)

            if ((self.best_val is None) or
                    (result_val * self.sign > self.best_val * self.sign)):
                self.best_val = result_val
                self.best_task = t

            return result_val * self.sign

        return target

    def run(self):
        self.bo.maximize(init_points=self.init_steps, n_iter=self.iterations)
        return {
            'best': self.best_task,
            'best_val': self.best_val,
            'opt_output': self.bo.res
        }
