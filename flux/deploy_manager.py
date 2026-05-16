import requests
import os


class DeployManager:

    def __init__(self, providers):
        self.providers = providers

    # -------------------------
    # VERCEL DEPLOY
    # -------------------------

    def deploy_vercel(self, repo_name):
        token = self.providers.get_key("Vercel")
        if not token:
            return "❌ No Vercel token"

        url = "https://api.vercel.com/v13/deployments"

        data = {
            "name": repo_name,
            "gitSource": {
                "type": "github",
                "repo": repo_name
            }
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.post(url, json=data, headers=headers)

        if r.status_code in [200, 201]:
            return "✅ Vercel deploy started"
        return f"❌ {r.text}"

    # -------------------------
    # RENDER DEPLOY
    # -------------------------

    def deploy_render(self, service_id):
        token = self.providers.get_key("Render")
        if not token:
            return "❌ No Render token"

        url = f"https://api.render.com/v1/services/{service_id}/deploys"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        r = requests.post(url, headers=headers)

        if r.status_code == 201:
            return "✅ Render deploy started"
        return f"❌ {r.text}"

    # -------------------------
    # SUPABASE (placeholder)
    # -------------------------

    def deploy_supabase(self):
        token = self.providers.get_key("Supabase")
        if not token:
            return "❌ No Supabase token"

        return "⚠️ Supabase deploy needs CLI integration (next step)"

    def auto_deploy_smart(self, repo_name, repo_path):
        from flux.auto_engine import AutoEngine

        project_type = AutoEngine.detect_project_type(repo_path)
        provider = AutoEngine.choose_provider(project_type)

        if not provider:
            return "❌ Could not detect project type"

        if provider == "Vercel":
            return self.deploy_vercel(repo_name)

        if provider == "Render":
            return "⚠️ Render needs service_id. Use manual deploy for now."

        if provider == "GitHub":
            return "⚙️ APK build handled via GitHub Actions"

        return "❌ Unknown path"

    def deploy_render_ui(self, service_id):
        return self.deploy_render(service_id)
