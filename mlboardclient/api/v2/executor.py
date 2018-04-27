# import eventlet
import logging
import threading
import time

from six.moves import queue

from mlboardclient.api import base


LOG = logging.getLogger(__name__)
# eventlet.monkey_patch(
#     thread=True,
#     time=True
# )


class TaskExecutor(object):
    def __init__(self, task_manager, max_parallel, callback=None):
        self.max_parallel = max_parallel
        self.manager = task_manager
        self.callback = callback

        self.event = threading.Event()
        self.reset()
        # self._spawn_threads()

    def _spawn_threads(self):
        self.event.clear()

        # self._queue_thread = eventlet.spawn(self._start_queue)
        self._queue_thread = threading.Thread(target=self._start_queue)
        self._queue_thread.start()
        # self._check_thread = eventlet.spawn(self._check)
        self._check_thread = threading.Thread(target=self._check)
        self._check_thread.start()
        self._spawned = True

    def put(self, task):
        if self._failed:
            if self._msg:
                raise RuntimeError(self._msg)

            raise RuntimeError('Executor has been failed.')

        self.queue.put(task)

        if not self._spawned:
            self._spawn_threads()

    def error(self):
        if not self._failed:
            return False

        if self._msg:
            return self._msg

        return self._failed

    def is_full(self):
        return self.queue.unfinished_tasks >= self.max_parallel

    def _start_queue(self):
        while not self.event.isSet() or self.queue.unfinished_tasks:
            if len(self._running_tasks) >= self.max_parallel:
                time.sleep(1)
                continue

            try:
                task = self.queue.get(block=False)
                task.start()
            except queue.Empty:
                time.sleep(0.02)
                continue
            except base.APIException as e:
                self.event.set()
                while self.queue.unfinished_tasks:
                    self.queue.task_done()
                self._msg = str(e)
                self._failed = True
                return

            LOG.info('Started task %s' % self._task_key(task))

            self._running_tasks[self._task_key(task)] = task

    @staticmethod
    def _task_key(task):
        return '%s:%s' % (task.name, task.build)

    def _check(self):
        # Check running tasks
        while not self.event.isSet() or self.queue.unfinished_tasks:
            for k in list(self._running_tasks):
                task = self._running_tasks[k]
                task.refresh()
                if task.completed:
                    if self.callback:
                        try:
                            self.callback(task)
                        except Exception as e:
                            msg = "Callback failed: %s" % str(e.message)
                            LOG.error(msg)
                            LOG.error("Exit executor...")
                            self.event.set()
                            while self.queue.unfinished_tasks:
                                self.queue.task_done()
                            self._msg = msg
                            self._failed = True
                            return
                    LOG.info(
                        'Completed task %s with status=%s' %
                        (self._task_key(task), task.status)
                    )
                    self.queue.task_done()
                    self._running_tasks.pop(k)

            time.sleep(5)

    def wait(self, timeout=None):
        try:
            self.event.set()
            self.queue.join()
            self._queue_thread.join()
            self._check_thread.join()
        except KeyboardInterrupt:
            return
        finally:
            self.reset()

    def reset(self):
        self._check_thread = None
        self._queue_thread = None
        self.queue = queue.Queue()
        self._running_tasks = {}
        self.event.clear()
        self._spawned = False
        self._failed = False
