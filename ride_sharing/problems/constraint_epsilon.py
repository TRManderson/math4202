from .base import Problem


class ConstraintEpsilonProblem(Problem):
    """
    Stability constraints relaxed to allow any solutions within selected epsilon
    """
    STABILITY_EPSILON = 5

    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        self.logger.info("Solving with stability epsilon of {}".format(self.STABILITY_EPSILON))

    def _stability_filter(self, savings, person, items):
        i = iter(items)
        while True:
            s, p = next(i)
            if s + self.STABILITY_EPSILON < savings:
                continue
            elif s == savings:
                if p == person:
                    continue
                yield p
            else:
                yield p
