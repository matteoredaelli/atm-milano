# atm-milano-mcp

<!-- mcp-name: io.github.matteoredaelli/atm-milano-mcp -->

MCP server for Milan public transport, built on [`atm-milano`](https://pypi.org/project/atm-milano/).

```json
{ "mcpServers": { "atm-milano": { "command": "uvx", "args": ["atm-milano-mcp"] } } }
```

`uvx` caches the installed version. To upgrade run `uvx --upgrade atm-milano-mcp --help` once, or use
`"args": ["atm-milano-mcp@latest"]` to always check for the newest release at startup.

## Tools

| Tool | Arguments | Description |
|---|---|---|
| `search_places` | `query`, `kinds?`, `limit?` | Find addresses, localities, stations, stops |
| `plan_trip` | `origin`, `destination`, `depart_at?`, `modes?` | Plan trips; places as free text or `"lat,lng"` |
| `get_line_route` | `line`, `direction?` | Ordered stops of a line (`M1`..`M5`, `90`, `15`...) |
| `get_stop_lines` | `stop_code` | Lines at a stop with live waits (e.g. `"5 min"`) |
| `get_stop_timetable` | `stop_code`, `line`, `direction?` | Scheduled times by day type and hour |
| `list_metro_stations` | `line?` | Metro stations with coordinates |

Example prompt: *"How do I get from Cadorna to Stazione Centrale leaving at 9:30?"*
