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
