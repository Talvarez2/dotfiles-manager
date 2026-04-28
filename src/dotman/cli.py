import shutil
import subprocess
import click
from pathlib import Path
from dotman.config import load_config, save_config, default_config, DEFAULT_CONFIG_PATH
from dotman.linker import create_symlink


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
    click.echo("sync: not yet implemented")


@cli.command()
def status():
    """Show tracked dotfiles and their status."""
    click.echo("status: not yet implemented")


if __name__ == "__main__":
    cli()
