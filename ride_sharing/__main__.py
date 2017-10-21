from ride_sharing.problems.base import Problem
from ride_sharing.problems.lazy_stability import LazyStabilityProblem
from ride_sharing.problems.simple_stability import SimpleStabilityProblem
from ride_sharing.problems.parallel_matching import ParallelMatchingProblem
from ride_sharing.problems.epsilon_stability import EpsilonStableProblem
from ride_sharing.problems.iterative_removal import IterativeConstraintRemovalProblem
from random import Random

import time

def main(argv):
    seed = 37
    r = Random(seed)
    p = ParallelMatchingProblem(r)
    # p.STABILITY_EPSILON = 100
    p.build_data()
    p.save_data("l{loc}xy{xy}a{a}t{t}s{seed}.pickle".format(
        loc=p.LOCATION_COUNT,
        seed=seed,
        xy=p.MAX_XY,
        a=p.ANNOUNCEMENT_COUNT,
        t=p.MAX_TIME,
    ))

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(level="INFO", format="%(asctime)s | %(message)s")
    main(sys.argv)