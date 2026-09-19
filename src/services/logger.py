"""Log estruturado JSON Lines por sessão (Princípio IV / FR-011, contracts/log-schema.md)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Union

from src.models.log_entry import to_log_dict
from src.models.session import Round, Session

DEFAULT_LOG_DIR = Path("logs")


def append_round(
    session: Session, round_: Round, log_dir: Optional[Union[str, Path]] = None
) -> Path:
    """Escreve uma linha JSON para `round_` em `logs/<session_id>.jsonl` (modo append)."""
    log_dir = Path(log_dir) if log_dir is not None else DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{session.session_id}.jsonl"

    entry = to_log_dict(session, round_)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())

    return path
