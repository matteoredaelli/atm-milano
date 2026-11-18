# atm-milano

Unofficial Python tools for Milan public transport (ATM / GiroMilano).

- [`atm-milano`](packages/atm-milano): async client with pydantic models
- [`atm-milano-mcp`](packages/atm-milano-mcp): FastMCP server built on it

```json
{ "mcpServers": { "atm-milano": { "command": "uvx", "args": ["atm-milano-mcp"] } } }
```

`uvx` caches the version; upgrade with `uvx --upgrade atm-milano-mcp --help` or use `atm-milano-mcp@latest` in `args`.

Dev: `make sync`, `make check`, `make build`. Release: tag `vX.Y.Z` (version comes from the tag, both packages).

Not affiliated with ATM; uses undocumented endpoints that may change.

License: GPL-3.0-or-later.
