#!/usr/bin/env bash
#
# datahub-lite MCP 서버 기동 래퍼.
#
# 기본 동작:
#   - LITE_DB 가 있는지 확인하고 없으면 안내 후 종료
#   - 패키지가 설치되어 있는지 확인, 없으면 editable install
#   - stdio transport 로 서버 기동
#
# 환경변수 (옵션):
#   LITE_DB         : datahub-lite duckdb 파일 경로 (기본: ~/.datahub/lite/datahub.duckdb)
#   TRANSPORT       : stdio | sse | http (기본: stdio)
#   PY              : 사용할 python (기본: 아래 감지 로직)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

LITE_DB="${LITE_DB:-$HOME/.datahub/lite/datahub.duckdb}"
TRANSPORT="${TRANSPORT:-stdio}"

if [ -n "${PY:-}" ]; then
  :
elif [ -x "$PKG_DIR/.venv/bin/python" ]; then
  PY="$PKG_DIR/.venv/bin/python"
elif [ -x "$PKG_DIR/../.venv/bin/python" ]; then
  PY="$PKG_DIR/../.venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi

if ! "$PY" -c "import mcp_server_datahub_lite" 2>/dev/null; then
  echo "[*] mcp-server-datahub-lite 가 설치되어 있지 않아 editable install 합니다..." >&2
  "$PY" -m pip install -e "$PKG_DIR" >&2
fi

if [ ! -f "$LITE_DB" ]; then
  echo "[ERR] datahub-lite DB 가 없습니다: $LITE_DB" >&2
  echo "       1) datahub lite init --type duckdb" >&2
  echo "       2) DATAHUB_GMS_TOKEN=<...> $PY $SCRIPT_DIR/populate_lite_from_gms.py" >&2
  echo "       (온프렘이면 반입한 스냅샷을 해당 경로로 복사)" >&2
  exit 1
fi

echo "[*] lite-db=$LITE_DB transport=$TRANSPORT" >&2
exec "$PY" -m mcp_server_datahub_lite --lite-db "$LITE_DB" --transport "$TRANSPORT"
