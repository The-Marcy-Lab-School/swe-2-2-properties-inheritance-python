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
        self._capacity = capacity

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        if value < 1:
            raise ValueError("A station needs at least one dock.")
        self.capacity = value


class ElectricBike(Bike):
    def __init__(self, serial, station, needs_repair, battery_range):
        self.battery_range = battery_range

    def hourly_rate(self):
        return super().hourly_rate() + 4.50
