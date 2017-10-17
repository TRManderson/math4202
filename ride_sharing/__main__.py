from ride_sharing.problems.base import Problem
from ride_sharing.problems.lazy_stability import LazyStabilityProblem
from ride_sharing.problems.simple_stability import SimpleStabilityProblem
from ride_sharing.problems.parallel_matching import ParallelMatchingProblem
from ride_sharing.problems.epsilon_stability import EpsilonStableProblem
from ride_sharing.problems.iterative_removal import IterativeConstraintRemovalProblem
from random import Random

import time

def main(argv):
    r = Random(3)
    p = type('BS', (ParallelMatchingProblem, LazyStabilityProblem), {})(r)
    # p.STABILITY_EPSILON = 100
    p.build_model()
    t1 = time.time()
    p.optimize()
    t2 = time.time()
    p.logger.info("Optimising took {}s".format(t2-t1))
    p.solution_summary()

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(level="INFO", format="%(asctime)s | %(message)s")
    main(sys.argv)