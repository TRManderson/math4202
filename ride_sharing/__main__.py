from ride_sharing.problems.lazy_stability import LazyStabilityProblem
from ride_sharing.problems.simple_stability import SimpleStabilityProblem
from ride_sharing.problems.parallel_matching import ParallelMatchingProblem
from ride_sharing.problems.epsilon_stability import EpsilonStableProblem
from random import Random

def main(argv):
    r = Random()
    p = type('BSType', (ParallelMatchingProblem, SimpleStabilityProblem), {})(r)
    p.build_model()
    p.optimize()
    p.solution_summary()

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(level="INFO", format="%(asctime)s | %(message)s")
    main(sys.argv)