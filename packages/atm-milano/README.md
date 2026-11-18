# atm-milano

Async client for ATM Milano (GiroMilano) with pydantic models. Unofficial; endpoints may change.

```
pip install atm-milano
```

## API (`AtmClient`)

| Method | Returns | Description |
|---|---|---|
| `search_places(term, kinds=, limit=)` | `SearchResults` | Addresses, localities, POIs (stations, stops) |
| `geocode(place)` | `Place` | Add coordinates to an address result |
| `resolve_place(ref)` | `Place` | Text, `Place` or `(lat, lng)` → place with coordinates |
| `plan_trip(origin, destination, when=, modes=)` | `TripPlan` | Public-transport trips (default: now, Europe/Rome) |
| `get_line_route(line, direction=0)` | `LineRoute` | Ordered stops of a line (`M1`..`M5`, `90`, `15`...) |
| `get_stop_lines(stop_code)` | `StopLines` | Lines at a stop with live wait times |
| `get_stop_timetable(stop_code, line, direction=0)` | `Timetable` | Scheduled times by day type and hour |
| `list_metro_stations(line=None)` | `list[MetroStation]` | Metro stations (Comune di Milano GIS) |

Errors: `AtmError` → `AtmBlockedError`, `AtmNotFoundError`, `AtmApiError`.

## Examples

```python
import asyncio
from datetime import datetime
from atm_milano import AtmClient, TransportMode


async def main():
    async with AtmClient(lang="en") as c:
        places = await c.search_places("Cadorna")
        print(places.places[0].name, places.places[0].code)

        plan = await c.plan_trip(
            "Cadorna",
            "Stazione Centrale",
            when=datetime(2026, 11, 20, 9, 30),
            modes=[TransportMode.METRO],
        )
        trip = plan.trips[0]
        print(trip.duration_minutes, "min", [s.description for s in trip.steps])

        route = await c.get_line_route("M1", direction=0)
        print(route.description, len(route.stops), "stops")

        stop = await c.get_stop_lines("-51")  # Cadorna M1
        print([(a.line_code, a.wait) for a in stop.arrivals])

        tt = await c.get_stop_timetable("12254", "1")  # tram 1 at Greco Rovereto
        print(tt.schedules[0].day_type)

        print(len(await c.list_metro_stations("M2")), "M2 stations")


asyncio.run(main())
```

Origins/destinations accept free text, a `Place`, or a `(lat, lng)` tuple.
