import json
import logging
import time

from mlboardclient.api import client


LOG = logging.getLogger(__name__)

m = client.Client('http://localhost:8082/api/v2')
app = m.apps.get('11-tfexample')
task = app.task('model')

task.resource('worker')['args'] = {'common': 'yes'}


def generate_tasks(num):
    tasks = []
    for i in range(num):
        t_copy = task.copy()
        t_copy.resource('worker')['args']['arg'] = i

        tasks.append(t_copy)
    return tasks


tasks = generate_tasks(5)
executor = m.tasks.new_executor(3)

# Spawn tasks
for t in tasks:
    executor.put(t)


more_tasks = generate_tasks(3)
spawned_more = False

# Check completed and checkout logs
while len(tasks) > 0:
    for t in tasks:
        if not t.completed:
            continue

        LOG.info('Task %s:%s logs:' % (t.name, t.build))

        logs = t.logs()
        worker_logs = [log for k, log in logs.items() if 'worker' in k]

        print(json.dumps(worker_logs, indent=2))
        tasks.remove(t)

        # if not spawned_more:
        #     # Spawn more tasks
        #     LOG.info('Spawn more tasks')
        #     for tsk in more_tasks:
        #         executor.put(tsk)
        #         tasks.append(tsk)
        #
        #     spawned_more = True

        break

    time.sleep(1)

executor.wait()

# Spawn more tasks
LOG.info('Spawn more tasks')
for tsk in more_tasks:
    executor.put(tsk)
    tasks.append(tsk)

executor.wait()
# print(json.dumps(list(logs), indent=2))
