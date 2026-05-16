import requests
import random
from flux.cloud_nodes import (
    GitHubActionsNode,
    VercelNode,
    RenderNode,
    SupabaseNode
)
from flux.cloud_router import CloudRouter
from flux.github_manager import GitHubManager
from flux.providers_manager import ProvidersManager

class ClusterManager:

    def __init__(self):
        self.nodes = []
        self.providers = ProvidersManager()
        self.github = GitHubManager()
        self.router = CloudRouter()

        self.github_node = GitHubActionsNode(self.github)
        self.vercel_node = VercelNode(self.providers.get_key("Vercel") or "YOUR_VERCEL_TOKEN")
        self.render_node = RenderNode(self.providers.get_key("Render") or "YOUR_RENDER_TOKEN")
        self.supabase_node = SupabaseNode(self.providers.get_key("Supabase") or "YOUR_SUPABASE_KEY")

    def register_node(self, url):
        if url not in self.nodes:
            self.nodes.append(url)

    def get_node(self):
        if not self.nodes:
            return None
        return random.choice(self.nodes)

    def health_check(self):
        alive = []
        for node in self.nodes:
            try:
                # Using /docs or a simple GET to check if it's up
                r = requests.get(f"{node}/docs", timeout=2)
                if r.status_code == 200:
                    alive.append(node)
            except:
                pass
        self.nodes = alive

    def auto_scale(self):
        if len(self.nodes) < 1:
            return "minimal mode"
        if len(self.nodes) > 3:
            return "scaled"
        return "normal"

    def dispatch(self, action, repo, path):
        target = self.router.decide(action)

        # ☁️ cloud routing
        if target == "github_actions":
            return self.github_node.run(repo)

        if target == "vercel":
            return self.vercel_node.deploy(repo)

        if target == "render":
            return self.render_node.deploy(repo)

        if target == "supabase":
            return self.supabase_node.migrate(repo)

        # 💻 fallback local worker
        self.health_check()
        node = self.get_node()

        if not node:
            return "No nodes available"

        try:
            res = requests.post(
                f"{node}/execute",
                json={
                    "action": action,
                    "repo": repo,
                    "path": path
                },
                timeout=15
            )
            return res.json()
        except Exception as e:
            return {"error": str(e)}
