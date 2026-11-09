# Properties and Inheritance

Put a rule behind an attribute so it cannot be set to nonsense, and let one class build on another.

**Practicing:** non-public attributes, `@property`, validating setters, class attributes, inheritance, `super()`, overriding a method

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
- [Modify](#modify)
  - [Question 5: `Station.capacity`](#question-5-stationcapacity)
  - [Question 6: `BoroughBike`](#question-6-boroughbike)
  - [Question 7: `Ride`](#question-7-ride)
- [Debug](#debug)
  - [Question 8: `Station.capacity`](#question-8-stationcapacity)
  - [Question 9: `ElectricBike`](#question-9-electricbike)
- [Submitting](#submitting)
- [Good luck!](#good-luck)

## AI Use on This Assignment

**Tutor mode, for this whole quarter.** The AI explains, questions, quizzes,
and critiques, and you write every line you submit. Quarter 1 is where you
build the habit of writing code by hand; asking an AI to write it for you
comes later, in Quarter 2, where the job becomes judging code rather than
producing it.

For this assignment that means asking it why a setter that assigns to
`self.capacity` calls itself forever, or having it quiz you on what
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

| Idea | Lesson |
| --- | --- |
| A single leading underscore, as in `self._capacity`, tells another programmer that this attribute is not part of the class's public interface. It prevents nothing. It is a message, and Python does not enforce it. | 2.3 |
| A `@property` makes a method readable like an attribute: `station.capacity`, with no parentheses. The caller cannot tell the difference, which is why an attribute can become a property without changing the code that reads it. | 2.3 |
| A setter runs whenever anything assigns to that name on an instance, including code inside the setter itself. It is the one place a rule about the value belongs. | 2.3 |
| Raise `ValueError` to refuse a value, and raise it **before** storing anything, so a refused assignment leaves the old value exactly as it was. | 2.3 |
| A property with a getter and no setter cannot be assigned to. That is how you make a value that is always computed and never stored. | 2.3 |
| A value assigned in the class body, written in capitals by convention, belongs to the class and is shared by every instance. Read it through the class name, so the value appears once. | 2.3 |
| A subclass inherits the parent's methods, so it can use them without rewriting them. Writing `class ElectricBike(Bike):` is the whole mechanism. | 2.4 |
| Inheriting does **not** run the parent's `__init__`. A subclass that writes its own `__init__` replaces the parent's and must call `super().__init__(...)` itself. | 2.4 |
| Overriding means defining a method the parent already has. `super().method()` calls the parent's version, so the subclass can extend an answer instead of replacing it. | 2.4 |
| Inheritance is for "is a". Composition — holding another object as an attribute — is for "has a". A ride is not a kind of bike, so `Ride` holds a `Bike`. | 2.4 |
| Two subclasses that differ only by a stored value should be one class that takes that value as an argument. A subclass is for different behavior, not for different data. | 2.4 |

</details>

### Syntax to recognize

```python
class Station:
    MIN_DOCKS = 1                        # a class attribute: shared by all

    def __init__(self, name, capacity):
        self._capacity = capacity        # non-public: not part of the
interface

    @property
    def capacity(self):                  # read as station.capacity
        return self._capacity

    @capacity.setter
    def capacity(self, value):           # runs on station.capacity = 25
        if value < 1:
            raise ValueError("...")      # refuse before storing
        self._capacity = value           # NOT self.capacity, that recurses


class ElectricBike(Bike):                # inherit from Bike
    def __init__(self, serial, station, needs_repair, battery_range):
        super().__init__(serial, station, needs_repair)   # run the parent's
        self.battery_range = battery_range

    def hourly_rate(self):               # override
        return super().hourly_rate() + 4.50   # extend the parent's answer
```

### Look these up yourself

- `isinstance()`. The tests use it to check your inheritance is real, and two
  questions talk about it. Read about it on
  [W3Schools](https://www.w3schools.com/python/ref_func_isinstance.asp).
- `round()`. One question asks for a price rounded to two decimal places. Read
  about it on
  [W3Schools](https://www.w3schools.com/python/ref_func_round.asp).

## From Scratch

Write these functions and classes in `src/from_scratch.py`.

### Question 1: `Station`

A station's capacity is the number of docks it has. Last week someone set a
station's capacity to `0` through a script, the station accepted it, and the
app spent a day reporting that a station with eight bikes in it had nowhere to
put them.

Write a class `Station` that will not accept a capacity below 1.

**`Bike` is already written for you** in `src/from_scratch.py`.

`__init__` takes a station name and a capacity. Store the name as `self.name`.
Store the capacity in a **non-public attribute** called `self._capacity`, and
start an empty list of bikes on the instance.

| Member | Does | Returns |
| --- | --- | --- |
| `capacity` | Reads the stored capacity. A `@property`, so callers write `station.capacity` with no parentheses | The number |
| `capacity` setter | Replaces the capacity, but raises `ValueError` if the new value is below 1 | Nothing |
| `dock(bike)` | Puts one `Bike` at this station | Nothing |
| `free_docks()` | How many docks are still empty | The number |

```python
station = Station("Grand Army", 20)
station.capacity                 # 20 — no parentheses, it is a property
station.free_docks()             # 20

station.dock(Bike("A1", "Grand Army", False))
station.free_docks()             # 19

station.capacity = 25            # allowed, this goes through the setter
station.capacity                 # 25

station.capacity = 0             # raises ValueError
station.capacity                 # still 25 — a refused assignment changes nothing
```

The setter has one job: decide, then either store or refuse. When it refuses it
raises `ValueError` with a message that says what the rule is, and the stored
value stays exactly as it was.

Assign to `self.capacity` inside `__init__` rather than to `self._capacity`, and
`__init__` gets the rule checked for free.

### Question 2: `Member`

Every Boro Bikes member may borrow three bikes at once. Not three because of
anything about them — three because that is the company's rule. Today that
number is written into four different files, and raising it to four means
finding all four.

Write a class `Member` that keeps the limit in one place: on the class itself.

`__init__` takes a member's name, stores it on the instance, and starts an
empty list of bikes they are holding.

| Member | Does | Returns |
| --- | --- | --- |
| `BORROW_LIMIT` | A **class attribute** set to `3`, written in the class body rather than in `__init__` | The number |
| `borrow(bike)` | Adds a bike if the member is under the limit, and raises `ValueError` if they are already at it | Nothing |
| `can_borrow()` | Whether this member is under the limit right now | `True` or `False` |

```python
Member.BORROW_LIMIT              # 3 — read off the class, no instance needed

ana = Member("Ana")
ana.can_borrow()                 # True
ana.borrow(Bike("A1", "Grand Army", False))
len(ana.bikes)                   # 1

Member("Ben").can_borrow()       # True — Ben has his own empty list
```

Read the limit as `Member.BORROW_LIMIT` inside your methods, not as a bare `3`.
The point of the class attribute is that the number appears once.

The capital letters are a convention: they tell another programmer this value is
a fixed setting, not something that changes per member.

### Question 3: `ClassicBike` and `ElectricBike`

Boro Bikes now rents two kinds of bike. Both have a serial, a station and a
repair flag, and both can be rented — all of that is already true of a `Bike`.
What differs is the price, and an electric bike also knows how far it can go on
its charge.

Write two classes that **inherit from `Bike`** rather than repeating it.

**`Bike` is already written for you** in `src/from_scratch.py`. Read it before
you start. Its `hourly_rate()` returns `3.00`, the base rate both kinds build
on.

| Class | `__init__` takes | `hourly_rate()` returns |
| --- | --- | --- |
| `ClassicBike` | serial, station, repair flag | The base rate plus `1.00` |
| `ElectricBike` | serial, station, repair flag, **battery_range** | The base rate plus `4.50` |

```python
classic = ClassicBike("A1", "Grand Army", False)
classic.serial                   # "A1" — inherited, you did not write it
classic.is_rentable()            # True — inherited too
classic.hourly_rate()            # 4.0

electric = ElectricBike("E9", "Borough Hall", False, 24)
electric.serial                  # "E9" — the parent stored this
electric.battery_range           # 24 — only an electric bike has one
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

A ride costs the bike's hourly rate for however long it lasted. Right now the
app stores that cost on the ride when it ends, which means a ride whose minutes
are corrected keeps the old price, and the two disagree forever.

Write a class `Ride` that never stores the cost, and works it out when asked.

**`Bike` is already written for you** in `src/from_scratch.py`.

`__init__` takes a `Bike` and a number of minutes, and stores both on the
instance.

| Member | Does | Returns |
| --- | --- | --- |
| `cost` | A `@property` that works out the price from the bike's rate and the minutes, rounded to 2 decimal places | The number |

```python
ride = Ride(Bike("A1", "Grand Army", False), 30)
ride.cost                        # 1.5 — half an hour at 3.00 an hour

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

## Modify

Change the code already in `src/modify.py`.

### Question 5: `Station.capacity`

`Station` stores its capacity in a public attribute, and three places in the
class read `self.capacity`. That is fine until the day a rule has to apply to
it, and then there is no single place to put the rule.

Make the stored value non-public and put a property in front of it, **without
changing any of the three lines that read it**.

The class is in `src/modify.py`. When you are done:

- The number is stored in `self._capacity`.
- `capacity` is a `@property` that returns it.
- `dock`, `free_docks` and `__repr__` still say `self.capacity`, exactly as they
  do now.

```python
station = Station("Grand Army", 20)
station.capacity                 # 20 — now going through the property
station.free_docks()             # 20 — this method did not change
vars(station)                    # {'name': ..., 'bikes': [], '_capacity': 20}
```

This is the ordinary way an attribute becomes a property in real code: the
callers never find out. They were already asking the object for its capacity,
and they still are. What changed is that the object now gets to decide how to
answer.

Only two lines change — the assignment in `__init__` and the new property. If
you find yourself editing `dock`, stop and look again.

### Question 6: `BoroughBike`

`ManhattanBike` and `BrooklynBike` are identical. Each inherits from `Bike`,
each calls `super().__init__`, and each stores one string. The only difference
between the two classes is which string.

The borough is **data**, not behavior. Replace both classes with the single
`BoroughBike` that is waiting in `src/modify.py`, and take a borough as an
argument.

```python
bike = BoroughBike("A1", "Grand Army", False, "Brooklyn")
bike.borough                     # "Brooklyn"
bike.serial                      # "A1" — still inherited from Bike
isinstance(bike, Bike)           # True

BoroughBike("M4", "Union Square", False, "Manhattan").borough
# "Manhattan" — one class covers both, and the next borough needs no new class
```

**Delete `ManhattanBike` and `BrooklynBike` when you are done.** Leaving them in
place is not finishing the job, and a test checks they are gone.

A new subclass should be the answer when the new thing **behaves** differently.
When it only holds a different value, a subclass means a new class for every
value anyone ever adds — five boroughs today, and a new class the day Boro
Bikes crosses into Yonkers.

### Question 7: `Ride`

`Ride` inherits from `Bike`. It was written that way because a ride needed the
bike's serial and rate, and inheriting got them. The result is that every ride
**is** a bike: `ride.is_rentable()` answers, `isinstance(ride, Bike)` is `True`,
and the same bike taken out twice becomes two unrelated objects that each think
they are a bike.

A ride is not a kind of bike. A ride **has** a bike. Change `Ride` in
`src/modify.py` to hold one instead of inheriting from one.

When you are done, `Ride` takes a `Bike` object and a number of minutes:

```python
bike = Bike("A1", "Grand Army", False)
ride = Ride(bike, 30)

ride.bike is bike                # True — the same object, not a copy
ride.minutes                     # 30
ride.rate()                      # 3.0 — asked of the bike it holds
isinstance(ride, Bike)           # False — a ride is not a bike
```

`rate()` still has to work, but it now reaches the bike it holds and asks it:
`self.bike.hourly_rate()`.

The test for this one is `isinstance(ride, Bike)` being `False`. That is the
whole difference between "is a" and "has a", and it is the question to ask
yourself every time inheritance looks convenient.

## Debug

Fix the code in `src/debug.py`.

### Question 8: `Station.capacity`

`Station` validates its capacity correctly. The rule is right, the error
message is right, and the rule is in the right place. Setting a capacity still
fails:

```python
station = Station("Grand Army", 20)
station.capacity = 25
# RecursionError: maximum recursion depth exceeded
```

The traceback for this is about a thousand lines long and every line is the
same two lines repeating. Do not read all of it. Read the **first** frame and
the **last**, notice they are the same line of your code, and ask what that
means.

Fix `Station` in `src/debug.py` so this works:

```python
station = Station("Grand Army", 20)
station.capacity = 25
station.capacity                 # 25

station.capacity = 0             # raises ValueError, as it should
station.capacity                 # still 25
```

A property's setter runs **whenever anything assigns to that name on an
instance** — including the setter itself. One word in the last line of the
setter is the difference between storing a value and calling yourself forever.

This bug is worth meeting here rather than in the project. Once you have seen
the shape of it, a thousand-line traceback that repeats becomes the easiest
error in Python to place.

### Question 9: `ElectricBike`

`ElectricBike` inherits from `Bike`, and its `hourly_rate()` works. Reading any
of the three attributes `Bike` is supposed to store does not:

```python
electric = ElectricBike("E9", "Borough Hall", False, 24)
electric.battery_range           # 24 — this one works
electric.hourly_rate()           # 7.5 — this works too
electric.serial
# AttributeError: 'ElectricBike' object has no attribute 'serial'
```

The class inherits from `Bike`, so why is the serial missing? Fix
`ElectricBike` in `src/debug.py`.

```python
electric = ElectricBike("E9", "Borough Hall", False, 24)
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
