#!/usr/bin/env bash
#
# Full mcp-server-datahub vs lite parity 테스트 실행 래퍼.
# 개발기에서 매 작업 전/후 돌려서 동치 여부를 검증하도록 설계.
#
# 필수 환경변수:
#   DATAHUB_GMS_TOKEN  : full 서버가 GMS 에 인증할 때 사용 (이미 받아둔 PAT)
# 옵션:
#   DATAHUB_GMS_URL    (기본: http://localhost:8080)
#   DATAHUB_LITE_DB    (기본: ~/.datahub/lite/datahub.duckdb)
#   UVX_BIN            (기본: ~/.local/bin/uvx)
#   LITE_BIN           (기본: repo-root/.venv/bin/mcp-server-datahub-lite)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PKG_DIR/.." && pwd)"

if [ -z "${DATAHUB_GMS_TOKEN:-}" ]; then
  echo "[ERR] DATAHUB_GMS_TOKEN env 가 필요합니다 (DataHub UI 에서 PAT 발급)." >&2
  exit 2
fi

DATAHUB_GMS_URL="${DATAHUB_GMS_URL:-http://localhost:8080}"
DATAHUB_LITE_DB="${DATAHUB_LITE_DB:-$HOME/.datahub/lite/datahub.duckdb}"

if ! curl -sS -o /dev/null -w "%{http_code}" "$DATAHUB_GMS_URL/config" | grep -q "200"; then
  echo "[ERR] $DATAHUB_GMS_URL 에 접속 불가. DataHub GMS 가 떠있나요?" >&2
  exit 3
fi

if [ ! -f "$DATAHUB_LITE_DB" ]; then
  echo "[ERR] $DATAHUB_LITE_DB 가 없습니다. 먼저 populate 스크립트로 적재하세요." >&2
  exit 4
fi

PY="${PY:-$REPO_ROOT/.venv/bin/python}"
if [ ! -x "$PY" ]; then
  PY="$(command -v python3 || command -v python)"
fi

"$PY" -m pip install --quiet pytest >/dev/null 2>&1 || true

export DATAHUB_GMS_URL DATAHUB_LITE_DB

cd "$PKG_DIR"
exec "$PY" -m pytest tests/ -v "$@"
