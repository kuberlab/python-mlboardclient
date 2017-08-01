# python-mlboardclient
Python lib for interacting ml-board component.

## Installation

    pip install 'git+https://github.com/kuberlab/python-mlboardclient.git'

## Usage

    from mlboardclient.api import client
    
    # Default url is http://mlboard-v2.kuberlab:8082/api/v2
    ml = client.Client('http://localhost:8082/api/v2')
    apps = ml.apps.list()
    [<mlboardclient.api.v2.apps.App object at 0x7f0b554b5f90>]
    
    app = apps[0]
    # Get tasks from config
    app.tasks
    [<Task name=model build=None status=undefined>]
    
    task = app.tasks[0]
    
    # Run & wait task
    task.run()
    <Task name=model build=4 status=Succeeded>

    # Get tasks from API
    app.get_tasks()
    [<Task name=model build=1 status=Failed>, <Task name=model build=2 status=Failed>, 
    <Task name=model build=3 status=Failed>, <Task name=model build=4 status=Succeeded>]
