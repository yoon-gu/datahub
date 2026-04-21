#!/usr/bin/env bash
#
# 외부망 빌드 머신에서 실행. 온프렘(오프라인) 반입을 위한 wheelhouse 생성.
#
# 산출물: ./wheelhouse/ 아래에 mcp-server-datahub-lite + 모든 의존성의 .whl 모음
# 타겟:   Ubuntu x86_64 / Python 3.10 (환경변수로 조정 가능)
#
# 온프렘 설치:
#   pip install --no-index --find-links=./wheelhouse mcp-server-datahub-lite
#
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${OUT_DIR:-$PROJECT_DIR/wheelhouse}"
PY_VER="${PY_VER:-3.10}"
PLATFORM="${PLATFORM:-manylinux2014_x86_64}"

mkdir -p "$OUT_DIR"
cd "$PROJECT_DIR"

echo "[*] Build wheel for this package"
python -m pip wheel --no-deps --wheel-dir "$OUT_DIR" .

echo "[*] Download all dependencies as wheels (platform=$PLATFORM, python=$PY_VER)"
python -m pip download \
    --dest "$OUT_DIR" \
    --python-version "$PY_VER" \
    --platform "$PLATFORM" \
    --only-binary=:all: \
    --implementation cp \
    --abi "cp${PY_VER//./}" \
    -e .

SHA="$OUT_DIR/SHA256SUMS"
echo "[*] Compute checksums -> $SHA"
( cd "$OUT_DIR" && find . -type f \( -name '*.whl' -o -name '*.tar.gz' \) | sort | xargs shasum -a 256 ) > "$SHA"

echo "[*] Generate licenses report"
python -m pip install --quiet pip-licenses 2>/dev/null || true
pip-licenses --format=markdown --with-urls > "$OUT_DIR/LICENSES.md" 2>/dev/null || echo "  (pip-licenses 설치 안 됨 — 건너뜀)"

cat > "$OUT_DIR/INSTALL.md" <<EOF
# On-prem 설치

사전조건: Python $PY_VER, pip. 네트워크 불필요.

\`\`\`bash
pip install --no-index --find-links=./wheelhouse mcp-server-datahub-lite
\`\`\`

실행:

\`\`\`bash
# 1) 메타데이터 (datahub.duckdb) 를 함께 반입해 적절한 위치에 둠
export DATAHUB_LITE_DB=/data/datahub.duckdb

# 2) Claude Desktop 설정에 등록하거나 직접 기동
mcp-server-datahub-lite --transport stdio
\`\`\`
EOF

count=$(find "$OUT_DIR" -name '*.whl' | wc -l | tr -d ' ')
size=$(du -sh "$OUT_DIR" | cut -f1)
echo "[*] Done. wheels=$count total=$size out=$OUT_DIR"
