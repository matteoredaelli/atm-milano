.PHONY: sync license lint fmt typecheck test test-live check build mcp clean

LICENSE_HOLDER := Matteo Redaelli
LICENSE_YEAR   := 2026

sync:
	uv sync --all-packages

license:
	uv run addlicense -f scripts/license-header.tmpl -c "$(LICENSE_HOLDER)" -y $(LICENSE_YEAR) \
		-ignore '.venv/**' -ignore 'dist/**' -ignore '**/fixtures/**' -ignore '**/*.md' \
		-ignore '**/*.json' -ignore '**/*.toml' -ignore '**/*.yml' -ignore 'uv.lock' \
		-ignore '.python-version' -ignore 'LICENSE' -ignore '**/_version.py' .

lint:
	uv run ruff check .
	uv run ruff format --check .

fmt:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run pyright

test:
	uv run pytest

test-live:
	uv run pytest -m live

check: lint typecheck test

build:
	rm -rf dist
	uv build --all-packages

mcp:
	uv run atm-milano-mcp

clean:
	rm -rf dist .pytest_cache .ruff_cache .venv
	find . -name __pycache__ -prune -exec rm -rf {} +
