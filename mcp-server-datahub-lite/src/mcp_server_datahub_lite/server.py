"""FastMCP server setup. Tool registration lives in submodules under `tools/`."""

from __future__ import annotations

from fastmcp import FastMCP

mcp: FastMCP = FastMCP(name="datahub-lite")


def register_all_tools() -> None:
    from .tools import entities, lineage, queries, schema_fields, search  # noqa: F401

    # 모듈을 import 하는 순간 @mcp.tool 데코레이터가 실행되어 등록됨
    _ = (entities, lineage, queries, schema_fields, search)
