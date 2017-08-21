from .models import *
from gurobipy import Model, quicksum, GRB
from typing import Dict, Optional, Tuple
from random import Random
import logging

class Problem(object):
    random = None  # type: Random
    logger = None  # type: logging.Logger
    model = None  # type: Model
    locations = None  # type: List[Location]
    rider_announcements = None  # type: List[RiderAnnouncement]
    driver_announcements = None  # type: List[DriverAnnouncement]
    matches = None  # type: Dict[Tuple[RiderAnnouncement, DriverAnnouncement], float]

    def __init__(self, random=None, logger=None):
        self.logger = logger or logging.getLogger("ride_sharing.Problem")
        self.random = random or Random()
        self.model = Model("Ride-sharing")

    def _gen_locations(self):
        # Generate a list of random locations to use as the set P
        self.locations = []
        self.logger.info("Location generation complete")

    def _gen_announcements(self):
        """
        Generate sets of rider and driver announcements
        """
        self.rider_announcements = []
        self.driver_announcmenets = []
        self.logger.info("Announcement generation complete")

    def _gen_matches(self):
        # Calculates the cost of each valid match between a rider and a driver
        self.matches = {}
        self.logger.info("Match generation complete")


    def _build_gurobi_model(self):
        """
        Generate the Gurobi model using the already generated locations, 
        announcements, feasible matches, etc.
        """
        self.logger.info("Gurobi model built")

    def callback(self, model, where):
        self.logger.debug("Entering callback")

    def build_model(self):
        self._gen_locations()
        self._gen_announcements()
        self._gen_matches()
        self._build_gurobi_model()

if __name__ = "__main__":
    p.build_model()
    p.model.optimize(p.callback)