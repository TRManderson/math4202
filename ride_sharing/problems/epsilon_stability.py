from .base import Problem
from operator import itemgetter

class EpsilonStableProblem(Problem):
    STABILITY_EPSILON = 5

    def _stability_filter(self, savings, person, items):
        i = iter(items)
        while True:
            s, p = next(i)
            if s < savings + self.STABILITY_EPSILON:
                continue
        yield from map(itemgetter(1), i)