#!/bin/bash
# Build script: assemble all docs into site-docs/ for MkDocs
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE_DOCS="$REPO_ROOT/site-docs"

echo "==> Cleaning site-docs/"
rm -rf "$SITE_DOCS"
mkdir -p "$SITE_DOCS"

echo "==> Copying docs/"
cp -r "$REPO_ROOT/docs/"* "$SITE_DOCS/"

echo "==> Copying metadata-ingestion/ → site-docs/ingestion/"
mkdir -p "$SITE_DOCS/ingestion"
# Top-level md files
for f in README.md recipe_overview.md source_overview.md sink_overview.md \
         cli-ingestion.md adding-source.md as-a-library.md developing.md \
         KAFKA_CONNECT_LINEAGE.md datahub-skills.md; do
  [ -f "$REPO_ROOT/metadata-ingestion/$f" ] && cp "$REPO_ROOT/metadata-ingestion/$f" "$SITE_DOCS/ingestion/$f"
done
# Subdirectories
for subdir in docs schedule_docs sink_docs integration_docs examples; do
  if [ -d "$REPO_ROOT/metadata-ingestion/$subdir" ]; then
    mkdir -p "$SITE_DOCS/ingestion/$subdir"
    cp -r "$REPO_ROOT/metadata-ingestion/$subdir/"* "$SITE_DOCS/ingestion/$subdir/" 2>/dev/null || true
  fi
done

echo "==> Copying metadata-integration/ → site-docs/integration/"
mkdir -p "$SITE_DOCS/integration"
cp -r "$REPO_ROOT/metadata-integration/"* "$SITE_DOCS/integration/" 2>/dev/null || true

echo "==> Copying docs-website/src/learn/ → site-docs/learn/"
mkdir -p "$SITE_DOCS/learn"
cp -r "$REPO_ROOT/docs-website/src/learn/"*.md "$SITE_DOCS/learn/" 2>/dev/null || true

echo "==> Creating index.md"
cat > "$SITE_DOCS/index.md" << 'INDEXEOF'
---
title: DataHub 한국어 문서
---

# DataHub 한국어 문서

**DataHub**는 LinkedIn이 오픈소스로 공개한 **메타데이터 관리 플랫폼**입니다.

> 회사 안의 데이터에 대한 데이터(메타데이터)를 한 곳에 모아서 검색·추적·관리하는 플랫폼

---

## 빠른 탐색

| 섹션 | 설명 |
|------|------|
| [핵심 개념 (ERA)](what-is-datahub/datahub-concepts.md) | Entity, Aspect, Relationship — DataHub의 근간 |
| [아키텍처](architecture/architecture.md) | 시스템 구성 요소와 동작 방식 |
| [Lineage](features/feature-guides/lineage.md) | 데이터 계보 추적 및 영향도 분석 |
| [Data Quality](managed-datahub/observe/assertions.md) | Assertion 기반 데이터 품질 관리 |
| [Ingestion](ingestion/README.md) | 메타데이터 자동 수집 (Recipe, Source, Sink) |
| [SDK / API](api/datahub-apis.md) | Python·Java SDK, GraphQL, REST API |
| [MLModel](api/tutorials/mlmodel-mlmodelgroup.md) | ML 모델 메타데이터 관리 |
| [Ownership / Tags / Glossary](ownership/ownership-types.md) | 소유권, 태그, 비즈니스 용어 관리 |
| [고급 주제](advanced/mcp-mcl.md) | MCP/MCL, Patch, Aspect 버전 관리 |

---

## 참고

- [DataHub 공식 문서](https://docs.datahub.com)
- [DataHub GitHub](https://github.com/datahub-project/datahub)
- [DataHub 데모](https://demo.datahub.com)
INDEXEOF

echo "==> Done! site-docs/ is ready for mkdocs build"
