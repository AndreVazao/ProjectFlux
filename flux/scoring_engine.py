class ScoringEngine:

    def score(self, idea):
        score = 0

        if idea["type"] == "python":
            score += 2
        if idea["type"] == "api":
            score += 3
        if idea["type"] == "apk":
            score += 1

        return score

    def rank(self, ideas):
        return sorted(ideas, key=self.score, reverse=True)
