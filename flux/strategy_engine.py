class StrategyEngine:

    def decide(self, learning_data):
        # prioridade global

        priorities = []

        for repo, actions in learning_data.items():
            for action, stats in actions.items():

                success = stats["success"]
                fail = stats["fail"]

                if fail > success:
                    priorities.append((repo, "fix"))

                elif success > fail:
                    priorities.append((repo, "deploy"))

                else:
                    priorities.append((repo, "evolve"))

        return priorities
