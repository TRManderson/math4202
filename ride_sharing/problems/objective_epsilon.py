from gurobipy import quicksum, GRB
from .base import Problem
import itertools


class StabilityPricingProblem(Problem):
    def _build_gurobi_model(self):
        self.force_arc = {
            (rider, driver): self.model.addVar(vtype=GRB.BINARY)
            for (rider, driver) in self.matches
        }
        super()._build_gurobi_model()
        self.logger.info("Solving with stability epsilon of {}".format(self.STABILITY_EPSILON))

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
        return rider_pref + driver_pref + var >= 1 - self.force_arc[(rider, driver)]


class ObjectiveEpsilonProblem(StabilityPricingProblem):
    """
    Whether or not to use stability constraints is priced into objective
    """
    STABILITY_EPSILON = 5

    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        self.model.setObjective(
            self.total_savings - self.STABILITY_EPSILON*quicksum(self.force_arc.values()),
            sense=GRB.MAXIMIZE
        )


class PaperObjectiveStabilityProblem(StabilityPricingProblem):
    """
    Objective is to maximise applied stability constraints
    """
    STABILITY_EPSILON = None

    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        self.model.setObjective(quicksum(self.force_arc.values()), sense=GRB.MINIMIZE)


class DynamicStabilityPricingProblem(StabilityPricingProblem):
    """
    Whether or not to use stability constraints is priced into objective and dependent on arc costs
    """
    STABILITY_EPSILON = 0.1

    def _value_stability_var(self, arc, var):
        return self.matches[arc]*var * self.STABILITY_EPSILON

    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        self.model.setObjective(self.total_savings - quicksum(
            itertools.starmap(self._value_stability_var, self.force_arc.items())
        ), sense=GRB.MAXIMIZE)
