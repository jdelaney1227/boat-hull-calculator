from bakery import assert_equal
from drafter import *
from dataclasses import dataclass

FRESH_DENSITY = 62.4  # pounds per cubic foot
SALT_DENSITY = 64.0
SPEED_FACTOR = 1.34   # hull speed (knots) = factor * sqrt(waterline ft)


@dataclass
class Hull:
    """One boat hull and its calculated results."""
    name: str
    length: float
    beam: float
    weight: float
    speed: float
    draft: float


@dataclass
class State:
    """Everything the site remembers between pages."""
    hulls: list[Hull]
    water_type: str
    message: str
    adds_count: int


def water_density(water_type: str) -> float:
    """Return water density in lb/ft^3 for 'Salt' or 'Fresh' water."""
    if water_type == "Salt":
        return SALT_DENSITY
    return FRESH_DENSITY


def hull_speed(length: float) -> float:
    """Return approximate hull speed in knots from waterline length."""
    return SPEED_FACTOR * length ** 0.5


def hull_draft(weight: float, length: float, beam: float,
               density: float) -> float:
    """Return how deep a box-shaped hull sits, in feet."""
    return weight / (density * length * beam)


def is_positive_number(text: str) -> bool:
    """Return True if text is a number greater than zero."""
    cleaned = text.replace(".", "", 1)
    return cleaned.isdigit() and float(text) > 0


def fastest_hull(hulls: list[Hull]) -> str:
    """Return the name of the fastest hull, or '' if the list is empty."""
    best_name = ""
    best_speed = 0.0
    for hull in hulls:
        if hull.speed > best_speed:
            best_speed = hull.speed
            best_name = hull.name
    return best_name


def total_weight(hulls: list[Hull]) -> float:
    """Return the combined weight of all hulls."""
    total = 0.0
    for hull in hulls:
        total += hull.weight
    return total


@route
def index(state: State) -> Page:
    """Home page."""
    return Page(state, [
        Header("Hull Comparison Notebook"),
        "Compare boat hulls by speed and draft.",
        state.message,
        Button("Add a hull", add_page),
        Button("See my hulls", fleet),
        Button("Summary", summary),
        Button("Water settings", settings),
    ])


@route
def add_page(state: State) -> Page:
    """Form for entering a new hull."""
    return Page(state, [
        Header("Add a Hull"),
        "Name", TextBox("name", "Hull " + str(state.adds_count + 1)),
        "Waterline length (ft)", TextBox("length", "25"),
        "Beam (ft)", TextBox("beam", "8"),
        "Weight (lb)", TextBox("weight", "3200"),
        Button("Add", add_hull),
        Button("Cancel", index),
    ])


@route
def add_hull(state: State, name: str, length: str, beam: str,
             weight: str) -> Page:
    """Validate the form, then store a new Hull in the state."""
    if not (is_positive_number(length) and is_positive_number(beam)
            and is_positive_number(weight)):
        state.message = "Length, beam, and weight must be positive numbers."
        return index(state)
    length_ft = float(length)
    beam_ft = float(beam)
    weight_lb = float(weight)
    density = water_density(state.water_type)
    new_hull = Hull(name, length_ft, beam_ft, weight_lb,
                    hull_speed(length_ft),
                    hull_draft(weight_lb, length_ft, beam_ft, density))
    state.hulls.append(new_hull)
    state.adds_count += 1
    state.message = "Added " + name + "."
    return fleet(state)


@route
def fleet(state: State) -> Page:
    """List every hull that has been added."""
    content = [Header("My Hulls"), state.message]
    if len(state.hulls) == 0:
        content.append("No hulls yet.")
    for hull in state.hulls:
        content.append(f"{hull.name}: {hull.speed:.1f} knots, "
                       f"draft {hull.draft:.2f} ft")
    content.append(Button("Remove last hull", remove_last))
    content.append(Button("Home", index))
    return Page(state, content)


@route
def remove_last(state: State) -> Page:
    """Delete the most recently added hull."""
    if len(state.hulls) > 0:
        removed = state.hulls.pop()
        state.message = "Removed " + removed.name + "."
    else:
        state.message = "Nothing to remove."
    return fleet(state)


@route
def settings(state: State) -> Page:
    """Choose salt or fresh water."""
    return Page(state, [
        Header("Water Settings"),
        "Current: " + state.water_type,
        SelectBox("water", ["Salt", "Fresh"], state.water_type),
        Button("Save", set_water),
    ])


@route
def set_water(state: State, water: str) -> Page:
    """Save the chosen water type."""
    state.water_type = water
    state.message = "Water set to " + water + " (applies to new hulls)."
    return index(state)


@route
def summary(state: State) -> Page:
    """Show the fastest hull and total weight."""
    if len(state.hulls) == 0:
        state.message = "Add a hull first."
        return index(state)
    return Page(state, [
        Header("Summary"),
        "Fastest hull: " + fastest_hull(state.hulls),
        f"Total weight: {total_weight(state.hulls):.0f} lb",
        Button("Home", index),
    ])


# Unit tests for the helper functions
assert_equal(hull_speed(25.0), 6.7)
assert_equal(hull_draft(3200.0, 25.0, 8.0, 64.0), 0.25)
assert_equal(is_positive_number("12.5"), True)
assert_equal(is_positive_number("-3"), False)
assert_equal(is_positive_number("abc"), False)
assert_equal(water_density("Salt"), 64.0)
assert_equal(total_weight([Hull("a", 1, 1, 100, 1, 1),
                           Hull("b", 1, 1, 50, 1, 1)]), 150.0)
assert_equal(fastest_hull([]), "")

set_site_information(
    author="jackdel@udel.edu",
    description="Compare boat hulls by speed and draft.",
    sources=["https://en.wikipedia.org/wiki/Hull_speed"],
    planning="planning.pdf",
    links=[https://github.com/jdelaney1227/boat-hull-calculator],
)
start_server(State([], "Salt", "", 0))
