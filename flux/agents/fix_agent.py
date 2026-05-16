from flux.fix_engine import FixEngine


class FixAgent:

    def run(self, repo, path, context):
        try:
            return FixEngine.run(path, "")
        except:
            return "no_fix"
