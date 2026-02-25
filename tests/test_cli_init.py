"""tests/test_cli_init.py — Tests for akf init command"""
from __future__ import annotations
from pathlib import Path
import pytest
from cli import cmd_init

class Args:
    def __init__(self, path=None, force=False):
        self.path = path
        self.force = force

class TestCmdInit:
    def test_creates_akf_yaml_in_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cmd_init(Args())
        assert (tmp_path / "akf.yaml").exists()

    def test_creates_in_specified_path(self, tmp_path):
        cmd_init(Args(path=str(tmp_path)))
        assert (tmp_path / "akf.yaml").exists()

    def test_creates_dir_if_missing(self, tmp_path):
        target = tmp_path / "new" / "vault"
        cmd_init(Args(path=str(target)))
        assert (target / "akf.yaml").exists()

    def test_created_file_is_valid_yaml(self, tmp_path):
        import yaml
        cmd_init(Args(path=str(tmp_path)))
        content = yaml.safe_load((tmp_path / "akf.yaml").read_text())
        assert "taxonomy" in content
        assert "enums" in content

    def test_aborts_if_exists_without_force(self, tmp_path):
        (tmp_path / "akf.yaml").write_text("original\n")
        with pytest.raises(SystemExit) as exc:
            cmd_init(Args(path=str(tmp_path)))
        assert exc.value.code == 1
        assert (tmp_path / "akf.yaml").read_text() == "original\n"

    def test_force_overwrites(self, tmp_path):
        (tmp_path / "akf.yaml").write_text("original\n")
        cmd_init(Args(path=str(tmp_path), force=True))
        assert "taxonomy" in (tmp_path / "akf.yaml").read_text()
