# dotfiles-manager

CLI tool to sync dev environment configs across machines.

## Install

```bash
pip install -e .
```

## Quick Start

```bash
# Initialize dotfiles repo
dotman init --dir ~/dotfiles

# Track config files
dotman link ~/.bashrc
dotman link ~/.vimrc
dotman link ~/.gitconfig

# Check status
dotman status

# Sync to git
dotman sync -m "add shell config"
```

## Commands

| Command | Description |
|---------|-------------|
| `dotman init --dir <path>` | Initialize dotfiles repo and config |
| `dotman link <file> [--name <n>]` | Track and symlink a config file |
| `dotman sync [-m <msg>]` | Git add, commit, and push dotfiles |
| `dotman status` | Show tracked files and link health |
| `dotman profile list` | List available profiles |
| `dotman profile switch <name>` | Switch to a profile |

## Profiles

Manage separate configs for different environments:

```bash
# Default profile is created on init
dotman link ~/.bashrc

# Switch to work profile
dotman profile switch work
dotman link ~/.bashrc  # different .bashrc for work

# Switch back
dotman profile switch default
```

## Config

Stored at `~/.dotman.toml`:

```toml
dotfiles_dir = "/home/user/dotfiles"
profile = "default"

[profiles.default.links]
".bashrc" = "/home/user/.bashrc"
".vimrc" = "/home/user/.vimrc"

[profiles.work.links]
".bashrc" = "/home/user/.bashrc"
```

## Status Icons

- `[✓]` — symlink OK
- `[✗]` — broken symlink
- `[?]` — missing (not linked yet)
- `[!]` — conflict (regular file exists where symlink expected)

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

<!-- GIF/screenshot placeholder -->
