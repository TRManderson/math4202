from gurobipy import GRB
from .base import Problem

class IterativeConstraintRemovalProblem(Problem):
    def optimize(self):
        super().optimize()
        while self.model.Status == GRB.INFEASIBLE:
            self.model.computeIIS()
            remove_constrs = []
            for arc, constr in self.constraints['stability'].items():
                if constr.IISConstr:
                    remove_constrs.append(arc)
            for arc in remove_constrs:
                self.model.remove(self.constraints['stability'].pop(arc))
            super().optimize()