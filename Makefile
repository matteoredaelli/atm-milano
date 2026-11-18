.PHONY: sync lint fmt typecheck test test-live check build mcp clean
sync:        ; uv sync --all-packages
lint:        ; uv run ruff check . && uv run ruff format --check .
fmt:         ; uv run ruff check --fix . && uv run ruff format .
typecheck:   ; uv run ty check packages
test:        ; uv run pytest
test-live:   ; uv run pytest -m live
check: lint typecheck test
build:       ; rm -rf dist && uv build --all-packages
mcp:         ; uv run atm-milano-mcp
clean:       ; rm -rf dist .pytest_cache .ruff_cache .venv; find . -name __pycache__ -prune -exec rm -rf {} +

.PHONY: license
license:     ; addlicense -f scripts/license-header.tmpl -c "Matteo Redaelli" -y 2026 -ignore '.venv/**' -ignore 'dist/**' -ignore '**/fixtures/**' -ignore '**/*.md' -ignore '**/*.json' -ignore '**/*.toml' -ignore '**/*.yml' -ignore 'uv.lock' -ignore '.python-version' -ignore 'LICENSE' .
