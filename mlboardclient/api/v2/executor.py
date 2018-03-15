import logging
# import eventlet
import threading
import time

from six.moves import queue


LOG = logging.getLogger(__name__)
# eventlet.monkey_patch(
#     thread=True,
#     time=True
# )


class TaskExecutor(object):
    def __init__(self, task_manager, max_parallel):
        self.max_parallel = max_parallel
        self.manager = task_manager
        self.queue = queue.Queue()

        self.event = threading.Event()
        self._running_tasks = {}

        # self._queue_thread = eventlet.spawn(self._start_queue)
        self._queue_thread = threading.Thread(target=self._start_queue)
        self._queue_thread.start()
        # self._check_thread = eventlet.spawn(self._check)
        self._check_thread = threading.Thread(target=self._check)
        self._check_thread.start()

    def put(self, task):
        self.queue.put(task)

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

            LOG.info('Started task %s', self._task_key(task))

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
            self._queue_thread.join(timeout)
            self._check_thread.join(timeout)
        except KeyboardInterrupt:
            return
