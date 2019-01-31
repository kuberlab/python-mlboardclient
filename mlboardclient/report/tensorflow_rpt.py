from tensorflow.python.training import session_run_hook
from tensorflow.python.training import training_util
from tensorflow.python.training.session_run_hook import SessionRunArgs
import tensorflow as tf
from mlboardclient.report.tensorlogs import Report
import numpy as np


def convert(o):
    if isinstance(o, np.int64): return int(o)
    if isinstance(o, np.int32): return int(o)
    if isinstance(o, np.int): return int(o)
    if isinstance(o, np.float32): return float(o)
    if isinstance(o, np.float64): return float(o)
    if isinstance(o, np.float): return float(o)
    if isinstance(o, tf.int64): return int(o)
    if isinstance(o, tf.int32): return int(o)
    if isinstance(o, tf.int): return int(o)
    if isinstance(o, tf.float32): return float(o)
    if isinstance(o, tf.float64): return float(o)
    if isinstance(o, tf.float): return float(o)
    return None

class MlBoardReporter(session_run_hook.SessionRunHook):
    def __init__(self,checkpoint_dir,tensors={},submit_summary=True,max_number_images=1,every_steps=None,every_n_secs=60):
        if every_steps is not None:
            every_n_secs = None
        self._timer = tf.train.SecondOrStepTimer(every_steps=every_steps,every_secs=every_n_secs)
        if submit_summary:
            self._rpt = Report(checkpoint_dir,max_number_images=max_number_images)
        else:
            self._rpt = None
        try:
            from mlboardclient.api import client
        except ImportError:
            tf.logging.warning("Can't find mlboardclient.api")
            client = None
        mlboard = None
        if client:
            mlboard = client.Client()
            try:
                mlboard.apps.get()
            except Exception:
                tf.logging.warning("Can't init mlboard env")
                mlboard = None

        self._mlboard = mlboard
        self._tensors = tensors
        self._most_recent_step = 0

    def begin(self):
        self._next_step = None
        self._global_step_tensor = training_util._get_or_create_global_step_read()  # pylint: disable=protected-access
        if self._global_step_tensor is None:
            raise RuntimeError(
                "Global step should be created to use StepCounterHook.")

    def before_run(self, run_context):  # pylint: disable=unused-argument
        requests = {"global_step": self._global_step_tensor}
        for n,t in self._tensors.items():
            requests[n] = t
        self._generate = (
                self._next_step is None or
                self._timer.should_trigger_for_step(self._next_step))

        return SessionRunArgs(requests)

    def after_run(self, run_context, run_values):
        _ = run_context
        stale_global_step = run_values.results["global_step"]
        global_step = stale_global_step + 1
        if self._next_step is None or self._generate:
            global_step = run_context.session.run(self._global_step_tensor)

        if self._mlboard is not None:
            if self._generate and (self._next_step is not None):
                rpt = {}
                for k,v in run_values.results.items():
                    v = convert(v)
                    if v is not None:
                        rpt[k] = v
                if self._rpt is not None:
                    self._rpt.reload()
                    most_recent_step = self._rpt.most_recent_step()
                    if most_recent_step>self._most_recent_step:
                        rpt['#documents.report.html'] = self._rpt.generate(reload=False)
                        self._most_recent_step = most_recent_step

                if len(rpt)>0:
                    self._mlboard.update_task_info(rpt)
        self._next_step = global_step + 1

