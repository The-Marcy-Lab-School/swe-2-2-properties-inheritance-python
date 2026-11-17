import ast
import importlib.util
import inspect
import textwrap
from pathlib import Path


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

def code_of(func):
    """A function's source with its comments and docstring removed.

    A test that bans a substring has to look at code only. Reading raw source
    fails a fellow who mentions the banned thing in a comment -- "no isinstance
    here" would fail a check for "isinstance" -- which is a correct answer
    rejected for its prose.
    """
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [ast.Pass()]
    return ast.unparse(ast.fix_missing_locations(tree))

def as_written(module, name, cls=None):
    """One function's body as it appears in the file, with decorators ignored.

    Reading a decorated function at runtime gives you the wrapper, so its own
    body is out of reach. Parsing the file instead shows what the fellow wrote,
    and works whatever shape their decorator took -- a closure, a class with
    __call__, or functools.wraps on top of either.
    """
    tree = ast.parse(inspect.getsource(module))
    scope = tree.body
    if cls is not None:
        scope = next(n.body for n in tree.body
                     if isinstance(n, ast.ClassDef) and n.name == cls)
    found = next((n for n in scope
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and n.name == name), None)
    assert found is not None, f"Keep a function named {name}."
    return "\n".join(ast.unparse(stmt) for stmt in found.body)


from from_scratch import Bike, ClassicBike, ElectricBike, Member, Ride, Station


TEST_SUITE_NAME = "From Scratch Tests"


import pytest



def test_station_reads_capacity_through_a_property():
    """Station - station.capacity reads the stored value without parentheses"""
    station = Station("Grand Army", 20)

    assert station.capacity == 20
    assert isinstance(type(station).capacity, property), \
        "Make capacity a @property, so callers read it with no parentheses."


def test_station_stores_the_capacity_non_publicly():
    """Station - the value lives in _capacity, not in a public capacity attribute"""
    station = Station("Grand Army", 20)

    assert "_capacity" in attributes_set_on(station), \
        "Store the number in self._capacity so the property is the way in."
    assert "capacity" not in attributes_set_on(station), \
        "capacity is the property on the class, so it must not also be on the instance."


def test_station_setter_accepts_a_valid_capacity():
    """Station - assigning a capacity of 1 or more replaces the stored value"""
    station = Station("Grand Army", 20)
    station.capacity = 25

    assert station.capacity == 25


def test_station_setter_refuses_a_capacity_below_one():
    """Station - assigning 0 or less raises ValueError with a message naming the rule"""
    station = Station("Grand Army", 20)

    with pytest.raises(ValueError) as refusal:
        station.capacity = 0
    assert str(refusal.value).strip(), \
        "Give ValueError a message saying what the rule is, not a bare raise."

    with pytest.raises(ValueError):
        station.capacity = -4


def test_station_keeps_its_old_capacity_after_a_refusal():
    """Station - a refused assignment leaves the stored value untouched"""
    station = Station("Grand Army", 20)

    with pytest.raises(ValueError):
        station.capacity = 0

    assert station.capacity == 20, \
        "Raise before storing, so a refused value never reaches _capacity."

    station.dock(Bike("A1", "Grand Army", False))
    assert station.free_docks() == 19


import pytest



def test_member_keeps_the_limit_on_the_class():
    """Member - BORROW_LIMIT is 3 and is written in the class body"""
    assert Member.BORROW_LIMIT == 3, \
        "Read it off the class itself: Member.BORROW_LIMIT, with no instance."
    assert "BORROW_LIMIT" in assigns_in_class_body(Member), \
        "Assign BORROW_LIMIT in the class body, not inside __init__."


def test_member_does_not_copy_the_limit_onto_each_instance():
    """Member - BORROW_LIMIT is not stored on the instance"""
    ana = Member("Ana")

    assert "BORROW_LIMIT" not in attributes_set_on(ana), \
        "One shared value on the class, not a copy on every member."


def test_members_hold_their_own_bikes():
    """Member - two members do not share one list of bikes"""
    ana, ben = Member("Ana"), Member("Ben")
    ana.borrow(Bike("A1", "Grand Army", False))

    assert len(ana.bikes) == 1
    assert len(ben.bikes) == 0, \
        "Start the list in __init__ with self.bikes = [], so each member owns one."


def test_member_refuses_a_fourth_bike():
    """Member - borrowing at the limit raises ValueError, and can_borrow says so first"""
    ana = Member("Ana")
    for serial in ["A1", "A2", "A3"]:
        ana.borrow(Bike(serial, "Grand Army", False))

    assert ana.can_borrow() is False
    with pytest.raises(ValueError):
        ana.borrow(Bike("A4", "Grand Army", False))
    assert len(ana.bikes) == 3, "A refused borrow must not add the bike."


def test_both_kinds_are_bikes():
    """ClassicBike and ElectricBike - both inherit from Bike"""
    assert issubclass(ClassicBike, Bike), "class ClassicBike(Bike): inherit, do not copy."
    assert issubclass(ElectricBike, Bike), "class ElectricBike(Bike): inherit, do not copy."


def test_classic_bike_inherits_what_bike_already_does():
    """ClassicBike - the parent stores the three attributes and answers is_rentable"""
    classic = ClassicBike("A1", "Grand Army", False)

    assert classic.serial == "A1"
    assert classic.station == "Grand Army"
    assert classic.is_rentable() is True
    assert ClassicBike("B7", "Borough Hall", True).is_rentable() is False


