# python-mlboardclient
Python lib for interacting ml-board component.

## Installation

    pip install 'git+https://github.com/kuberlab/python-mlboardclient.git'

## Usage

    from mlboardclient.api import client
    
    ml = client.Client()
    
    apps = ml.apps.list()
    
    # Get app config
    print(apps[0].config)
