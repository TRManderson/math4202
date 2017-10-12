from .base import Problem
from operator import itemgetter

class EpsilonStableProblem(Problem):
    STABILITY_EPSILON = 10

    def _stability_filter(self, savings, person, items):
        i = iter(items)
        while True:
            s, p = next(i)
            if s < savings:
                continue
            elif s == savings:
                if p != person:
                    yield p
                    self.logger.debug("Found tie: {} == {}".format(person, p))
            else:
                break
        yield from map(itemgetter(1), i)