def test_classic_bike_charges_a_dollar_over_the_base():
    """ClassicBike - hourly_rate is the base rate plus 1.00"""
    assert ClassicBike("A1", "Grand Army", False).hourly_rate() == 4.00


def test_electric_bike_stores_its_own_attribute_and_the_parents():
    """ElectricBike - super().__init__ stores the three, and battery_range is added"""
    electric = ElectricBike("E9", "Borough Hall", False, 24)

    assert electric.battery_range == 24
    assert electric.serial == "E9", \
        "Call super().__init__(...) so Bike stores the serial, station and repair flag."
    assert electric.station == "Borough Hall"
    assert electric.needs_repair is False


def test_electric_bike_charges_more():
    """ElectricBike - hourly_rate is the base rate plus 4.50"""
    assert ElectricBike("E9", "Borough Hall", False, 24).hourly_rate() == 7.50


def test_neither_subclass_writes_the_base_rate_itself():
    """ClassicBike and ElectricBike - both reach the base rate through super()"""
    for cls in (ClassicBike, ElectricBike):
        source = code_of(cls.hourly_rate)
        assert "super()" in source, \
            f"{cls.__name__}.hourly_rate must call super().hourly_rate() for the base rate."
        assert "Bike.hourly_rate" not in source, \
            f"{cls.__name__}.hourly_rate must reach the parent through super(), " \
            "not by naming the class."


import pytest



def test_ride_stores_the_bike_and_the_minutes():
    """Ride - __init__ keeps the bike object itself, not just its serial"""
    bike = Bike("A1", "Grand Army", False)
    ride = Ride(bike, 30)

    assert ride.bike is bike, "Store the Bike object, so the ride can ask it for its rate."
    assert ride.minutes == 30


def test_ride_works_out_its_cost():
    """Ride - cost is the bike's hourly rate over the minutes, read without parentheses"""
    ride = Ride(Bike("A1", "Grand Army", False), 30)

    assert ride.cost == 1.5
    assert isinstance(type(ride).cost, property), \
        "Make cost a @property, so callers read it with no parentheses."


def test_ride_never_stores_the_cost():
    """Ride - correcting the minutes changes the cost"""
    ride = Ride(Bike("A1", "Grand Army", False), 30)
    ride.minutes = 60

    assert ride.cost == 3.0, "Work the cost out when asked rather than storing it."
    assert "cost" not in attributes_set_on(ride), \
        "cost is computed, so it must not be an attribute on the instance."


def test_ride_refuses_to_have_its_cost_set():
    """Ride - assigning to cost raises AttributeError, because there is no setter"""
    ride = Ride(Bike("A1", "Grand Army", False), 30)

    with pytest.raises(AttributeError):
        ride.cost = 99


YOUR_TESTS = Path(__file__).parent.parent / "my_tests" / "test_bike_rates.py"


class WorkingBike:
    def __init__(self, serial, station, needs_repair):
        self.serial = serial
        self.station = station
        self.needs_repair = needs_repair

    def hourly_rate(self):
        return 3.00


class WorkingClassicBike(WorkingBike):
    def hourly_rate(self):
        return super().hourly_rate() + 1.00


class WorkingElectricBike(WorkingBike):
    def __init__(self, serial, station, needs_repair, battery_range):
        super().__init__(serial, station, needs_repair)
        self.battery_range = battery_range

    def hourly_rate(self):
        return super().hourly_rate() + 4.50


class ClassicBikeWithoutItsDollar(WorkingClassicBike):
    def hourly_rate(self):
        return WorkingBike.hourly_rate(self)


class ElectricBikeThatReplacesTheBase(WorkingElectricBike):
    def hourly_rate(self):
        return 4.50


def your_test(name, classic_class, electric_class, monkeypatch):
    """One of the fellow's tests, set to run against the given bike classes.

    Their file imports ClassicBike and ElectricBike from from_scratch.
    Replacing both names in the loaded file grades the test itself, whatever
    state their own classes are in.
    """
    spec = importlib.util.spec_from_file_location("your_bike_tests", YOUR_TESTS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ClassicBike", classic_class)
    monkeypatch.setattr(module, "ElectricBike", electric_class)
    test = getattr(module, name, None)
    assert test is not None, f"Keep the name {name} for your test in {YOUR_TESTS.name}."
    return test


def test_your_classic_bike_test_catches_a_wrong_rate(monkeypatch):
    """Your tests - the classic bike test passes on a working bike and fails when the dollar is not added"""
    name = "test_a_classic_bike_adds_one_dollar"

    your_test(name, WorkingClassicBike, WorkingElectricBike, monkeypatch)()

    broken_test = your_test(name, ClassicBikeWithoutItsDollar, WorkingElectricBike, monkeypatch)
    try:
        broken_test()
    except AssertionError:
        return
    pytest.fail("Your test passed against a classic bike that charges only the base rate, so it would not catch that mistake.")


def test_your_electric_bike_test_catches_a_wrong_rate(monkeypatch):
    """Your tests - the electric bike test passes on a working bike and fails when the base rate is left out"""
    name = "test_an_electric_bike_adds_four_fifty"

    your_test(name, WorkingClassicBike, WorkingElectricBike, monkeypatch)()

    broken_test = your_test(name, WorkingClassicBike, ElectricBikeThatReplacesTheBase, monkeypatch)
    try:
        broken_test()
    except AssertionError:
        return
    pytest.fail("Your test passed against an electric bike that charges only its $4.50, so it would not catch that mistake.")
