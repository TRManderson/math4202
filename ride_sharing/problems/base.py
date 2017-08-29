from ..models import *
from gurobipy import Model, quicksum, GRB, Constr, Var
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
    constraints = None  # type: Dict[str, Constr]
    variables = None  # type: Dict[Tuple[RiderAnnouncement, DriverAnnouncement], Var]

    LOCATION_COUNT = 200
    MIN_XY = 0
    MAX_XY = 2000
    ANNOUNCEMENT_COUNT = 200
    FLEXIBILITY = 20
    MIN_PER_KM = 1.2
    MAX_TIME = 2000

    def __init__(self, random=None, logger=None):
        self.logger = logger or logging.getLogger("ride_sharing.Problem")
        self.random = random or Random()
        self.model = Model("Ride-sharing")

    def _gen_locations(self):
        # Generate a list of random locations to use as the set P
        self.logger.info("Beginning location generation")
        gen = lambda: self.random.uniform(MIN_XY, MAX_XY)
        self.locations = [Location(gen(), gen()) for _ in range(LOCATION_COUNT)]
        self.distances_cache = {}
        self.logger.info("Location generation complete")

    def distance_between(self, loc1, loc2):
        if (loc1, loc2) not in self.distances_cache:
            self.distances_cache[loc1, loc2] = loc1.distance_to(loc2)
            self.distances_cache[loc2, loc1] = self.distances_cache[loc1, loc2]
        return self.distances_cache[loc1, loc2]

    def _gen_announcements(self):
        """
        Generate sets of rider and driver announcements
        """
        self.logger.info("Generating announcements")
        self.rider_announcements = []
        self.driver_announcements = []
        for _ in range(self.ANNOUNCEMENT_COUNT):
            if self.random.randint(0, 1):
                ls = self.rider_announcements
                cls = RiderAnnouncement
            else:
                ls = self.driver_announcements
                cls = DriverAnnouncement
            start_loc = self.random.choice(self.locations)
            end_loc = self.random.choice(self.locations)
            dist = self.distance_between(start_loc, end_loc)
            while True:
                start_time = self.random.uniform(0, self.MAX_TIME)
                end_time = start_time + dist*self.MIN_PER_KM + self.FLEXIBILITY
                if end_time < MAX_TIME:
                    ls.append(cls(
                        origin=start_loc,
                        dest=end_loc,
                        depart=start_time,
                        arrive=end_time
                    ))
                    break


    def _gen_matches(self):
        # Calculates the cost of each valid match between a rider and a driver
        self.logger.info("Generating valid pairings")
        self.matches = {}
        

    def _build_gurobi_model(self):
        """
        Generate the Gurobi model using the already generated locations, 
        announcements, feasible matches, etc.
        """
        self.logger.info("Building Gurobi model")
        self.constraints = {}
        self.variables = {}

    def callback(self, model, where):
        self.logger.debug("Entering callback")

    def build_model(self):
        self._gen_locations()
        self._gen_announcements()
        self._gen_matches()
        self._build_gurobi_model()