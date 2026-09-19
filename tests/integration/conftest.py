"""Evita que os testes de integração escrevam em logs/ na raiz do repositório."""
import pytest

from src.services import logger


@pytest.fixture(autouse=True)
def _isolated_log_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")
