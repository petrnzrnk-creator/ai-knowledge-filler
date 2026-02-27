import pytest
from pathlib import Path
from akf.config import reset_config
import akf as _akf_pkg


@pytest.fixture(autouse=True)
def use_default_config(monkeypatch):
    """Force package defaults for all tests — ignore repo akf.yaml in CWD.
    monkeypatch.setenv is inherited by subprocesses (subprocess CLI tests).
    """
    defaults = Path(_akf_pkg.__file__).parent / "defaults" / "akf.yaml"
    monkeypatch.setenv("AKF_CONFIG_PATH", str(defaults))
    reset_config()
    yield
    reset_config()
