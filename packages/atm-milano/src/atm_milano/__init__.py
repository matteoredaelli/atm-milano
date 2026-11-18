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

"""Async client for ATM Milano (GiroMilano) public data."""

from .client import AtmClient
from .errors import AtmApiError, AtmBlockedError, AtmError, AtmNotFoundError
from .models import (
    Fare,
    LineRoute,
    LineStop,
    MetroStation,
    Place,
    PlaceKind,
    Ride,
    SearchResults,
    StepType,
    StopArrival,
    StopLines,
    Timetable,
    TransportMode,
    Trip,
    TripPlan,
    TripStep,
    Waypoint,
)

__all__ = [
    "AtmApiError",
    "AtmBlockedError",
    "AtmClient",
    "AtmError",
    "AtmNotFoundError",
    "Fare",
    "LineRoute",
    "LineStop",
    "MetroStation",
    "Place",
    "PlaceKind",
    "Ride",
    "SearchResults",
    "StepType",
    "StopArrival",
    "StopLines",
    "Timetable",
    "TransportMode",
    "Trip",
    "TripPlan",
    "TripStep",
    "Waypoint",
]
