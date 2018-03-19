import json

from mlboardclient.api import client
from mlboardclient.api.v2 import optimizator

m = client.Client('http://localhost:8082/api/v2')
app = m.apps.get('11-tfexample')
task = app.task('model')


# task.resource('worker')['args'] = {'common': 'yes'}
spec = optimizator.ParamSpecBuilder().resource(
    'worker').param('argument').bounds(-2, 10).build()


print('Run with param spec = %s' % spec)
result = task.optimize('checked_value', spec, 5)

print(json.dumps(result, indent=2))
