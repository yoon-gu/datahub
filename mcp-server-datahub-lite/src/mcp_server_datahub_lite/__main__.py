"""Entry point for `python -m mcp_server_datahub_lite` and `mcp-server-datahub-lite` script."""

from __future__ import annotations

import argparse
import os
import sys

from .lite import LiteClient
from .server import mcp, register_all_tools


def main() -> int:
    parser = argparse.ArgumentParser(prog="mcp-server-datahub-lite")
    parser.add_argument(
        "--lite-db",
        default=None,
        help="Path to datahub-lite DuckDB file. Overrides DATAHUB_LITE_DB env. "
        "Default: ~/.datahub/lite/datahub.duckdb",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
    )
    args = parser.parse_args()

    if args.lite_db:
        os.environ["DATAHUB_LITE_DB"] = os.path.expanduser(args.lite_db)

    # DB 를 여기서 한 번 열어 경로 문제 / 파일 누락 를 조기 검출
    db_path = os.path.expanduser(os.environ.get("DATAHUB_LITE_DB", "~/.datahub/lite/datahub.duckdb"))
    if not os.path.exists(db_path):
        print(f"[ERR] datahub-lite DB not found at {db_path}", file=sys.stderr)
        print(
            "      먼저 `datahub lite init --type duckdb` 실행 후 populate 스크립트로 메타데이터를 적재해주세요.",
            file=sys.stderr,
        )
        return 2

    LiteClient(db_path)  # probe

    register_all_tools()
    mcp.run(transport=args.transport)
    return 0


if __name__ == "__main__":
    sys.exit(main())
