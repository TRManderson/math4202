from ..models import *
from gurobipy import Model, quicksum, GRB, Constr, Var
from typing import Dict, Optional, Tuple, TypeVar, Type, Generic
from random import Random
import heapq as hq
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):
        return iterable
import logging
import itertools
from ..util import tail
from operator import itemgetter
import collections

ArcType = TypeVar('ArcType')

class ProblemBase(Generic[ArcType]):
    random = None  # type: Random
    logger = None  # type: logging.Logger
    model = None  # type: Model
    locations = None  # type: List[Location]
    rider_announcements = None  # type: List[RiderAnnouncement]
    driver_announcements = None  # type: List[DriverAnnouncement]
    matches = None  # type: Dict[ArcType, float]
    constraints = None  # type: Dict[str, Constr]
    variables = None  # type: Dict[ArcType, Var]

    def __init__(self, random=None, logger=None):
        self.logger = logger or logging.getLogger("ride_sharing.Problem")
        self.random = random or Random()
        self.model = Model("Ride-sharing")
        self.logger.info("Initialised " + type(self).__name__)

    def _gen_locations(self):
        # Generate a list of random locations to use as the set P
        self.logger.info("Beginning location generation")
        self.locations = []

    def _gen_announcements(self):
        """
        Generate sets of rider and driver announcements
        """
        self.logger.info("Generating announcements")
        self.rider_announcements = []
        self.driver_announcements = []

    def _gen_matches(self):
        # Calculates the cost of each valid match between a rider and a driver
        self.logger.info("Generating valid pairings")
        self.matches = {}

    def _build_gurobi_model(self) -> None:
        """
        Generate the Gurobi model using the already generated locations,
        announcements, feasible matches, etc.
        """
        self.logger.info("Building Gurobi model")
        self.constraints = {}
        self.variables = {}

    def callback(self, model, where):
        self.logger.getChild('callback').debug("Entering callback")

    def build_model(self) -> None:
        self._gen_locations()
        self._gen_announcements()
        self._gen_matches()
        self.logger.info("Generated {} arcs".format(len(self.matches)))
        self._build_gurobi_model()

    def optimize(self):
        def inner_fn(*args, **kwargs):
            """
            Gurobi is mean and doesn't think bound methods are functions
            """
            self.callback(*args, **kwargs)
        self.model.optimize(inner_fn)


class Problem(ProblemBase):
    LOCATION_COUNT = 200
    MIN_XY = 0
    MAX_XY = 200
    ANNOUNCEMENT_COUNT = 2000
    FLEXIBILITY = 20
    MIN_PER_KM = 1.2
    MAX_TIME = 2000
    EPSILON = 0.001

    def _gen_locations(self):
        super()._gen_locations()
        gen = lambda: self.random.uniform(self.MIN_XY, self.MAX_XY)
        self.locations = [Location(gen(), gen()) for _ in tqdm(range(self.LOCATION_COUNT), "locations", ncols=100)]
        self.distances_cache = {}

    def distance_between(self, loc1, loc2):
        if (loc1, loc2) not in self.distances_cache:
            self.distances_cache[loc1, loc2] = loc1.distance_to(loc2)
            self.distances_cache[loc2, loc1] = self.distances_cache[loc1, loc2]
        return self.distances_cache[loc1, loc2]

    def _gen_announcements(self):
        super()._gen_announcements()
        for _ in tqdm(range(self.ANNOUNCEMENT_COUNT), "announcements", ncols=100):
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
                if end_time < self.MAX_TIME:
                    ls.append(cls(
                        origin=start_loc,
                        dest=end_loc,
                        depart=start_time,
                        arrive=end_time
                    ))
                    break
        depart_fn = lambda d: d.depart
        self.rider_announcements.sort(key=depart_fn)
        self.driver_announcements.sort(key=depart_fn)

    def _track_savings(self, rider, driver, savings):
        self.matches[(rider, driver)] = savings
        hq.heappush(self.rider_preferences[rider], (-savings, driver))
        hq.heappush(self.driver_preferences[driver], (-savings, rider))

    def _gen_matches(self):
        # Calculates the cost of each valid match between a rider and a driver
        super()._gen_matches()
        self.driver_preferences = collections.defaultdict(list)
        self.rider_preferences = collections.defaultdict(list)
        for rider in self.rider_announcements:
            for driver in self.driver_announcements:
                if rider.depart > driver.arrive:
                    continue
                if driver.depart > rider.arrive:
                    # drivers are sorted by departure time
                    # all future drivers have > depart
                    break
                pickup = self.distance_between(driver.origin, rider.origin)
                dropoff = self.distance_between(rider.dest, driver.dest)
                d_trip = self.distance_between(driver.origin, driver.dest)
                if pickup + dropoff > d_trip:
                    # if the driver doubles their trip or worse, it's not worth it
                    continue
                r_trip = self.distance_between(rider.origin, rider.dest)

                # check timings
                max_rider_dropoff = driver.arrive - dropoff*self.MIN_PER_KM
                min_rider_pickup = driver.depart + pickup*self.MIN_PER_KM
                overlap = min(rider.arrive, max_rider_dropoff)-max(min_rider_pickup, rider.depart)
                if r_trip*self.MIN_PER_KM > overlap:
                    # if the rider takes longer on their trip than the overlap
                    # between the driver possible pickup time and the rider
                    # allowed times, this is not a valid match
                    continue

                self._track_savings(rider, driver, d_trip - (pickup + dropoff))

    def _build_gurobi_model(self):
        super()._build_gurobi_model()
        riders = collections.defaultdict(list)
        drivers = collections.defaultdict(list)
        objective = 0

        for arc, val in self.matches.items():
            rider, driver = arc
            var = self.variables[arc] = self.model.addVar(vtype=GRB.BINARY)
            objective += var * val
            riders[rider].append(var)
            drivers[driver].append(var)

        self.model.setObjective(objective, sense=GRB.MAXIMIZE)

        r_const = self.constraints['rider'] = {}
        for rider, vars in riders.items():
            r_const[rider] = self.model.addConstr(
                quicksum(vars) <= 1
            )

        d_const = self.constraints['driver'] = {}
        for driver, vars in drivers.items():
            d_const[driver] = self.model.addConstr(
                quicksum(vars) <= 1
            )

    def solution_summary(self):
        rider_total = len(self.rider_announcements)
        rider_participated = 0
        for rider, constr in self.constraints['rider'].items():
            if constr.Slack == 0:
                rider_participated += 1
        self.logger.info("Rider participation: {}/{}\t{}%".format(rider_participated, rider_total, round(rider_participated*100.0/rider_total, 2)))


        driver_total = len(self.driver_announcements)
        driver_participated = 0
        for driver, constr in self.constraints['driver'].items():
            if constr.Slack == 0:
                driver_participated += 1
        self.logger.info("Driver participation: {}/{}\t{}%".format(driver_participated, driver_total, round(driver_participated*100.0/driver_total, 2)))

    def _stability_constraint_for(self, rider, driver, var):
        rider_pref = quicksum(
            self.variables[(rider, driver_preferred)]
            for driver_preferred in
            tail(itertools.dropwhile(driver.__ne__, map(itemgetter(1), self.rider_preferences[rider])))
        )
        driver_pref = quicksum(
            self.variables[(rider_preferred, driver)]
            for rider_preferred in
            tail(itertools.dropwhile(driver.__ne__, map(itemgetter(1), self.driver_preferences[rider])))
        )
        return rider_pref + driver_pref + var >= 1
