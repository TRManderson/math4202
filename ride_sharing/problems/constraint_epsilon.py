from .base import Problem
from operator import itemgetter


class ConstraintEpsilonProblem(Problem):
    STABILITY_EPSILON = 10

    def _stability_filter(self, savings, person, items):
        i = iter(items)
        while True:
            s, p = next(i)
            if s < savings + self.STABILITY_EPSILON:
                continue
            elif p == person:
                continue
            else:
                yield p