from ride_sharing.problems.base import Problem
from random import Random

def main(argv):
    r = Random(3)
    p = Problem(r)
    p.build_model()
    p.optimize()
    p.solution_summary()

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(level="INFO")
    main(sys.argv)