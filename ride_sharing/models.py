from typing import List, Optional
import math
import attr
import pickle

Time = float  # type alias


@attr.s(frozen=True)
class Location(object):
    """
    The distance between any pair of locations must be known, this is the only
    requirement.

    A simple way to fulfill this requirement is by generating 2D coordinates
    for locations and using euclidean distance as the distance metric.
    """
    x = attr.ib()
    y = attr.ib()

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@attr.s(frozen=True)
class Announcement(object):
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
    # __slots__ = ('origin', 'dest', 'depart', 'arrive')
    origin = attr.ib()  # type: Location
    dest = attr.ib()  # type: Location
    depart = attr.ib()  # type: Time
    arrive = attr.ib()  # type: Time
    rider = None  # type: Optional[bool]
    driver = None  # type: Optional[bool]
    rider_driver_str = attr.ib(init=False)

    def __attrs_post_init__(self):
        set = lambda v: object.__setattr__(self, 'rider_driver_str', v)
        if self.rider:
            set("Rider")
        elif self.driver:
            set("Rider")
        else:
            set("")


class RiderAnnouncement(Announcement):
    rider = True
    driver = False


class DriverAnnouncement(Announcement):
    rider = False
    driver = True


@attr.s(frozen=True)
class DataSet(object):
    locations = attr.ib()
    rider_announcements = attr.ib()
    driver_announcements = attr.ib()
    matches = attr.ib()
    rider_preferences = attr.ib()
    driver_preferences = attr.ib()

    @classmethod
    def load_data(cls, f):
        return cls(**pickle.load(f))

    def save_data(self, f):
        pickle.dump(attr.asdict(self, recurse=False), f)


__all__ = [
    'Location',
    'RiderAnnouncement',
    'DriverAnnouncement',
    'DataSet'
]
