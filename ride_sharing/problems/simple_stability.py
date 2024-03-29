from .base import Problem


class SimpleStabilityProblem(Problem):
    """
    Simple implementation with stability constraints implemented as per the paper
    """
    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        stab = self.constraints['stability'] = {}
        for arc, var in self.variables.items():
            stab[arc] = self.model.addConstr(self._stability_constraint_for(*arc, var))
