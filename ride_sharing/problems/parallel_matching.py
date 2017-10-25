from .base import Problem, distance_between
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from multiprocessing import cpu_count
_parallel_distance_cache = {}


def matches_for_rider(rider, driver_announcements, min_per_km):
    result = []
    for driver in driver_announcements:
        if rider.depart > driver.arrive:
            continue
        if driver.depart > rider.arrive:
            # drivers are sorted by departure time
            # all future drivers have > depart
            break
        pickup = distance_between(driver.origin, rider.origin, _parallel_distance_cache)
        dropoff = distance_between(rider.dest, driver.dest, _parallel_distance_cache)
        d_trip = distance_between(driver.origin, driver.dest, _parallel_distance_cache)
        if pickup + dropoff > d_trip:
            # if the driver doubles their trip or worse, it's not worth it
            continue
        r_trip = distance_between(rider.origin, rider.dest, _parallel_distance_cache)

        # check timings
        max_rider_dropoff = driver.arrive - dropoff * min_per_km
        min_rider_pickup = driver.depart + pickup * min_per_km
        overlap = min(rider.arrive, max_rider_dropoff)-max(min_rider_pickup, rider.depart)
        if r_trip * min_per_km > overlap:
            # if the rider takes longer on their trip than the overlap
            # between the driver possible pickup time and the rider
            # allowed times, this is not a valid match
            continue

        result.append((rider, driver, d_trip - (pickup + dropoff)))
    return result


class ParallelMatchingProblem(Problem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distances_cache = _parallel_distance_cache

    def _gen_matches(self):
        self.logger.info("Generating valid pairings")
        exec = ProcessPoolExecutor()

        chunk_size = int(round(len(self.rider_announcements)/(cpu_count()*8.0)))

        fn = partial(matches_for_rider, driver_announcements=self.driver_announcements, min_per_km=self.MIN_PER_KM)

        for results in exec.map(fn, self.rider_announcements, chunksize=chunk_size):
            for res in results:
                self._track_savings(*res)