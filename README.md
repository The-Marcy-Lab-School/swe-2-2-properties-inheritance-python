# Properties and Inheritance

Put a rule behind an attribute so it cannot be set to nonsense, and let one class build on another.

**Practicing:** non-public attributes, `@property`, validating setters, class attributes, inheritance, `super()`, overriding a method, `__dict__`, testing each subclass

- [AI Use on This Assignment](#ai-use-on-this-assignment)
- [Setup](#setup)
- [Before You Start](#before-you-start)
  - [Syntax to recognize](#syntax-to-recognize)
  - [Look these up yourself](#look-these-up-yourself)
- [From Scratch](#from-scratch)
  - [Question 1: `Station`](#question-1-station)
  - [Question 2: `Member`](#question-2-member)
  - [Question 3: `ClassicBike` and `ElectricBike`](#question-3-classicbike-and-electricbike)
  - [Question 4: `Ride`](#question-4-ride)
  - [Question 5: Testing Each Kind of Bike](#question-5-testing-each-kind-of-bike)
- [Modify](#modify)
  - [Question 6: `Station.capacity`](#question-6-stationcapacity)
  - [Question 7: `BoroughBike`](#question-7-boroughbike)
  - [Question 8: `Ride`](#question-8-ride)
- [Debug](#debug)
  - [Question 9: `Station.capacity`](#question-9-stationcapacity)
  - [Question 10: `ElectricBike`](#question-10-electricbike)
- [Submitting](#submitting)
- [Good luck!](#good-luck)

## AI Use on This Assignment

**Tutor mode, for this whole quarter.** The AI explains, questions, quizzes,
and critiques, and you write every line you submit. Quarter 1 is where you
build the habit of writing code by hand; asking an AI to write it for you
comes later, in Quarter 2, where the job becomes judging code rather than
producing it.

For this assignment that means asking it what a setter receives as its
parameter, or having it quiz you on what
`super().__init__()` actually runs until you can say it without looking. Ask it
a hundred questions — that is the whole point. What you do not do is ask it for
the answer. Paste this at the start of a chat and it will hold for the rest of
the conversation:

> You are acting as a tutor. Your job is to explain what this coding question
> is asking, clarify confusing wording, and highlight the relevant concepts I
> need to know — but do not provide the full solution or code that directly
> answers the question. Instead, rephrase the problem in simpler terms,
> identify what is being tested, and suggest what steps or thought processes
> might help. Ask me guiding questions to make sure I am thinking critically.
> Do not write the final function, algorithm, or code implementation.

You own every line you submit, and you will be asked to explain it.

## Setup

Clone your repository in `development/mod-2` and then `cd` into it. Set up
your virtual environment and make a draft branch before you start.

```sh
git clone [your_repo]
cd [your_repo]
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
git checkout -b draft
```

Run `pytest` to test the entire assignment. To run one question, pass part of
its name: `pytest -k Bike`. Every push runs the tests on GitHub and reports
which ones passed in the **Actions** tab.

Push before it is finished. Your instructor grades this against the rubric,
not against the test count, so treat submitting as a checkpoint rather than a
finish line and come back to improve it.

When you are done working on this assignment, turn off your virtual
environment by running:

```sh
deactivate
```

## Before You Start

Skim this section before you read the lessons, so you know what to look for in
them. Classes, instances, `__init__`, `self` and `__repr__` are all assumed
here. The new material is the **rule that lives with the data**, and the
**class that builds on another class**.

This assignment has three sections:

1. From Scratch
2. Modify
3. Debug

<details>
<summary><strong>Ideas to look for</strong> — the ideas behind the questions, if you want them up front</summary>

Each question depends on one or more of these ideas. Part of the work is
deciding which.

| Idea                                                                                                                                                                                                                              | Lesson |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| A single leading underscore, as in `self._capacity`, tells another programmer that this attribute is not part of the class's public interface. It prevents nothing. It is a message, and Python does not enforce it.              | 2.3    |
| A `@property` makes a method readable like an attribute: `station.capacity`, with no parentheses. The caller cannot tell the difference, which is why an attribute can become a property without changing the code that reads it. | 2.3    |
| A setter runs whenever anything assigns to that name on an instance, including code inside the setter itself. It is the one place a rule about the value belongs.                                                                 | 2.3    |
| Raise `ValueError` to refuse a value, and raise it **before** storing anything, so a refused assignment leaves the old value exactly as it was.                                                                                   | 2.3    |
| A property with a getter and no setter cannot be assigned to. That is how you make a value that is always computed and never stored.                                                                                              | 2.3    |
| A value assigned in the class body, written in capitals by convention, belongs to the class and is shared by every instance. Read it through the class name, so the value appears once.                                           | 2.4    |
| A subclass inherits the parent's methods, so it can use them without rewriting them. Writing `class ElectricBike(Bike):` is the whole mechanism.                                                                                  | 2.4    |
| Inheriting does **not** run the parent's `__init__`. A subclass that writes its own `__init__` replaces the parent's and must call `super().__init__(...)` itself.                                                                | 2.4    |
| Overriding means defining a method the parent already has. `super().method()` calls the parent's version, so the subclass can extend an answer instead of replacing it.                                                           | 2.4    |
| Inheritance is for "is a". Composition — holding another object as an attribute — is for "has a". A ride is not a kind of bike, so `Ride` holds a `Bike`.                                                                         | 2.4    |
| Two subclasses that differ only by a stored value should be one class that takes that value as an argument. A subclass is for different behavior, not for different data.                                                         | 2.4    |
| `obj.__dict__` lists the attributes stored on one object. A property is defined on the class, so it does not appear there, but the non-public attribute the property reads does.                                                  | 2.4    |
| When two subclasses override the same method, give each subclass its own test that makes the same call and asserts the result that subclass should give, so a failing test names the subclass that broke.                         | 2.4    |

</details>

### Syntax to recognize

```python
class Event:
    def __init__(self, name, date, capacity, base_price):
        self.name = name                 # public: no rule, so no property
        self.date = date
        self.capacity = capacity         # runs the capacity setter below
        self.base_price = base_price
        self._seats_sold = 0             # non-public: a single leading underscore

    @property
    def seats_sold(self):                # a getter with no setter: read, never assigned
        return self._seats_sold

    @property
    def capacity(self):                  # read as pottery.capacity, no parentheses
        return self._capacity

    @capacity.setter
    def capacity(self, value):           # runs on pottery.capacity = 0
        if value < 1:
            raise ValueError(f'Capacity must be at least 1, not {value}.')
        self._capacity = value

    def ticket_price(self):
        return self.base_price


class Concert(Event):                    # Concert inherits from Event
    SERVICE_FEE = 5                      # a class attribute: one copy, shared

    def __init__(self, name, date, capacity, base_price, performer):
        super().__init__(name, date, capacity, base_price)   # runs Event's __init__
        self.performer = performer

    def ticket_price(self):              # overrides Event's ticket_price()
        return super().ticket_price() + Concert.SERVICE_FEE   # extends Event's version
```

### Look these up yourself

- `round()`. One question asks for a price rounded to two decimal places. Read
  about it on
  [W3Schools](https://www.w3schools.com/python/ref_func_round.asp).

## From Scratch

Write these functions and classes in `src/from_scratch.py`.

The examples pass every number and every `True` or `False` by keyword, as in
`Station("Grand Army", capacity=20)`, so that each value says what it is. Give
each `__init__` parameter the name the examples use, or those calls will not
run.

### Question 1: `Station`

**`Bike` is already written for you** in `src/from_scratch.py`.

A station's capacity is the number of docks it has. Last week someone accidentally set a
station's capacity to `0` through a script, the station accepted it, and the
app spent a day reporting that a station with eight bikes in it had no docks for them.

Write a class `Station` that will not accept a capacity below 1.

`__init__` takes a station name and a capacity. Store the name as `self.name`.
Store the capacity in a **non-public attribute** called `self._capacity`, and
start an empty list of bikes called `self.bikes`.

| Member            | Does                                                                                                       | Returns    |
| ----------------- | ---------------------------------------------------------------------------------------------------------- | ---------- |
| `capacity`        | Reads the stored capacity. A `@property`, so callers write `station.capacity` with no parentheses          | The number |
| `capacity` setter | Replaces the capacity, but raises `ValueError` if the new value is below 1 with a message stating the rule | Nothing    |
| `dock(bike)`      | Puts one `Bike` at this station                                                                            | Nothing    |
| `free_docks()`    | How many docks are still empty                                                                             | The number |

```python
station = Station("Grand Army", capacity=20)
station.capacity                 # 20 — no parentheses, it is a property
station.free_docks()             # 20

station.dock(Bike("A1", "Grand Army", needs_repair=False))
station.free_docks()             # 19

station.capacity = 25            # allowed, this goes through the setter
station.capacity                 # 25

station.capacity = 0             # raises ValueError
station.capacity                 # still 25 — a refused assignment changes nothing
```

The setter has one job: decide, then either store or refuse. When it refuses it
raises `ValueError` with a message that says what the rule is, and the stored
value stays exactly as it was.

Tip: Assign to `self.capacity` inside `__init__` rather than to `self._capacity`.
Assigning to `self.capacity` anywhere, inside the class or outside it, runs the
setter, so the setter also checks the starting capacity and no station can be
created with a capacity of 0.

### Question 2: `Member`

Every Boro Bikes member may borrow up to three bikes at once, and the limit is
the same for every member.

Write a class called `Member` that has a name and a list of the bikes the
member is holding, and keeps the borrowing limit on the class itself. It should
answer the question "can this member borrow another bike?"

`__init__` takes a member's name, stores it on the instance, and starts an
empty list of bikes called `self.bikes`.

| Member         | Does                                                                                            | Returns           |
| -------------- | ----------------------------------------------------------------------------------------------- | ----------------- |
| `BORROW_LIMIT` | A **class attribute** set to `3`, written in the class body rather than in `__init__`           | The number        |
| `borrow(bike)` | Adds a bike if the member is under the limit, and raises `ValueError` if they are already at it | Nothing           |
| `can_borrow()` | Whether this member is under the limit right now                                                | `True` or `False` |

```python
Member.BORROW_LIMIT              # 3 — read off the class, no instance needed

ana = Member("Ana")
ana.can_borrow()                 # True
ana.borrow(Bike("A1", "Grand Army", needs_repair=False))
len(ana.bikes)                   # 1

Member("Ben").can_borrow()       # True — this member has an empty list of their own
```

Read the limit as `Member.BORROW_LIMIT` inside your methods, not as a bare `3`.
The point of the class attribute is that the number appears once.

The capital letters are a convention: they tell another programmer this value is
a fixed setting, not something that changes per member.

### Question 3: `ClassicBike` and `ElectricBike`

Boro Bikes now rents two kinds of bike. Both have a serial, a station and a
repair flag, and both can be rented — all of that is already true of a `Bike`.
What differs is the price, and an electric bike also stores its battery range:
how many miles it can go on a full charge.

Write two classes that **inherit from `Bike`** rather than repeating its code.

**`Bike` is already written for you** in `src/from_scratch.py`. Read it before
you start. Its `hourly_rate()` returns `3.00`, the base rate both kinds build
on.

| Class          | `__init__` takes                                | `hourly_rate()` returns   |
| -------------- | ----------------------------------------------- | ------------------------- |
| `ClassicBike`  | serial, station, repair flag                    | The base rate plus `1.00` |
| `ElectricBike` | serial, station, repair flag, **battery_range** | The base rate plus `4.50` |

```python
classic = ClassicBike("A1", "Grand Army", needs_repair=False)
classic.serial                   # "A1" — inherited, you did not write it
classic.is_rentable()            # True — inherited too
classic.hourly_rate()            # 4.0

electric = ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24)
electric.serial                  # "E9" — the parent stored this
electric.battery_range           # 24 miles — only an electric bike has one
electric.hourly_rate()           # 7.5

isinstance(electric, Bike)       # True — an ElectricBike is a Bike
```

Two rules make this inheritance rather than copying:

- Each `hourly_rate()` calls `super().hourly_rate()` to get the base rate and
  adds to it. Neither one writes `3.00`, so changing the base rate in `Bike`
  changes both.
- `ElectricBike.__init__` calls `super().__init__(...)` to let `Bike` store the
  three attributes it already knows how to store, and then stores
  `battery_range` itself.

`ClassicBike` adds no data of its own, so it needs no `__init__` at all.

### Question 4: `Ride`

A ride costs the bike's hourly rate for however long it lasted. Staff sometimes
correct a ride's minutes after the ride ends, and the price has to follow the
correction.

Write a class called `Ride` that has a bike and a number of minutes. It should
answer the question "what does this ride cost?" by working the cost out each
time it is asked, never by storing it.

**`Bike` is already written for you** in `src/from_scratch.py`.

`__init__` takes a `Bike` and a number of minutes, and stores them as
`self.bike` and `self.minutes`.

| Member | Does                                                                                                     | Returns    |
| ------ | -------------------------------------------------------------------------------------------------------- | ---------- |
| `cost` | A `@property` that works out the price from the bike's rate and the minutes, rounded to 2 decimal places | The number |

```python
ride = Ride(Bike("A1", "Grand Army", needs_repair=False), minutes=30)
ride.cost                        # 1.5 — half an hour at $3.00 an hour

ride.minutes = 60
ride.cost                        # 3.0 — the cost followed the correction

ride.cost = 99                   # raises AttributeError
```

The last line is the point of the question. A property with a getter and no
setter cannot be assigned to, so there is no way for a stored cost and a real
cost to drift apart. You do not write the error — Python raises it because you
never wrote a setter.

An hourly rate over a number of minutes is `rate * minutes / 60`. Use
`round(number, 2)` so the result is a price rather than a long float.

### Question 5: Testing Each Kind of Bike

A classic bike costs the base rate plus $1.00 an hour, and an electric bike
costs the base rate plus $4.50. Each kind works out its price in its own
`hourly_rate()`, so one kind can start charging its riders the wrong price
while the other keeps working, and nothing reports an error.

Write two pytest tests that answer the questions "does a classic bike charge
the base rate plus $1.00?" and "does an electric bike charge the base rate plus
$4.50?" Write them in `my_tests/test_bike_rates.py`, which already imports
`ClassicBike` and `ElectricBike` and names both tests for you.

| Write                                     | Does                                                                  |
| ----------------------------------------- | --------------------------------------------------------------------- |
| `test_a_classic_bike_adds_one_dollar()`   | Makes a `ClassicBike` and asserts that its `hourly_rate()` is `4.0`   |
| `test_an_electric_bike_adds_four_fifty()` | Makes an `ElectricBike` and asserts that its `hourly_rate()` is `7.5` |

Run your tests with:

```sh
pytest my_tests
```

Both tests should pass once your `ClassicBike` and `ElectricBike` work. The
assignment's own tests then check your tests twice: once against bikes that
work, where each of your tests must pass, and once against a bike whose
`hourly_rate()` gives the wrong price, where that bike's test must fail. A test
that still passes when the price is wrong would not catch the mistake it is
there to catch.

> Your tests go in `my_tests/` rather than `tests/` because `tests/` is replaced
> with the assignment's own tests when your work is graded, so anything you
> write there is lost.

## Modify

Change the code already in `src/modify.py`.

### Question 6: `Station.capacity`

`Station` stores its capacity in a public attribute, and three places in the
class read `self.capacity`. A rule about the capacity, such as refusing a
capacity below 1, needs one place that runs on every assignment, and only a
property's setter does that. Without a property, the rule would have to be
repeated at every line that assigns to the capacity.

Make the stored value non-public and put it behind a property, **without
changing any of the three lines that read it**.

The class is in `src/modify.py`. When you are done:

- The number is stored in `self._capacity`.
- `capacity` is a `@property` that returns it.
- `dock`, `free_docks` and `__repr__` still say `self.capacity`, exactly as they
  do now.

```python
station = Station("Grand Army", capacity=20)
station.capacity                 # 20 — now going through the property
station.free_docks()             # 20 — this method did not change
station.__dict__                 # {'name': 'Grand Army', '_capacity': 20, 'bikes': []}
```

Check your change by printing `station.__dict__`, which lists the attributes
stored on the instance. `_capacity` should be there and `capacity` should not,
because the property is defined on the class rather than stored on each
instance.

This is the ordinary way an attribute becomes a property in real code. Code
that read `station.capacity` before still reads `station.capacity` and gets the
same number, so none of it has to change. What changed is that reading
`capacity` now runs a method, and that method is where a rule can go later.

Only two places change — the assignment in `__init__` and the new property. If
you find yourself editing `dock`, stop and look again.

### Question 7: `BoroughBike`

`ManhattanBike` and `BrooklynBike` differ only in the string each stores. Each
inherits from `Bike`, calls `super().__init__`, and stores its borough's name.

The borough is a value each bike holds. Replace both classes with the single
`BoroughBike` that is waiting in `src/modify.py`, and make its `__init__` take
the borough as an argument named `borough`.

```python
bike = BoroughBike("A1", "Grand Army", needs_repair=False, borough="Brooklyn")
bike.borough                     # "Brooklyn"
bike.serial                      # "A1" — still inherited from Bike
isinstance(bike, Bike)           # True

BoroughBike("M4", "Union Square", needs_repair=False, borough="Manhattan").borough
# "Manhattan" — one class covers both, and the next borough needs no new class
```

**Delete `ManhattanBike` and `BrooklynBike` when you are done.** A test checks
that they are gone.

A new subclass should be the answer when the new thing **behaves** differently.
When it only holds a different value, a subclass means a new class for every
value anyone ever adds — five boroughs today, and a new class the day Boro
Bikes crosses into Yonkers.

### Question 8: `Ride`

`Ride` inherits from `Bike`. It was written that way because a ride needed the
bike's serial and rate, and inheriting got them. The result is that every ride
**is** a bike: `ride.is_rentable()` returns `True` or `False` as if a ride
could be rented, and `isinstance(ride, Bike)` is `True`. Each ride also stores
its own copy of the bike's serial, station and repair flag, so when the same
bike is taken out twice, a repair flag set on one ride is never seen by the
other.

A ride is not a kind of bike. A ride **has** a bike. Change `Ride` in
`src/modify.py` to hold one instead of inheriting from one.

When you are done, `Ride` takes a `Bike` object and a number of minutes:

```python
bike = Bike("A1", "Grand Army", needs_repair=False)
ride = Ride(bike, minutes=30)

ride.bike is bike                # True — the same object, not a copy
ride.minutes                     # 30
ride.rate()                      # 3.0 — asked of the bike it holds
isinstance(ride, Bike)           # False — a ride is not a bike
```

**Notes**:

- `rate()` still has to work, but it now reaches the bike it holds and asks it: `self.bike.hourly_rate()`.
- The ride no longer stores the serial, the station or the repair flag itself. Code that needs the serial reads it from the bike.
- The test for this one is `isinstance(ride, Bike)` being `False`. That is the
  whole difference between "is a" and "has a", and it is the question to ask
  yourself every time inheritance looks convenient.

## Debug

Fix the code in `src/debug.py`.

### Question 9: `Station.capacity`

`Station` validates its capacity correctly. The rule is right, the error
message is right, and the rule is in the right place. Setting a capacity still
fails:

```python
station = Station("Grand Army", capacity=20)
station.capacity = 25
# RecursionError: maximum recursion depth exceeded
```

The traceback shows the same line of `src/debug.py` a few times, then a line
such as `[Previous line repeated 996 more times]`. Python ran that one line
about a thousand times, until it reached its limit and raised `RecursionError`.
Find the line the traceback repeats, and ask why running it would run it again.

Fix `Station` in `src/debug.py` so this works:

```python
station = Station("Grand Army", capacity=20)
station.capacity = 25
station.capacity                 # 25

station.capacity = 0             # raises ValueError, as it should
station.capacity                 # still 25
```

A property's setter runs **whenever anything assigns to that name on an
instance** — including the setter itself. One word in the last line of the
setter is the difference between storing a value and the setter calling itself
again and again.

This bug is worth meeting here rather than in the project. Once you have seen
the shape of it, a traceback that says `Previous line repeated` becomes the
easiest error in Python to place.

### Question 10: `ElectricBike`

`ElectricBike` inherits from `Bike`, and its `hourly_rate()` works. Reading any
of the three attributes `Bike` is supposed to store does not:

```python
electric = ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24)
electric.battery_range           # 24 — this one works
electric.hourly_rate()           # 7.5 — this works too
electric.serial
# AttributeError: 'ElectricBike' object has no attribute 'serial'
```

The class inherits from `Bike`, so why is the serial missing? Fix
`ElectricBike` in `src/debug.py`.

```python
electric = ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24)
electric.serial                  # "E9"
electric.station                 # "Borough Hall"
electric.is_rentable()           # True
electric.battery_range           # 24
```

Inheriting gets you the parent's **methods**. It does not run the parent's
`__init__` for you. Writing your own `__init__` in a subclass replaces the
parent's completely, and the attributes it would have stored are simply never
stored — which is why `is_rentable()` is inherited and present, but `serial` is
not.

Add one line, and leave `hourly_rate()` alone.

## Submitting

```sh
git add -A
git commit -m "your message"
git push
```

Pushing runs the tests on GitHub. Check the **Actions** tab to see which
passed, then open a pull request to your instructor for feedback.

## Good luck!

Every system you build from here is made of classes, so this is the
assignment the rest of the module stands on. You got this!
