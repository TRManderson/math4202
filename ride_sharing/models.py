from typing import List, Dict, Tuple, Optional
from random import Random
import math
import logging
from gurobipy import Model, quicksum, GRB

Time = float  # type alias

class Location(object):
	"""
	The distance between any pair of locations must be known, this is the only
	requirement.

	A simple way to fulfill this requirement is by generating 2D coordinates
	for locations and using euclidean distance as the distance metric.
	"""
	__slots__ = ('x', 'y')

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def distance_to(self, other):
		return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

	def to_tuple(self):
		return (self.x, self.y)

	def __str__(self):
		return "({}, {})".format(*self.to_tuple())

	def __repr__(self):
		return "Location<x={}, y={}>".format(*self.to_tuple())


def Announcement(object):
	"""
	Announcements include an origin and departure location, an earliest departure
	time, a latest arrival time, and an announcement time.

	The time-flexibility of an announcement is the difference between latest arrival
	and earliest departure, minus travel time.

	v(s) = trip origin
	w(s) = trip destination
	e(s) = earliest departure
	l(s) = latest arrival
	f(s) = time_flexibility
	"""
	__slots__ = ('origin', 'dest', 'depart', 'arrive')
	origin = None  # type: Location
	dest = None  # type: Location
	depart = None  # type: Time
	arrive = None  # type: Time
	rider = None  # type: Optional[bool]
	driver = None  # type: Optional[bool]

	def __init__(self, origin: Location, dest: Location, depart: Time, arrive: Time):
		self.origin = origin
		self.dest = dest
		self.depart = depart
		self.arrive = arrive

	def to_tuple(self):
		return (self.origin, self.dest, self.depart, self.arrive)

	def __hash__(self):
		return hash(self.to_tuple())

	def __eq__(self, other):
		return self.to_tuple() == other.to_tuple() 
			and self.rider == other.rider
			and self.driver == other.driver

	def __repr__(self):
		rider_driver = ""
		if self.rider:
			rider_driver = "Rider"
		elif self.driver:
			rider_driver = "Driver"
		return "{}Announcement<{} -> {}, depart={} arrive={}>".format(rider_driver, *self.to_tuple())


class RiderAnnouncement(Announcement):
	rider = True
	driver = False

class DriverAnnouncement(Announcement):
	rider = False
	driver = True

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