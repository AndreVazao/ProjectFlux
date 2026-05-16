class CloudRouter:

    def decide(self, action):

        if action == "build":
            return "github_actions"   # grátis

        if action == "deploy_web":
            return "vercel"           # grátis

        if action == "deploy_api":
            return "render"

        if action == "database":
            return "supabase"

        return "local"
