class CEOEngine:

    def decide(self, metrics):

        decisions = []

        for project, runs in metrics.items():

            success = sum(1 for r in runs if "executed" in r)

            if success > 2:
                decisions.append((project, "scale"))

            elif success == 0:
                decisions.append((project, "kill"))

            else:
                decisions.append((project, "improve"))

        return decisions
