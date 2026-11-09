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


from debug import Bike, ElectricBike, Station


TEST_SUITE_NAME = "Debug Tests"


import pytest



def test_setting_a_capacity_does_not_recurse():
    """Station.capacity - assigning a valid capacity stores it instead of recursing"""
    station = Station("Grand Army", 20)
    station.capacity = 25

    assert station.capacity == 25


def test_the_setter_still_refuses_a_bad_value():
    """Station.capacity - the rule was correct and must stay correct"""
    station = Station("Grand Army", 20)

    with pytest.raises(ValueError):
        station.capacity = 0


def test_a_refused_assignment_changes_nothing():
    """Station.capacity - the stored value survives a refusal"""
    station = Station("Grand Army", 20)

    with pytest.raises(ValueError):
        station.capacity = -1

    assert station.capacity == 20


def test_the_value_still_lives_in_the_non_public_attribute():
    """Station.capacity - the fix stores to _capacity, it does not remove the property"""
    station = Station("Grand Army", 20)
    station.capacity = 30

    assert "_capacity" in attributes_set_on(station), \
        "The setter should assign to self._capacity."
    assert isinstance(type(station).capacity, property), \
        "Keep the property. The bug is one word inside the setter."


def test_electric_bike_has_the_attributes_its_parent_stores():
    """ElectricBike - super().__init__ runs, so the three attributes are there"""
    electric = ElectricBike("E9", "Borough Hall", False, 24)

    assert electric.serial == "E9", \
        "Call super().__init__(serial, station, needs_repair) in ElectricBike.__init__."
    assert electric.station == "Borough Hall"
    assert electric.needs_repair is False


def test_electric_bike_keeps_its_own_attribute():
    """ElectricBike - battery_range is still stored by the subclass"""
    assert ElectricBike("E9", "Borough Hall", False, 24).battery_range == 24


def test_electric_bike_can_use_its_inherited_method():
    """ElectricBike - is_rentable needs needs_repair to have been stored"""
    assert ElectricBike("E9", "Borough Hall", False, 24).is_rentable() is True
    assert ElectricBike("E1", "Grand Army", True, 12).is_rentable() is False


def test_the_rate_was_left_alone():
    """ElectricBike - hourly_rate already worked and still does"""
    electric = ElectricBike("E9", "Borough Hall", False, 24)

    assert isinstance(electric, Bike)
    assert electric.hourly_rate() == 7.50
