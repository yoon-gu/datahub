"""Read-only DuckDB access layer for datahub-lite.

`datahub lite serve` HTTP 를 쓰지 않고 DuckDB 파일을 직접 연다.
- 오프라인 친화적 (추가 프로세스 없음)
- 단일 MCP 서버 프로세스에서 DB 파일 한 번만 열어 재사용
- read_only=True 로 열어 쓰기 실수 방지
"""

from __future__ import annotations

import json
import os
import threading
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional

import duckdb

DEFAULT_DB_PATH = os.path.expanduser(
    os.environ.get("DATAHUB_LITE_DB", "~/.datahub/lite/datahub.duckdb")
)


class LiteClient:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = duckdb.connect(db_path, read_only=True)

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _query(self, sql: str, params: Optional[List[Any]] = None) -> List[tuple]:
        with self._lock:
            cur = self._conn.execute(sql, params or [])
            return cur.fetchall()

    def get_aspect(self, urn: str, aspect_name: str) -> Optional[Dict[str, Any]]:
        rows = self._query(
            "SELECT metadata FROM metadata_aspect_v2 "
            "WHERE urn = ? AND aspect_name = ? AND version = 0",
            [urn, aspect_name],
        )
        if not rows:
            return None
        return json.loads(rows[0][0])

    def get_all_aspects(self, urn: str) -> Dict[str, Dict[str, Any]]:
        rows = self._query(
            "SELECT aspect_name, metadata FROM metadata_aspect_v2 "
            "WHERE urn = ? AND version = 0",
            [urn],
        )
        return {name: json.loads(meta) for name, meta in rows}

    def iter_urns_by_type(self, entity_type: str) -> Iterable[str]:
        prefix = f"urn:li:{entity_type}:"
        rows = self._query(
            "SELECT DISTINCT urn FROM metadata_aspect_v2 WHERE urn LIKE ? || '%'",
            [prefix],
        )
        for (urn,) in rows:
            yield urn

    def all_urns(self) -> Iterable[str]:
        rows = self._query("SELECT DISTINCT urn FROM metadata_aspect_v2")
        for (urn,) in rows:
            yield urn

    def all_aspects_by_name(self, aspect_name: str) -> Iterable[tuple[str, Dict[str, Any]]]:
        rows = self._query(
            "SELECT urn, metadata FROM metadata_aspect_v2 "
            "WHERE aspect_name = ? AND version = 0",
            [aspect_name],
        )
        for urn, meta in rows:
            yield urn, json.loads(meta)


@lru_cache(maxsize=1)
def get_client() -> LiteClient:
    return LiteClient()


def reset_client() -> None:
    get_client.cache_clear()
