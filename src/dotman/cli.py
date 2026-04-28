import shutil
import subprocess
import click
from pathlib import Path
from dotman.config import load_config, save_config, default_config, DEFAULT_CONFIG_PATH
from dotman.linker import create_symlink, check_link


@click.group()
def cli():
    """Dotfiles manager - sync dev configs across machines."""


def _require_config():
    config = load_config()
    if not config:
        click.echo("Run 'dotman init' first.", err=True)
        raise SystemExit(1)
    return config


def _get_links(config):
    profile = config.get("profile", "default")
    return config.get("profiles", {}).get(profile, {}).get("links", {})


@cli.command()
@click.option("--dir", "dotfiles_dir", default="~/dotfiles", help="Dotfiles repo directory")
def init(dotfiles_dir):
    """Initialize dotfiles repository and config."""
    dotfiles_dir = Path(dotfiles_dir).expanduser().resolve()
    dotfiles_dir.mkdir(parents=True, exist_ok=True)
    if not (dotfiles_dir / ".git").exists():
        subprocess.run(["git", "init", str(dotfiles_dir)], check=True)
    config = default_config(dotfiles_dir)
    save_config(config)
    click.echo(f"Initialized dotfiles repo at {dotfiles_dir}")
    click.echo(f"Config written to {DEFAULT_CONFIG_PATH}")


@cli.command()
@click.argument("path")
@click.option("--name", default=None, help="Name for the link in config")
def link(path, name):
    """Track and symlink a config file into the dotfiles repo."""
    config = _require_config()
    source = Path(path).expanduser().resolve()
    if not source.exists():
        click.echo(f"Source file not found: {source}", err=True)
        raise SystemExit(1)
    dotfiles_dir = Path(config["dotfiles_dir"])
    name = name or source.name
    dest = dotfiles_dir / name
    if not dest.exists():
        shutil.copy2(str(source), str(dest))
    source.unlink()
    create_symlink(dest, source)
    profile = config.get("profile", "default")
    config["profiles"][profile]["links"][name] = str(source)
    save_config(config)
    click.echo(f"Linked {name}: {dest} -> {source}")


@cli.command()
@click.option("-m", "--message", default="dotfiles sync", help="Commit message")
def sync(message):
    """Commit and push dotfiles changes."""
    config = _require_config()
    dotfiles_dir = config["dotfiles_dir"]
    subprocess.run(["git", "add", "-A"], cwd=dotfiles_dir, check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=dotfiles_dir)
    if result.returncode == 0:
        click.echo("Nothing to sync.")
        return
    subprocess.run(["git", "commit", "-m", message], cwd=dotfiles_dir, check=True)
    result = subprocess.run(["git", "remote"], cwd=dotfiles_dir, capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.run(["git", "push"], cwd=dotfiles_dir, check=True)
        click.echo("Synced and pushed.")
    else:
        click.echo("Synced (no remote configured).")


@cli.command()
def status():
    """Show tracked dotfiles and their status."""
    config = _require_config()
    dotfiles_dir = Path(config["dotfiles_dir"])
    links = _get_links(config)
    click.echo(f"Profile: {config.get('profile', 'default')}")
    if not links:
        click.echo("No tracked dotfiles.")
        return
    for name, target in links.items():
        state = check_link(dotfiles_dir / name, Path(target))
        icon = {"ok": "✓", "broken": "✗", "missing": "?", "conflict": "!"}.get(state, "?")
        click.echo(f"  [{icon}] {name} -> {target} ({state})")


if __name__ == "__main__":
    cli()
