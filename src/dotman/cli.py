import click


@click.group()
def cli():
    """Dotfiles manager - sync dev configs across machines."""


@cli.command()
@click.option("--dir", "dotfiles_dir", default="~/dotfiles", help="Dotfiles repo directory")
def init(dotfiles_dir):
    """Initialize dotfiles repository and config."""
    click.echo("init: not yet implemented")


@cli.command()
@click.argument("path")
@click.option("--name", default=None, help="Name for the link in config")
def link(path, name):
    """Track and symlink a config file into the dotfiles repo."""
    click.echo("link: not yet implemented")


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
