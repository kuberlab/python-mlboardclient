
class MlboardContext(object):
    def __init__(self,
                 workspace_id=None,
                 workspace=None,
                 project_name=None,
                 app_id=None,
                 kuberlab_api_url=None):
        self.workspace_id = workspace_id
        self.workspace = workspace
        self.project_name = project_name
        self.app_id = app_id
        self.kuberlab_api_url = kuberlab_api_url
