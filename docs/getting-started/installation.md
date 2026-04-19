# Installation

## Requirements

- Python `>=3.13`
- `uv` or `pip`

## Install (Development)

Using `uv`:

```bash
uv sync --all-groups
```

Using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Validate Environment

```bash
pytest -q
```

If tests pass, your local environment is ready.
