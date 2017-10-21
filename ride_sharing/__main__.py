from ride_sharing.problems.base import Problem
from ride_sharing.problems.lazy_stability import LazyStabilityProblem
from ride_sharing.problems.simple_stability import SimpleStabilityProblem
from ride_sharing.problems.parallel_matching import ParallelMatchingProblem
from ride_sharing.problems.epsilon_stability import EpsilonStableProblem
from ride_sharing.problems.iterative_removal import IterativeConstraintRemovalProblem
from random import Random
import os
import click
import time

model_names = {
    'stability': SimpleStabilityProblem,
    'lazy': LazyStabilityProblem,
    'epsilon': EpsilonStableProblem,
    'iterative': IterativeConstraintRemovalProblem,
}

models_option = click.option('--model', '-m', type=click.Choice(list(model_names.keys())), multiple=True, required=True)
seed_option = click.argument('--seed', type=int, default=os.urandom(4))


@click.group(name='ride_sharing', epilog="Tom Manderson & Iain Rudge")
def cli():
    """
    MATH4202 Project: "Stability in Dynamic Ride-Sharing System"
    """
    pass


@cli.command()
@models_option
@seed_option
@click.option('--parallel', 'parallel', flag_value=True, default=True)
@click.option('--single-threaded', 'parallel', flag_value=False)
def test(model, seed, parallel):
    """
    Run the existing test code
    """
    r = Random(seed)
    base_cls = ParallelMatchingProblem if parallel else Problem
    bases = tuple(model_names[name] for name in model) + (base_cls,)
    cls = type('RuntimeClass', bases, {})
    p = cls(r)
    p.build_data()
    p.build_model()
    p.optimize()
    p.solution_summary()


@cli.command()
@click.option('--parallel', 'parallel', flag_value=True, default=True)
@click.option('--single-threaded', 'parallel', flag_value=False)
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
    p = cls()
    p.load_data(filename)
    p.build_model()
    p.optimize()
    p.solution_summary()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level="INFO", format="%(asctime)s | %(message)s")
    cli()
