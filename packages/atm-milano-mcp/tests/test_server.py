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

from atm_milano_mcp.server import _ref, mcp
from fastmcp import Client


def test_ref():
    assert _ref("45.46, 9.19") == (45.46, 9.19)
    assert _ref("Duomo") == "Duomo"


async def test_tools_listed_with_output_schema():
    async with Client(mcp) as c:
        tools = {t.name: t for t in await c.list_tools()}
    assert {"search_places", "plan_trip", "get_line_route", "get_stop_lines"} <= set(tools)
    assert tools["plan_trip"].output_schema
