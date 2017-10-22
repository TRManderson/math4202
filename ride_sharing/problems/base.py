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
import time
from operator import itemgetter, attrgetter
import collections

ArcType = TypeVar('ArcType')


def distance_between(loc1, loc2, cache={}):
    if (loc1, loc2) not in cache:
        cache[loc1, loc2] = loc1.distance_to(loc2)
        cache[loc2, loc1] = cache[loc1, loc2]
    return cache[loc1, loc2]


class Problem(Generic[ArcType]):
    LOCATION_COUNT = 500
    MIN_XY = 0
    MAX_XY = 1000
    ANNOUNCEMENT_COUNT = 20000
    FLEXIBILITY = 20
    MIN_PER_KM = 1.2
    MAX_TIME = 2000
    PRECISION = 4

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
        self.locations = []
        self.constraints = {}
        self.variables = {}
        self.rider_announcements = set()
        self.driver_announcements = set()
        self.matches = {}
        self.driver_preferences = collections.defaultdict(list)
        self.rider_preferences = collections.defaultdict(list)

    def _gen_locations(self):
        # Generate a list of random locations to use as the set P
        self.logger.info("Beginning location generation")
        gen = lambda: round(self.random.uniform(self.MIN_XY, self.MAX_XY), self.PRECISION)
        self.locations = [Location(gen(), gen()) for _ in tqdm(range(self.LOCATION_COUNT), "locations", ncols=100)]
        self.distances_cache = {}

    def _gen_announcements(self):
        self.logger.info("Generating announcements")
        for _ in tqdm(range(self.ANNOUNCEMENT_COUNT), "announcements", ncols=100):
            if self.random.randint(0, 1):
                ls = self.rider_announcements
                cls = RiderAnnouncement
            else:
                ls = self.driver_announcements
                cls = DriverAnnouncement
            start_loc = self.random.choice(self.locations)
            end_loc = self.random.choice(self.locations)
            dist = distance_between(start_loc, end_loc, self.distances_cache)
            while True:
                start_time = round(self.random.uniform(0, self.MAX_TIME), self.PRECISION)
                end_time = start_time + dist*self.MIN_PER_KM + self.FLEXIBILITY
                if end_time < self.MAX_TIME:
                    announcement = cls(
                        origin=start_loc,
                        dest=end_loc,
                        depart=start_time,
                        arrive=end_time
                    )
                    if announcement not in ls:
                        ls.add(announcement)
                        break
        depart_fn = attrgetter('depart')
        self.rider_announcements = list(self.rider_announcements)
        self.driver_announcements = list(self.driver_announcements)
        self.rider_announcements.sort(key=depart_fn)
        self.driver_announcements.sort(key=depart_fn)

    def _track_savings(self, rider, driver, savings):
        self.matches[(rider, driver)] = savings
        hq.heappush(self.rider_preferences[rider], (savings, driver))
        hq.heappush(self.driver_preferences[driver], (savings, rider))

    def _gen_matches(self):
        # Calculates the cost of each valid match between a rider and a driver
        self.logger.info("Generating valid pairings")
        for rider in self.rider_announcements:
            for driver in self.driver_announcements:
                if rider.depart > driver.arrive:
                    continue
                if driver.depart > rider.arrive:
                    # drivers are sorted by departure time
                    # all future drivers have > depart
                    break
                pickup = distance_between(driver.origin, rider.origin, self.distances_cache)
                dropoff = distance_between(rider.dest, driver.dest, self.distances_cache)
                d_trip = distance_between(driver.origin, driver.dest, self.distances_cache)
                if pickup + dropoff > d_trip:
                    # if the driver doubles their trip or worse, it's not worth it
                    continue
                r_trip = distance_between(rider.origin, rider.dest, self.distances_cache)

                # check timings
                max_rider_dropoff = driver.arrive - dropoff*self.MIN_PER_KM
                min_rider_pickup = driver.depart + pickup*self.MIN_PER_KM
                overlap = min(rider.arrive, max_rider_dropoff)-max(min_rider_pickup, rider.depart)
                if r_trip*self.MIN_PER_KM > overlap:
                    # if the rider takes longer on their trip than the overlap
                    # between the driver possible pickup time and the rider
                    # allowed times, this is not a valid match
                    continue
                if d_trip - (pickup + dropoff) < 0:
                    continue

                self._track_savings(rider, driver, d_trip - (pickup + dropoff))

    def load_data(self, filename):
        with open(filename, 'rb') as f:
            ds = DataSet.load_data(f)
        self.locations = ds.locations
        self.rider_announcements = ds.rider_announcements
        self.driver_announcements = ds.driver_announcements
        self.matches = ds.matches
        self.rider_preferences = ds.rider_preferences
        self.driver_preferences = ds.driver_preferences

    def save_data(self, filename):
        ds = DataSet(
            locations=self.locations,
            rider_announcements=self.rider_announcements,
            driver_announcements=self.driver_announcements,
            matches=self.matches,
            rider_preferences=self.rider_preferences,
            driver_preferences=self.driver_preferences,
        )
        with open(filename, 'wb+') as f:
            ds.save_data(f)

    def _build_gurobi_model(self):
        """
        Generate the Gurobi model using the already generated locations,
        announcements, feasible matches, etc.
        """
        self.logger.info("Building Gurobi model")

        riders = collections.defaultdict(list)
        drivers = collections.defaultdict(list)
        self.constraints['stability'] = {}
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
                quicksum(vars) <= 1, name="{} once".format(rider)
            )

        d_const = self.constraints['driver'] = {}
        for driver, vars in drivers.items():
            d_const[driver] = self.model.addConstr(
                quicksum(vars) <= 1, name="{} once".format(driver)
            )

    def callback(self, model, where):
        self.logger.getChild('callback').debug("Entering callback")

    def build_data(self):
        self._gen_locations()
        self._gen_announcements()
        t1 = time.time()
        self._gen_matches()
        t2 = time.time()
        self.logger.info("Generated {} arcs: {}s".format(len(self.matches), t2-t1))

    def build_model(self) -> None:
        t1 = time.time()
        self._build_gurobi_model()
        t2 = time.time()
        self.logger.info("Building gurobi model took {}s".format(t2 - t1))

    def optimize(self):
        def inner_fn(*args, **kwargs):
            """
            Gurobi is mean and doesn't think bound methods are functions
            """
            self.callback(*args, **kwargs)
        self.model.optimize(inner_fn)

    def solution_summary(self):
        if self.model.Status == GRB.INFEASIBLE:
            self.model.computeIIS()
            p = False
            for rider, constr in self.constraints['rider'].items():
                if constr.IISConstr:
                    p = True
                    self.logger.info('{} participates in IIS'.format(rider))
            if not p:
                self.logger.info("No rider constraints participate in IIS")

            p = False
            for driver, constr in self.constraints['driver'].items():
                if constr.IISConstr:
                    p = True
                    self.logger.info('{} participates in IIS'.format(driver))
            if not p:
                self.logger.info("No driver constraints participate in IIS")

            p = False
            for arc, constr in self.constraints['stability'].items():
                if constr.IISConstr:
                    p = True
                    self.logger.info('{} participates in IIS (cost {})'.format(arc, self.matches[arc]))
            if not p:
                self.logger.info("No stability constraints participate in IIS")

            return

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

    def _stability_filter(self, savings, person, items):
        i = iter(items)
        while True:
            s, p = next(i)
            if s < savings:
                continue
            elif s == savings:
                if p != person:
                    yield p
                    self.logger.debug("Found tie: {} == {}".format(person, p))
            else:
                yield p


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
        return rider_pref + driver_pref + var >= 1
