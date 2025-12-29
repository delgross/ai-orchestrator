"""
Minimal async-friendly DB client placeholder.
Currently wraps sqlite3 for local, single-user use; swap to a faster driver (e.g., asyncpg)
by updating this module only.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, List, Tuple

DB_PATH = Path.home() / "ai" / "agent.db"


class DBClient:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self._conn.close()

    def execute(self, sql: str, params: Any = ()) -> None:
        cur = self._conn.cursor()
        cur.execute(sql, params)
        self._conn.commit()

    def query(self, sql: str, params: Any = ()) -> List[Tuple]:
        cur = self._conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()


def get_db() -> DBClient:
    return DBClient()

