from typing import List, Optional
import math

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

    def __hash__(self):
        return hash(self.to_tuple())


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

    @property
    def rider_driver_str(self):
        if self.rider:
            return "Rider"
        elif self.driver:
            return "Driver"
        return ""

    def to_tuple(self):
        return (self.origin, self.dest, self.depart, self.arrive, self.rider_driver_str)

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __repr__(self):
        return "{}Announcement<{} -> {}, depart={} arrive={}>".format(
            self.rider_driver_str,
            *self.to_tuple()[:-1]
        )


class RiderAnnouncement(Announcement):
    rider = True
    driver = False

class DriverAnnouncement(Announcement):
    rider = False
    driver = True

__all__ = [
    'Location',
    'RiderAnnouncement',
    'DriverAnnouncement',
]
