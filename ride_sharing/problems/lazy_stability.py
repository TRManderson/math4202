from .base import Problem
from gurobipy import CallbackClass, Model, quicksum


class ULazyStabilityProblem(Problem):
    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        self.model.setParam('LazyConstraints', 1)

    def _cb_arcs_solutions(self, model: Model):
        keys = self.variables.keys()
        vals = self.variables.values()
        return zip(keys, vals, model.cbGetSolution(vals))

    def callback(self, model, where):
        if where != CallbackClass.MIPSOL:
            return
        for arc, var, val in self._cb_arcs_solutions(model):
            if val > 1.0 - self.EPSILON:
                continue
            model.cbLazy(self._stability_constraint_for(*arc, var))


class LLazyStabilityProblem(Problem):
    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        self.model.setParam('LazyConstraints', 1)

    def _cb_arcs_solutions(self, model: Model):
        keys = self.variables.keys()
        vals = self.variables.values()
        return zip(keys, vals, model.cbGetSolution(vals))

    def callback(self, model, where):
        if where != CallbackClass.MIPSOL:
            return
        for arc, var, val in self._cb_arcs_solutions(model):
            if val < self.EPSILON:
                continue
            model.cbLazy(self._stability_constraint_for(*arc, var))
