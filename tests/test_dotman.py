import os
import pytest
from pathlib import Path
from click.testing import CliRunner
from dotman.cli import cli
from dotman.config import load_config
from dotman.linker import create_symlink, check_link


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    import dotman.config as cfg
    monkeypatch.setattr(cfg, "DEFAULT_CONFIG_PATH", tmp_path / ".dotman.toml")
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


class TestInit:
    def test_creates_config_and_repo(self, runner, home):
        dotdir = home / "dotfiles"
        result = runner.invoke(cli, ["init", "--dir", str(dotdir)])
        assert result.exit_code == 0
        assert (dotdir / ".git").is_dir()
        assert (home / ".dotman.toml").exists()

    def test_idempotent(self, runner, home):
        dotdir = home / "dotfiles"
        runner.invoke(cli, ["init", "--dir", str(dotdir)])
        result = runner.invoke(cli, ["init", "--dir", str(dotdir)])
        assert result.exit_code == 0


class TestLink:
    def test_creates_symlink(self, runner, home):
        dotdir = home / "dotfiles"
        runner.invoke(cli, ["init", "--dir", str(dotdir)])
        src = home / ".bashrc"
        src.write_text("# bashrc")
        result = runner.invoke(cli, ["link", str(src)])
        assert result.exit_code == 0
        assert src.is_symlink()
        assert (dotdir / ".bashrc").exists()

    def test_without_init_fails(self, runner, home):
        result = runner.invoke(cli, ["link", "/tmp/nonexistent"])
        assert result.exit_code != 0

    def test_nonexistent_file_fails(self, runner, home):
        runner.invoke(cli, ["init", "--dir", str(home / "dotfiles")])
        result = runner.invoke(cli, ["link", str(home / "nope")])
        assert result.exit_code != 0


class TestStatus:
    def test_empty(self, runner, home):
        runner.invoke(cli, ["init", "--dir", str(home / "dotfiles")])
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "No tracked dotfiles" in result.output

    def test_shows_linked_file(self, runner, home):
        runner.invoke(cli, ["init", "--dir", str(home / "dotfiles")])
        src = home / ".vimrc"
        src.write_text("set nocp")
        runner.invoke(cli, ["link", str(src)])
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert ".vimrc" in result.output
        assert "ok" in result.output


class TestSync:
    def test_nothing_to_sync(self, runner, home):
        runner.invoke(cli, ["init", "--dir", str(home / "dotfiles")])
        result = runner.invoke(cli, ["sync"])
        assert result.exit_code == 0
        assert "Nothing to sync" in result.output

    def test_commits_changes(self, runner, home):
        import subprocess
        dotdir = home / "dotfiles"
        runner.invoke(cli, ["init", "--dir", str(dotdir)])
        (dotdir / "test.txt").write_text("hello")
        result = runner.invoke(cli, ["sync", "-m", "test commit"])
        assert result.exit_code == 0
        log = subprocess.run(
            ["git", "log", "--oneline"], cwd=str(dotdir),
            capture_output=True, text=True,
        )
        assert "test commit" in log.stdout


class TestProfile:
    def test_list(self, runner, home):
        runner.invoke(cli, ["init", "--dir", str(home / "dotfiles")])
        result = runner.invoke(cli, ["profile", "list"])
        assert result.exit_code == 0
        assert "default" in result.output

    def test_switch_creates_new(self, runner, home):
        runner.invoke(cli, ["init", "--dir", str(home / "dotfiles")])
        result = runner.invoke(cli, ["profile", "switch", "work"])
        assert result.exit_code == 0
        assert "Switched to profile: work" in result.output

    def test_switch_applies_links(self, runner, home):
        runner.invoke(cli, ["init", "--dir", str(home / "dotfiles")])
        src = home / ".bashrc"
        src.write_text("# default bashrc")
        runner.invoke(cli, ["link", str(src)])
        assert src.is_symlink()
        runner.invoke(cli, ["profile", "switch", "work"])
        assert not src.is_symlink()
        runner.invoke(cli, ["profile", "switch", "default"])
        assert src.is_symlink()


class TestLinker:
    def test_create_symlink(self, tmp_path):
        source = tmp_path / "source.txt"
        source.write_text("content")
        target = tmp_path / "target.txt"
        create_symlink(source, target)
        assert target.is_symlink()
        assert target.read_text() == "content"

    def test_backs_up_existing(self, tmp_path):
        source = tmp_path / "source.txt"
        source.write_text("new")
        target = tmp_path / "target.txt"
        target.write_text("old")
        create_symlink(source, target)
        assert target.is_symlink()
        assert (tmp_path / "target.txt.bak").read_text() == "old"

    def test_check_link_ok(self, tmp_path):
        source = tmp_path / "s.txt"
        source.write_text("x")
        target = tmp_path / "t.txt"
        os.symlink(source, target)
        assert check_link(source, target) == "ok"

    def test_check_link_missing(self, tmp_path):
        assert check_link(tmp_path / "s", tmp_path / "t") == "missing"

    def test_check_link_conflict(self, tmp_path):
        source = tmp_path / "s.txt"
        source.write_text("x")
        target = tmp_path / "t.txt"
        target.write_text("y")
        assert check_link(source, target) == "conflict"
