# atm-milano-mcp

MCP server for Milan public transport, built on [`atm-milano`](https://pypi.org/project/atm-milano/).

```json
{ "mcpServers": { "atm-milano": { "command": "uvx", "args": ["atm-milano-mcp"] } } }
```

`uvx` caches the installed version. To upgrade run `uvx --upgrade atm-milano-mcp --help` once, or use
`"args": ["atm-milano-mcp@latest"]` to always check for the newest release at startup.

Tools: `search_places`, `plan_trip`, `get_line_route`, `get_stop_lines`, `get_stop_timetable`, `list_metro_stations`.
