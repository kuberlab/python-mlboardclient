import json

from mlboardclient.api import client

m = client.Client('http://localhost:8082/api/v2')
app = m.apps.get('11-tfexample')
task = app.task('model')

task.resource('worker')['args'] = {'common': 'yes'}


def args(num):
    for i in range(num):
        def f(t):
            t.resource('worker')['args']['arg'] = i

        yield f


logs = task.parallel_run(3, args(7))
print(json.dumps(list(logs), indent=2))
