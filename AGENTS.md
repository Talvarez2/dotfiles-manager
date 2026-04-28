# AGENTS.md

## Project Overview

Python CLI tool (`dotman`) for managing dotfiles across machines using symlinks and git.

## Tech Stack

- Python 3.7+, Click CLI, TOML config, pytest
- Package layout: `src/dotman/` with `cli.py`, `config.py`, `linker.py`

## Architecture

- `cli.py` — Click command group with init, link, sync, status, profile commands
- `config.py` — TOML config read/write at `~/.dotman.toml`
- `linker.py` — Symlink creation and health checking
- Config supports multiple profiles, each with its own set of tracked links

## Testing

```bash
PYTHONPATH=src pytest -v
```

Tests use `tmp_path` and `monkeypatch` to isolate HOME and config path. All tests are in `tests/test_dotman.py`.

## Key Conventions

- All commands require `dotman init` first (enforced by `_require_config()`)
- Symlinks point from home dir to dotfiles repo (repo is source of truth)
- Existing files are backed up with `.bak` suffix before symlinking
- Profile switch removes old profile's symlinks and applies new ones
