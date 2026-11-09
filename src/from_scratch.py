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
    pass


class Member:
    pass


class ClassicBike:
    pass


class ElectricBike:
    pass


class Ride:
    pass
