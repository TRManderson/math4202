from ride_sharing.problems.base import Problem
from ride_sharing.problems.lazy_stability import LazyStabilityProblem
from ride_sharing.problems.simple_stability import SimpleStabilityProblem
from ride_sharing.problems.parallel_matching import ParallelMatchingProblem
from ride_sharing.problems.constraint_epsilon import ConstraintEpsilonProblem
from ride_sharing.problems.objective_epsilon import ObjectiveEpsilonProblem, DynamicStabilityPricingProblem, PaperObjectiveStabilityProblem
from ride_sharing.util import compose
from random import Random
import os
import click


model_names = {
    'system': Problem,
    'simple': SimpleStabilityProblem,
    'lazy': LazyStabilityProblem,
    'c_epsilon': ConstraintEpsilonProblem,
    'o_epsilon': ObjectiveEpsilonProblem,
    'paper_objective': PaperObjectiveStabilityProblem,
    'dynamic': DynamicStabilityPricingProblem
}
model_descs = {
    'system': "Solve to system optimal",
    "simple": "Standard stable solution",
    "lazy": "Apply stability to unselected arcs lazily",
    "c_epsilon": "Constraint-based epsilon-stability",
    "o_epsilon": "Objective-based epsilon-stability",
    "paper_objective": "The paper's objective-based epsilon-stability",
    "dynamic": "Objective-dependent constraint pricing"
}

def gen_help():
    res = []
    for name, desc in model_descs.items():
        res.append("{}: {}".format(name, desc))
    return "\n".join(res)

models_option = click.option('--model', '-m', type=click.Choice(list(model_names.keys())), multiple=True, required=True, help=gen_help())
seed_option = click.option('--seed', type=int, default=int.from_bytes(os.urandom(4), byteorder='big'))
parallel_option = compose(
    click.option('--parallel', 'parallel', flag_value=True, default=True, help="Perform arc generation in parallel (on by default)"),
    click.option('--single-threaded', 'parallel', flag_value=False, help="Perform arc generation in only one thread"),
)


@click.group(name='ride_sharing', epilog="Tom Manderson & Iain Rudge")
def cli():
    """
    MATH4202 Project: "Stability in Dynamic Ride-Sharing System"
    """
    pass


@cli.command()
@parallel_option
@seed_option
@models_option
def test(model, seed, parallel):
    """
    Run the existing test code
    """
    r = Random(seed)
    base_cls = ParallelMatchingProblem if parallel else Problem
    bases = tuple(model_names[name] for name in model) + (base_cls,)
    cls = type('RuntimeClass', bases, {})
    print([c.__name__ for c in cls.mro()[1:-1]])
    p = cls(r)
    p.build_data()
    p.build_model()
    p.optimize()
    p.solution_summary()


@cli.command()
@parallel_option
@seed_option
@click.argument('filename')
def build_data(filename, seed, parallel):
    """
    Build model data and save to a file
    """
    r = Random(seed)
    cls = ParallelMatchingProblem if parallel else Problem
    p = cls(r)
    p.build_data()
    p.save_data(filename)


@cli.command()
@models_option
@click.argument('filename')
def from_data(filename, model):
    """
    Attempt a solve from a file
    """
    bases = tuple(model_names[name] for name in model)
    cls = type('RuntimeClass', bases, {})
    print([c.__name__ for c in cls.mro()[1:-1]])
    p = cls()
    p.load_data(filename)
    p.build_model()
    p.optimize()
    p.solution_summary()

def main():
    import logging
    logging.basicConfig(level="INFO", format="%(asctime)s | %(message)s")
    cli()

if __name__ == "__main__":
    main()
