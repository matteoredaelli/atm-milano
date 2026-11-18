# Copyright (C) 2026 Matteo Redaelli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from atm_milano import AtmBlockedError, AtmClient, AtmNotFoundError
from atm_milano.client import _normalize_line

FIX = Path(__file__).parent / "fixtures"


class FakeSession:
    def __init__(self, routes: dict[str, tuple[int, object]]):
        self.routes, self.calls = routes, []

    async def request(self, method, url, params=None, **_):
        self.calls.append((method, url, params))
        for key, (status, body) in self.routes.items():
            if key in url:
                return SimpleNamespace(status_code=status, json=lambda b=body: b)
        raise AssertionError(f"unexpected {url}")

    async def close(self): ...


def fx(name):
    return json.loads((FIX / name).read_text())


async def test_search_and_geocode_flow():
    s = FakeSession({"/search": (200, fx("search.json")), "/Geocode": (200, fx("geocode.json"))})
    c = AtmClient(session=s)
    res = await c.search_places("cadorna")
    addr = next(p for p in res.places if not p.has_coordinates)
    full = await c.geocode(addr)
    assert full.lat is not None and 45 < full.lat < 46


async def test_plan_trip_with_coordinates():
    s = FakeSession({"/tpl/trips": (200, fx("trips.json"))})
    plan = await AtmClient(session=s).plan_trip((45.468, 9.1759), (45.495, 9.2162))
    assert plan.trips and s.calls[0][2]["TransportModes"] == "Metro,Bus,Tram,Rail"


async def test_blocked_and_not_found():
    with pytest.raises(AtmBlockedError):
        await AtmClient(session=FakeSession({"journeyPatterns": (403, {})})).get_line_route("1")
    with pytest.raises(AtmNotFoundError):
        await AtmClient(session=FakeSession({"journeyPatterns": (404, {})})).get_line_route("zz")


async def test_metro_stations_filter():
    gis = {**fx("metro.json"), "exceededTransferLimit": False}
    s = FakeSession({"gisportal": (200, gis)})
    all_ = await AtmClient(session=s).list_metro_stations()
    assert all_
    only = await AtmClient(session=s).list_metro_stations("M4")
    assert all("4" in x.lines for x in only)


def test_line_alias():
    assert _normalize_line("m2") == "-2" and _normalize_line("90") == "90"


@pytest.mark.live
async def test_live_search():
    async with AtmClient() as c:
        assert (await c.search_places("duomo")).places
