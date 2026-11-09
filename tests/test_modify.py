import ast
import inspect
import textwrap


def attributes_set_on(instance):
    """The attribute names stored on this instance rather than on its class.

    An attribute written in the class body is shared by every instance, so it
    does not appear here. One assigned to self in __init__ does.
    """
    return set(vars(instance))


def assigns_in_class_body(cls):
    """The names assigned directly in a class body, read with the ast module.

    The source is parsed rather than searched as text, so a name mentioned in a
    comment or a docstring never counts.
    """
    source = textwrap.dedent(inspect.getsource(cls))
    body = ast.parse(source).body[0].body
    names = set()
    for node in body:
        if isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


from modify import Bike, BoroughBike, Ride, Station


TEST_SUITE_NAME = "Modify Tests"


import inspect



def test_station_stores_the_capacity_non_publicly():
    """Station.capacity - the number moved to _capacity"""
    station = Station("Grand Army", 20)

    assert "_capacity" in attributes_set_on(station), \
        "Assign to self._capacity in __init__."
    assert "capacity" not in attributes_set_on(station), \
        "capacity is now the property on the class, so it is no longer on the instance."


def test_station_still_answers_for_its_capacity():
    """Station.capacity - reading it through the property gives the same number"""
    station = Station("Grand Army", 20)

    assert station.capacity == 20
    assert isinstance(type(station).capacity, property), \
        "Add a @property called capacity that returns self._capacity."


def test_the_three_readers_still_work():
    """Station.capacity - dock, free_docks and __repr__ behave exactly as before"""
    station = Station("Grand Army", 2)

    assert station.free_docks() == 2
    station.dock("first")
    assert station.free_docks() == 1
    assert "capacity=2" in repr(station)


def test_the_three_readers_were_left_alone():
    """Station.capacity - the methods still ask for self.capacity, not self._capacity"""
    for method in (Station.dock, Station.free_docks, Station.__repr__):
        source = inspect.getsource(method)
        assert "_capacity" not in source, \
            f"{method.__name__} should not have changed. The property is what makes that possible."


import modify



def test_borough_bike_takes_the_borough_as_an_argument():
    """BoroughBike - one class covers every borough"""
    assert BoroughBike("A1", "Grand Army", False, "Brooklyn").borough == "Brooklyn"
    assert BoroughBike("M4", "Union Square", False, "Manhattan").borough == "Manhattan"


def test_borough_bike_is_still_a_bike():
    """BoroughBike - it inherits, so the parent still stores the three attributes"""
    bike = BoroughBike("A1", "Grand Army", False, "Brooklyn")

    assert isinstance(bike, Bike)
    assert bike.serial == "A1", "Call super().__init__(...) so Bike stores the serial."
    assert bike.station == "Grand Army"
    assert bike.is_rentable() is True


def test_the_two_old_classes_are_gone():
    """BoroughBike - ManhattanBike and BrooklynBike have been deleted"""
    assert not hasattr(modify, "ManhattanBike"), \
        "Delete ManhattanBike. One class with an attribute replaces it."
    assert not hasattr(modify, "BrooklynBike"), \
        "Delete BrooklynBike. One class with an attribute replaces it."


def test_the_borough_arrives_as_an_argument():
    """BoroughBike - __init__ takes a borough, and no borough name is written into it"""
    import inspect

    parameters = inspect.signature(BoroughBike.__init__).parameters
    assert "borough" in parameters, \
        "BoroughBike.__init__ takes the borough as an argument."

    source = inspect.getsource(BoroughBike)
    assert "Brooklyn" not in source and "Manhattan" not in source, \
        "The borough arrives as an argument, so no borough name belongs in the class."


def test_ride_holds_the_bike_it_was_given():
    """Ride - the bike is stored as an attribute, and it is the same object"""
    bike = Bike("A1", "Grand Army", False)
    ride = Ride(bike, 30)

    assert ride.bike is bike, "Store the Bike object itself: self.bike = bike."
    assert ride.minutes == 30


def test_a_ride_is_not_a_bike():
    """Ride - it no longer inherits from Bike"""
    bike = Bike("A1", "Grand Army", False)
    ride = Ride(bike, 30)

    assert not isinstance(ride, Bike), \
        "A ride has a bike, so Ride must not inherit from Bike."
    assert not hasattr(ride, "serial"), \
        "The ride does not carry the serial. Its bike does: ride.bike.serial."


def test_ride_asks_its_bike_for_the_rate():
    """Ride - rate reaches through to the bike it holds"""
    ride = Ride(Bike("A1", "Grand Army", False), 30)

    assert ride.rate() == 3.00


def test_two_rides_can_share_one_bike():
    """Ride - the same bike taken out twice is one object, held by both rides"""
    bike = Bike("A1", "Grand Army", False)
    morning, evening = Ride(bike, 30), Ride(bike, 45)

    assert morning.bike is evening.bike
    assert morning.minutes != evening.minutes
