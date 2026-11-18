import json
from pathlib import Path

import pytest
from atm_milano import (
    LineRoute,
    Place,
    PlaceKind,
    StepType,
    StopLines,
    Timetable,
    TripPlan,
)
from atm_milano.models import Trip

FIX = Path(__file__).parent / "fixtures"


def load(name: str):
    return json.loads((FIX / name).read_text())


def test_search_places_zero_coords_become_none():
    rows = load("search.json")["rows"]
    places = [Place.model_validate(r) for r in rows]
    addr = next(p for p in places if p.kind is PlaceKind.ADDRESS)
    assert addr.lat is None and not addr.has_coordinates
    poi = next(p for p in places if p.code == "-51")
    assert poi.has_coordinates and poi.category == "Underground station"


def test_trip_parsing():
    trips = [Trip.model_validate(t) for t in load("trips.json")["Trips"]]
    t = trips[0]
    assert t.steps[0].type is StepType.DEPART
    ride = next(s for s in t.steps if s.type is StepType.RIDE)
    assert ride.rides[0].line_code == "M1"
    assert ride.rides[0].stops_on_board == 10
    assert t.fare and t.fare.price_eur == pytest.approx(2.2)
    assert TripPlan(trips=trips).trips


def test_line_route():
    r = LineRoute.model_validate(load("journey_pattern.json"))
    assert r.line_code == "-1" and len(r.stops) > 10
    assert r.stops[0].lat > 45


def test_stop_lines_and_timetable():
    s = StopLines.model_validate(load("line_summary.json"))
    assert s.stop_code == "12254" and s.arrivals[0].line_code == "1"
    tt = Timetable.model_validate(load("timetable.json"))
    assert tt.schedules[0].days and tt.schedules[0].slots
