from pathlib import Path
import os


def create_symlink(source, target):
    """Create symlink: target -> source. Source is in dotfiles repo, target is in home."""
    source, target = Path(source), Path(target)
    if target.is_symlink():
        target.unlink()
    elif target.exists():
        target.rename(str(target) + ".bak")
    target.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(source, target)


def check_link(source, target):
    """Check symlink status. Returns: 'ok', 'broken', 'missing', or 'conflict'."""
    source, target = Path(source), Path(target)
    if not target.is_symlink() and not target.exists():
        return "missing"
    if target.is_symlink():
        return "ok" if target.resolve() == source.resolve() else "broken"
    return "conflict"
