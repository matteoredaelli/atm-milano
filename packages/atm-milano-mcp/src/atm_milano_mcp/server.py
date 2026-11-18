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

"""FastMCP server. Tool signatures/returns reuse the `atm_milano` pydantic models directly."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from atm_milano import (
    AtmClient,
    AtmError,
    LineRoute,
    MetroStation,
    PlaceKind,
    SearchResults,
    StopLines,
    Timetable,
    TransportMode,
    TripPlan,
)
from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

_client: AtmClient | None = None


@asynccontextmanager
async def _lifespan(_: FastMCP) -> AsyncGenerator[None]:
    global _client
    _client = AtmClient()
    try:
        yield
    finally:
        await _client.aclose()
        _client = None


mcp = FastMCP(
    "atm-milano",
    instructions=(
        "Public transport in Milan (ATM). Use search_places to find stations/addresses, "
        "plan_trip for routes (accepts free text or 'lat,lng'), get_stop_lines for live waits. "
        "Metro lines can be passed as M1..M5."
    ),
    lifespan=_lifespan,
)


def _c() -> AtmClient:
    if _client is None:  # e.g. tests calling tools without the lifespan
        raise ToolError("Client not initialised")
    return _client


def _ref(value: str) -> str | tuple[float, float]:
    """'45.46,9.19' -> coordinate tuple; anything else stays a text query."""
    parts = value.split(",")
    if len(parts) == 2:
        try:
            return float(parts[0]), float(parts[1])
        except ValueError:
            pass
    return value


async def _run[T](coro) -> T:
    try:
        return await coro
    except AtmError as e:
        raise ToolError(f"{type(e).__name__}: {e}") from e


READ_ONLY = {"readOnlyHint": True, "openWorldHint": True}


@mcp.tool(annotations=READ_ONLY)
async def search_places(
    query: Annotated[str, Field(description="Address, locality or POI name, e.g. 'Cadorna'")],
    kinds: Annotated[list[PlaceKind] | None, Field(description="Restrict result kinds")] = None,
    limit: Annotated[int, Field(ge=1, le=30)] = 10,
) -> SearchResults:
    """Search Milan addresses, localities and points of interest (metro/rail stations, stops)."""
    k = tuple(kinds) if kinds else (PlaceKind.ADDRESS, PlaceKind.LOCALITY, PlaceKind.POI)
    return await _run(_c().search_places(query, limit=limit, kinds=k))


@mcp.tool(annotations=READ_ONLY)
async def plan_trip(
    origin: Annotated[str, Field(description="Free text ('Stazione Centrale') or 'lat,lng'")],
    destination: Annotated[str, Field(description="Free text or 'lat,lng'")],
    depart_at: Annotated[
        datetime | None,
        Field(description="ISO 8601 departure time; naive = Europe/Rome. Default: now"),
    ] = None,
    modes: Annotated[
        list[TransportMode] | None, Field(description="Default: Metro, Bus, Tram, Rail")
    ] = None,
    ctx: Context | None = None,
) -> TripPlan:
    """Plan public-transport trips between two places in the Milan area."""
    m = tuple(modes) if modes else tuple(TransportMode)
    return await _run(_c().plan_trip(_ref(origin), _ref(destination), when=depart_at, modes=m))


@mcp.tool(annotations=READ_ONLY)
async def get_line_route(
    line: Annotated[str, Field(description="'M1'..'M5', or bus/tram number like '90', '15'")],
    direction: Annotated[int, Field(ge=0, le=1)] = 0,
) -> LineRoute:
    """Ordered stops (with coordinates) of a line in one direction."""
    return await _run(_c().get_line_route(line, direction))


@mcp.tool(annotations=READ_ONLY)
async def get_stop_lines(
    stop_code: Annotated[str, Field(description="Stop code, e.g. '-51' or '12254'")],
) -> StopLines:
    """Lines serving a stop with live wait messages (e.g. '5 min')."""
    return await _run(_c().get_stop_lines(stop_code))


@mcp.tool(annotations=READ_ONLY)
async def get_stop_timetable(
    stop_code: str,
    line: Annotated[str, Field(description="'M1'..'M5' or bus/tram number")],
    direction: Annotated[int, Field(ge=0, le=1)] = 0,
) -> Timetable:
    """Scheduled timetable of a line at a stop, by day type and hour."""
    return await _run(_c().get_stop_timetable(stop_code, line, direction))


@mcp.tool(annotations=READ_ONLY)
async def list_metro_stations(
    line: Annotated[str | None, Field(description="Filter by line, e.g. 'M2'")] = None,
) -> list[MetroStation]:
    """Metro stations with coordinates (source: Comune di Milano open GIS)."""
    return await _run(_c().list_metro_stations(line))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
