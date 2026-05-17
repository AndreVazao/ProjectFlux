from flux.deploy_manager import DeployManager
from flux.providers import ProviderManager


class DeployAgent:

    def __init__(self):
        self.providers = ProviderManager()
        self.deploy = DeployManager(self.providers)

    def run(self, repo, path):
        try:
            return self.deploy.auto_deploy_smart(repo, path)
        except:
            return "no_deploy"
