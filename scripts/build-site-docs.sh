#!/bin/bash
# Build script: assemble all docs into docs-website/genDocs/ for Docusaurus
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GEN_DOCS="$REPO_ROOT/docs-website/genDocs"

echo "==> Cleaning genDocs/"
rm -rf "$GEN_DOCS"
mkdir -p "$GEN_DOCS"

echo "==> Copying docs/"
cp -r "$REPO_ROOT/docs/"* "$GEN_DOCS/"

echo "==> Copying metadata-ingestion/ → genDocs/ingestion/"
mkdir -p "$GEN_DOCS/ingestion"
for f in README.md recipe_overview.md source_overview.md sink_overview.md \
         cli-ingestion.md adding-source.md as-a-library.md developing.md \
         KAFKA_CONNECT_LINEAGE.md datahub-skills.md; do
  [ -f "$REPO_ROOT/metadata-ingestion/$f" ] && cp "$REPO_ROOT/metadata-ingestion/$f" "$GEN_DOCS/ingestion/$f"
done
for subdir in docs schedule_docs sink_docs integration_docs examples; do
  if [ -d "$REPO_ROOT/metadata-ingestion/$subdir" ]; then
    mkdir -p "$GEN_DOCS/ingestion/$subdir"
    cp -r "$REPO_ROOT/metadata-ingestion/$subdir/"* "$GEN_DOCS/ingestion/$subdir/" 2>/dev/null || true
  fi
done

echo "==> Copying metadata-integration/ → genDocs/integration/"
mkdir -p "$GEN_DOCS/integration"
cp -r "$REPO_ROOT/metadata-integration/"* "$GEN_DOCS/integration/" 2>/dev/null || true

echo "==> Copying docs-website/src/learn/ → genDocs/learn/"
mkdir -p "$GEN_DOCS/learn"
for f in "$REPO_ROOT/docs-website/src/learn/"*.md; do
  [ -f "$f" ] && cp "$f" "$GEN_DOCS/learn/"
done

echo "==> Stripping problematic MDX/JSX from markdown files"
find "$GEN_DOCS" -name '*.md' -exec sed -i.bak \
  -e '/^import .* from/d' \
  -e '/^import {/d' \
  -e '/^export /d' \
  -e '/<Tabs>/d' \
  -e '/<\/Tabs>/d' \
  -e '/<TabItem /d' \
  -e '/<\/TabItem>/d' \
  -e '/<details>/d' \
  -e '/<\/details>/d' \
  -e '/<summary>/d' \
  -e '/<\/summary>/d' \
  -e '/{{ inline/d' \
  -e '/{{ command-output/d' \
  -e 's/<FeatureAvailability[^>]*\/>//' \
  -e 's/<FeatureAvailability[^>]*>//' \
  -e 's/<\/FeatureAvailability>//' \
  {} \;
find "$GEN_DOCS" -name '*.md.bak' -delete

echo "==> Fixing bare URLs followed by Korean text"
find "$GEN_DOCS" -name '*.md' -exec perl -i -pe \
  's{(https?://[^\s\)>\]`]+?)([가-힣])}{`$1` $2}g' {} \;

echo "==> Renaming .mdx files to .md"
find "$GEN_DOCS" -name '*.mdx' -exec sh -c 'mv "$1" "${1%.mdx}.md"' _ {} \;

echo "==> Creating index page"
cat > "$GEN_DOCS/README.md" << 'INDEXEOF'
---
title: DataHub 한국어 문서
slug: /
---

# DataHub 한국어 문서

**DataHub**는 LinkedIn이 오픈소스로 공개한 **메타데이터 관리 플랫폼**입니다.

> 회사 안의 데이터에 대한 데이터(메타데이터)를 한 곳에 모아서 검색·추적·관리하는 플랫폼

---

## 빠른 탐색

| 섹션 | 설명 |
|------|------|
| [핵심 개념 (ERA)](what-is-datahub/datahub-concepts) | Entity, Aspect, Relationship — DataHub의 근간 |
| [아키텍처](architecture/architecture) | 시스템 구성 요소와 동작 방식 |
| [Lineage](features/feature-guides/lineage) | 데이터 계보 추적 및 영향도 분석 |
| [Data Quality](managed-datahub/observe/assertions) | Assertion 기반 데이터 품질 관리 |
| [Ingestion](ingestion/README) | 메타데이터 자동 수집 (Recipe, Source, Sink) |
| [SDK / API](api/datahub-apis) | Python·Java SDK, GraphQL, REST API |
| [MLModel](api/tutorials/mlmodel-mlmodelgroup) | ML 모델 메타데이터 관리 |
| [Ownership / Tags / Glossary](ownership/ownership-types) | 소유권, 태그, 비즈니스 용어 관리 |
| [고급 주제](advanced/mcp-mcl) | MCP/MCL, Patch, Aspect 버전 관리 |

---

## 참고

- [DataHub 공식 문서](https://docs.datahub.com)
- [DataHub GitHub](https://github.com/datahub-project/datahub)
- [DataHub 데모](https://demo.datahub.com)
INDEXEOF

echo "==> Removing problematic release notes"
rm -f "$GEN_DOCS/managed-datahub/release-notes/v_0_2_11.md"
rm -f "$GEN_DOCS/managed-datahub/release-notes/v_0_2_15.md"

echo "==> Done! genDocs/ is ready for Docusaurus build"
