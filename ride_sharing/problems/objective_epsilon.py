from gurobipy import quicksum, GRB
from .base import Problem
import itertools


class StabilityPricingProblem(Problem):

    def _build_gurobi_model(self):
        self.force_arc = {}
        super()._build_gurobi_model()

    def _stability_constraint_for(self, rider, driver, var):
        match_savings = self.matches[(rider, driver)]
        rider_pref = quicksum(
            self.variables[(rider, driver_preferred)]
            for driver_preferred in
            self._stability_filter(match_savings, driver, self.rider_preferences[rider])
        )
        driver_pref = quicksum(
            self.variables[(rider_preferred, driver)]
            for rider_preferred in
            self._stability_filter(match_savings, rider, self.driver_preferences[driver])
        )
        constr_var = self.force_arc[(rider, driver)] = self.model.addVar(vtype=GRB.BINARY)
        return rider_pref + driver_pref + var >= constr_var


class ObjectiveEpsilonProblem(StabilityPricingProblem):
    STABILITY_EPSILON = 5

    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        obj = self.model.getObjective()
        self.model.setObjective(obj - self.PRICE_OF_STABILITY * quicksum(self.force_arc.values()))


class DynamicStabilityPricingProblem(Problem):
    def _value_stability_var(self, arc, val):
        return self.matches[arc]*val/4

    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        obj = self.model.getObjective()
        self.model.setObjective(obj - quicksum(
            itertools.starmap(self._value_stability_var, self.force_arc.items())
        ))
