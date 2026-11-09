class Bike:
    """Already written for you. Do not change it."""

    def __init__(self, serial, station, needs_repair):
        self.serial = serial
        self.station = station
        self.needs_repair = needs_repair

    def is_rentable(self):
        return not self.needs_repair

    def hourly_rate(self):
        """The base rate, in dollars, that every kind of bike starts from."""
        return 3.00

    def __repr__(self):
        return f"Bike({self.serial!r}, {self.station!r}, {self.needs_repair})"


class Station:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.bikes = []

    def dock(self, bike):
        if len(self.bikes) >= self.capacity:
            raise ValueError(f"{self.name} is full.")
        self.bikes.append(bike)

    def free_docks(self):
        return self.capacity - len(self.bikes)

    def __repr__(self):
        return f"Station({self.name!r}, capacity={self.capacity})"


class ManhattanBike(Bike):
    def __init__(self, serial, station, needs_repair):
        super().__init__(serial, station, needs_repair)
        self.borough = "Manhattan"


class BrooklynBike(Bike):
    def __init__(self, serial, station, needs_repair):
        super().__init__(serial, station, needs_repair)
        self.borough = "Brooklyn"


class BoroughBike(Bike):
    """Replace the two classes above with this one."""
    pass


class Ride(Bike):
    def __init__(self, serial, station, needs_repair, minutes):
        super().__init__(serial, station, needs_repair)
        self.minutes = minutes

    def rate(self):
        return self.hourly_rate()
