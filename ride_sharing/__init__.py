from .problems.base import Problem

if __name__ = "__main__":
    p.build_model()
    p.model.optimize(p.callback)
