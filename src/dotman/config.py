from pathlib import Path
import toml

DEFAULT_CONFIG_PATH = Path.home() / ".dotman.toml"


def load_config(path=None):
    """Load config from TOML file."""
    p = Path(path) if path else DEFAULT_CONFIG_PATH
    if not p.exists():
        return {}
    return toml.load(p)


def save_config(config, path=None):
    """Write config dict to TOML file."""
    p = Path(path) if path else DEFAULT_CONFIG_PATH
    p.write_text(toml.dumps(config))


def default_config(dotfiles_dir):
    """Return a default config dict."""
    return {
        "dotfiles_dir": str(dotfiles_dir),
        "profile": "default",
        "profiles": {"default": {"links": {}}},
    }
