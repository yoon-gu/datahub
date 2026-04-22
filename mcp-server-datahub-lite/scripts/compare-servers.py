"""Side-by-side diff report: full mcp-server-datahub vs lite.

각 테스트 케이스마다 양쪽 서버에서 key 응답 필드를 뽑아 좌/우 컬럼으로 비교.
터미널(ANSI) 또는 HTML 파일로 렌더링.

사용:
    DATAHUB_GMS_TOKEN=<PAT> \\
        .venv/bin/python mcp-server-datahub-lite/scripts/compare-servers.py

옵션:
    --tools search,get_lineage   특정 tool 만
    --no-color                   터미널 ANSI 끄기
    --col-width 70               터미널 컬럼 폭 (기본 60)
    --html PATH                  HTML 파일 생성
    --open                       HTML 생성 후 자동으로 브라우저에서 열기
    --quiet                      터미널 case 상세 출력 생략 (요약만)
"""

from __future__ import annotations

import argparse
import html
import os
import sys
import webbrowser
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests import test_cases  # noqa: E402
from tests.mcp_client import McpStdioClient, full_client_args, lite_client_args  # noqa: E402


# ----------------------------------------------------------------------
# Case data model + Reporter (terminal + HTML)
# ----------------------------------------------------------------------


@dataclass
class Case:
    tool: str
    label: str
    left: List[str]
    right: List[str]
    match: bool
    note: str


@dataclass
class Report:
    cases: List[Case] = field(default_factory=list)

    def add(self, tool: str, label: str, left: Sequence[str], right: Sequence[str],
            match: bool, note: str = "") -> None:
        self.cases.append(Case(tool=tool, label=label, left=list(left),
                               right=list(right), match=match, note=note))

    def summary(self) -> List[Tuple[str, int, int]]:
        """Return [(tool, pass, fail), ...] in insertion order."""
        order: List[str] = []
        passes: Dict[str, int] = {}
        fails: Dict[str, int] = {}
        for c in self.cases:
            if c.tool not in passes:
                order.append(c.tool)
                passes[c.tool] = fails[c.tool] = 0
            if c.match:
                passes[c.tool] += 1
            else:
                fails[c.tool] += 1
        return [(t, passes[t], fails[t]) for t in order]


class Style:
    def __init__(self, use_color: bool):
        self.use_color = use_color and sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        if not self.use_color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def bold(self, t: str) -> str: return self._c("1", t)
    def dim(self, t: str) -> str: return self._c("2", t)
    def green(self, t: str) -> str: return self._c("32", t)
    def red(self, t: str) -> str: return self._c("31", t)
    def yellow(self, t: str) -> str: return self._c("33", t)
    def cyan(self, t: str) -> str: return self._c("36", t)


def _pad(s: str, width: int) -> str:
    if len(s) >= width:
        return s[: width - 1] + "…"
    return s + " " * (width - len(s))


def render_terminal(report: Report, style: Style, col_width: int = 60) -> None:
    current_tool: Optional[str] = None
    for case in report.cases:
        if case.tool != current_tool:
            current_tool = case.tool
            print(style.bold(f"\n╔══ {case.tool} " + "═" * (60 - len(case.tool))))

        full_width = col_width * 2 + 3
        print()
        print(style.bold(f"[{case.tool}]") + "   " + style.dim(case.label))
        print("─" * full_width)
        print(f"{_pad(style.cyan('FULL'), col_width)}   {style.cyan('LITE')}")
        print("─" * full_width)
        left_set = {l.strip() for l in case.left if l.strip()}
        right_set = {r.strip() for r in case.right if r.strip()}
        rows = max(len(case.left), len(case.right))
        pad_l = case.left + [""] * (rows - len(case.left))
        pad_r = case.right + [""] * (rows - len(case.right))
        for l, r in zip(pad_l, pad_r):
            l_mark = "  " if not l.strip() or l.strip() in right_set else style.red(" *")
            r_mark = "  " if not r.strip() or r.strip() in left_set else style.red(" *")
            print(f"{_pad(l, col_width)}{l_mark} {_pad(r, col_width)}{r_mark}")
        print("─" * full_width)
        verdict = style.green("  ✓ MATCH") if case.match else style.red("  ✗ DIFF")
        if case.note:
            verdict += f"   {style.dim(case.note) if case.match else style.yellow(case.note)}"
        print(verdict)


def render_html(report: Report, path: str) -> None:
    summary = report.summary()
    total_pass = sum(p for _, p, _ in summary)
    total_fail = sum(f for _, _, f in summary)
    overall_ok = total_fail == 0

    css = """
    :root {
        --bg: #fafafa; --fg: #1b1b1b; --muted: #6b6b6b;
        --line: #e0e0e0; --card: #ffffff;
        --match: #0a7a3a; --diff: #c1272d; --warn: #c47d00;
        --match-bg: #e8f7ee; --diff-bg: #fdecec; --mark-bg: #fff2c7;
        --code: Menlo, Consolas, ui-monospace, monospace;
    }
    * { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", sans-serif;
           margin: 0; padding: 24px; background: var(--bg); color: var(--fg); }
    h1 { margin: 0 0 6px; font-size: 22px; }
    .sub { color: var(--muted); margin-bottom: 24px; font-size: 13px; }
    .summary { background: var(--card); padding: 16px 20px; border: 1px solid var(--line);
               border-radius: 8px; margin-bottom: 24px; }
    .summary h2 { margin: 0 0 12px; font-size: 15px; }
    .summary table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .summary td { padding: 6px 10px; border-bottom: 1px solid var(--line); }
    .summary td:last-child { text-align: right; font-variant-numeric: tabular-nums; }
    .summary .tool-name { font-family: var(--code); font-weight: 600; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px;
             font-weight: 600; }
    .badge.match { color: var(--match); background: var(--match-bg); }
    .badge.diff  { color: var(--diff);  background: var(--diff-bg); }
    .tool-group { margin-bottom: 28px; }
    .tool-group h2 { font-size: 18px; margin: 12px 0; padding-bottom: 6px;
                     border-bottom: 2px solid var(--line); }
    .case { background: var(--card); border: 1px solid var(--line); border-radius: 8px;
            margin-bottom: 12px; overflow: hidden; }
    .case.diff { border-color: #f3c1c1; }
    .case-head { display: flex; align-items: center; justify-content: space-between;
                 padding: 10px 16px; background: #f4f4f6; border-bottom: 1px solid var(--line);
                 font-size: 13px; cursor: pointer; }
    .case.diff .case-head { background: #fff4f4; }
    .case-head .label { font-family: var(--code); color: var(--fg); }
    .case-head .note { color: var(--muted); font-size: 12px; margin-left: 12px; }
    .case-body { display: grid; grid-template-columns: 1fr 1fr; }
    .case-body > div { padding: 10px 16px; font-family: var(--code); font-size: 12px;
                       white-space: pre-wrap; line-height: 1.5; }
    .case-body > div:first-child { border-right: 1px solid var(--line); }
    .col-head { font-weight: 700; color: var(--muted); font-size: 11px; text-transform: uppercase;
                letter-spacing: 0.05em; padding-bottom: 4px; display: block; }
    .uniq { background: var(--mark-bg); padding: 0 3px; border-radius: 2px; }
    details summary::-webkit-details-marker { display: none; }
    details summary { list-style: none; }
    details[open] .case-head::after { content: "▼"; color: var(--muted); }
    details:not([open]) .case-head::after { content: "▶"; color: var(--muted); }
    """

    def _line_html(line: str, other_set: Set[str]) -> str:
        stripped = line.strip()
        escaped = html.escape(line).replace(" ", "&nbsp;")
        if stripped and stripped not in other_set:
            # highlight with preserved indent
            indent_len = len(line) - len(line.lstrip(" "))
            indent = "&nbsp;" * indent_len
            body = html.escape(line[indent_len:])
            return f'{indent}<span class="uniq">{body}</span>'
        return escaped or "&nbsp;"

    parts: List[str] = []
    parts.append("<!doctype html><html><head><meta charset='utf-8'>")
    parts.append("<title>DataHub MCP Parity Report</title>")
    parts.append(f"<style>{css}</style></head><body>")
    parts.append("<h1>DataHub MCP Parity Report</h1>")
    parts.append(f"<div class='sub'>full <code>mcp-server-datahub</code> ↔ "
                 f"lite <code>mcp-server-datahub-lite</code> · "
                 f"{len(report.cases)} cases, "
                 f"<span class='badge match'>{total_pass} match</span> · "
                 f"<span class='badge diff'>{total_fail} diff</span></div>")

    # Summary table
    parts.append("<div class='summary'><h2>Tool Summary</h2><table>")
    for tool, p, f_ in summary:
        badge = "<span class='badge match'>OK</span>" if f_ == 0 else f"<span class='badge diff'>{f_} diff</span>"
        parts.append(f"<tr><td class='tool-name'>{html.escape(tool)}</td>"
                     f"<td>{p} match / {f_} diff</td><td>{badge}</td></tr>")
    parts.append("</table></div>")

    # Group cases by tool
    by_tool: Dict[str, List[Case]] = {}
    for c in report.cases:
        by_tool.setdefault(c.tool, []).append(c)

    for tool, cases in by_tool.items():
        parts.append(f"<section class='tool-group'><h2>{html.escape(tool)}</h2>")
        for c in cases:
            cls = "" if c.match else " diff"
            badge = ("<span class='badge match'>✓ MATCH</span>" if c.match
                     else "<span class='badge diff'>✗ DIFF</span>")
            left_set = {l.strip() for l in c.left if l.strip()}
            right_set = {r.strip() for r in c.right if r.strip()}
            left_html = "<br>".join(_line_html(l, right_set) for l in c.left)
            right_html = "<br>".join(_line_html(r, left_set) for r in c.right)
            open_attr = "open" if not c.match else ""
            note_html = f"<span class='note'>{html.escape(c.note)}</span>" if c.note else ""
            parts.append(f"<details class='case{cls}' {open_attr}>")
            parts.append(
                "<summary><div class='case-head'>"
                f"<span>{badge}&nbsp;&nbsp;<span class='label'>{html.escape(c.label)}</span>"
                f"{note_html}"
                "</span></div></summary>"
            )
            parts.append("<div class='case-body'>")
            parts.append(f"<div><span class='col-head'>FULL</span>{left_html}</div>")
            parts.append(f"<div><span class='col-head'>LITE</span>{right_html}</div>")
            parts.append("</div></details>")
        parts.append("</section>")

    parts.append("</body></html>")
    with open(path, "w", encoding="utf-8") as fp:
        fp.write("".join(parts))


# ----------------------------------------------------------------------
# Response shape normalization
# ----------------------------------------------------------------------


def _result_payload(res: Any) -> Any:
    if isinstance(res, dict) and set(res.keys()) == {"result"}:
        return res["result"]
    return res


def _lineage_container(resp: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(resp, dict):
        return None
    for k in ("downstreams", "upstreams"):
        inner = resp.get(k)
        if isinstance(inner, dict):
            return inner
    return resp if isinstance(resp, dict) else None


def _short(urn: str) -> str:
    if "," in urn:
        parts = urn.rstrip(")").split(",")
        if len(parts) >= 2:
            return parts[-2]
    return urn.split(":")[-1] if ":" in urn else urn


def _find_entity(data: Any, urn: str) -> Optional[Dict[str, Any]]:
    if isinstance(data, dict):
        if data.get("urn") == urn:
            return data
        if urn in data and isinstance(data[urn], dict):
            return data[urn]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("urn") == urn:
                return item
    return None


def extract_entity_summary(resp: Any, urn: str) -> Dict[str, Any]:
    data = _result_payload(resp)
    entry = _find_entity(data, urn) or {}
    aspects = entry.get("aspects") if isinstance(entry.get("aspects"), dict) else None

    def _nested_urn(x: Any) -> Optional[str]:
        if isinstance(x, str) and x.startswith("urn:li:"):
            return x
        if isinstance(x, dict):
            u = x.get("urn")
            if isinstance(u, str):
                return u
            for k in ("owner", "tag", "term", "entity", "domain"):
                nested = _nested_urn(x.get(k))
                if nested:
                    return nested
        return None

    def _extract_urn_list(*candidates: Any) -> List[str]:
        for c in candidates:
            if not c:
                continue
            if isinstance(c, list):
                out: List[str] = []
                for x in c:
                    u = _nested_urn(x)
                    if u:
                        out.append(u)
                if out:
                    return sorted(set(out))
        return []

    owners = _extract_urn_list(
        (entry.get("ownership") or {}).get("owners"),
        ((aspects or {}).get("ownership") or {}).get("owners"),
    )
    tags = _extract_urn_list(
        (entry.get("tags") or {}).get("tags"),
        ((aspects or {}).get("globalTags") or {}).get("tags"),
    )
    terms = _extract_urn_list(
        (entry.get("glossaryTerms") or {}).get("terms"),
        ((aspects or {}).get("glossaryTerms") or {}).get("terms"),
    )

    full_domain = entry.get("domain") or {}
    domain_urn = None
    if isinstance(full_domain, dict):
        d = full_domain.get("domain")
        if isinstance(d, dict):
            domain_urn = d.get("urn")
        elif isinstance(d, str):
            domain_urn = d
    if not domain_urn and aspects:
        doms = (aspects.get("domains") or {}).get("domains") or []
        if doms:
            domain_urn = doms[0]

    schema_fields = 0
    sm_full = entry.get("schemaMetadata") or {}
    if isinstance(sm_full.get("fields"), list):
        schema_fields = len(sm_full["fields"])
    elif aspects:
        sm = aspects.get("schemaMetadata") or {}
        if isinstance(sm.get("fields"), list):
            schema_fields = len(sm["fields"])

    has_upstream = False
    if aspects and aspects.get("upstreamLineage"):
        has_upstream = bool((aspects["upstreamLineage"] or {}).get("upstreams"))
    up_full = entry.get("upstream") or entry.get("upstreamLineage")
    if up_full and not has_upstream:
        if isinstance(up_full, dict):
            has_upstream = bool(up_full.get("total") or up_full.get("upstreams"))

    return {
        "owners": owners, "tags": tags, "terms": terms,
        "domain": domain_urn, "schemaFields": schema_fields, "hasUpstream": has_upstream,
    }


def extract_fieldpaths(resp: Any) -> Set[str]:
    data = _result_payload(resp)
    fields = []
    if isinstance(data, dict):
        fields = data.get("fields") or []
    elif isinstance(data, list):
        fields = data
    return {f.get("fieldPath") for f in fields if isinstance(f, dict) and f.get("fieldPath")}


def extract_lineage_datasets(resp: Any) -> Set[str]:
    container = _lineage_container(resp)
    if container is None:
        return set()
    results = container.get("results") or container.get("searchResults") or []
    out: Set[str] = set()
    for r in results:
        if not isinstance(r, dict):
            continue
        entity = r.get("entity") or r
        urn_val = entity.get("urn") if isinstance(entity, dict) else None
        if isinstance(urn_val, str) and urn_val.startswith("urn:li:dataset:"):
            degree = r.get("degree")
            if degree is None or degree <= 1:
                out.add(urn_val)
    return out


def extract_lineage_all(resp: Any) -> Tuple[int, int, int]:
    container = _lineage_container(resp)
    if container is None:
        return 0, 0, 0
    results = container.get("results") or container.get("searchResults") or []
    n_ds = n_job = 0
    for r in results:
        if not isinstance(r, dict):
            continue
        entity = r.get("entity") or r
        urn_val = entity.get("urn") if isinstance(entity, dict) else None
        if not isinstance(urn_val, str):
            continue
        if urn_val.startswith("urn:li:dataset:"):
            n_ds += 1
        elif urn_val.startswith("urn:li:dataJob:"):
            n_job += 1
    return n_ds, n_job, len(results)


def extract_query_urns(resp: Any) -> Set[str]:
    data = _result_payload(resp)
    if not isinstance(data, dict):
        return set()
    queries = data.get("queries") or []
    return {q.get("urn") for q in queries if isinstance(q, dict) and q.get("urn")}


def extract_search_urns(resp: Any) -> Set[str]:
    data = _result_payload(resp)
    if not isinstance(data, dict):
        return set()
    results = data.get("results") or data.get("searchResults") or []
    out: Set[str] = set()
    for r in results:
        if not isinstance(r, dict):
            continue
        if r.get("urn"):
            out.add(r["urn"])
        ent = r.get("entity")
        if isinstance(ent, dict) and ent.get("urn"):
            out.add(ent["urn"])
    return out


def extract_path_count(resp: Any) -> int:
    if not isinstance(resp, dict):
        return 0
    if "pathCount" in resp:
        return resp["pathCount"] or 0
    if isinstance(resp.get("paths"), list):
        return len(resp["paths"])
    return 0


# ----------------------------------------------------------------------
# Per-tool runners
# ----------------------------------------------------------------------


def _summary_lines(s: Dict[str, Any]) -> List[str]:
    lines = [
        f"schemaFields: {s['schemaFields']}",
        f"hasUpstream:  {s['hasUpstream']}",
        f"domain:       {s['domain'] or '-'}",
        f"owners ({len(s['owners'])}):",
    ]
    lines += [f"  {o.split(':')[-1]}" for o in s["owners"]]
    lines.append(f"tags ({len(s['tags'])}):")
    lines += [f"  {t.split(':')[-1]}" for t in s["tags"]]
    lines.append(f"terms ({len(s['terms'])}):")
    lines += [f"  {t.split(':')[-1]}" for t in s["terms"]]
    return lines


def run_get_entities(full, lite, report: Report) -> None:
    for urn in test_cases.DATASETS:
        fs = extract_entity_summary(full.call("get_entities", {"urns": urn}), urn)
        ls = extract_entity_summary(lite.call("get_entities", {"urns": urn}), urn)
        match = all(fs[k] == ls[k] for k in ("owners", "tags", "terms", "domain", "schemaFields"))
        mismatches = [k for k in ("owners", "tags", "terms", "domain", "schemaFields") if fs[k] != ls[k]]
        note = ",".join(mismatches) if mismatches else "all attrs equal"
        report.add("get_entities", f"urn={_short(urn)}", _summary_lines(fs), _summary_lines(ls), match, note)


def run_list_schema_fields(full, lite, report: Report) -> None:
    for urn in test_cases.DATASETS_WITH_SCHEMA:
        ff = sorted(extract_fieldpaths(full.call("list_schema_fields", {"urn": urn, "limit": 500})))
        lf = sorted(extract_fieldpaths(lite.call("list_schema_fields", {"urn": urn, "limit": 500})))
        match = ff == lf
        note = f"full={len(ff)} lite={len(lf)}"
        if not ff and not lf:
            note += " (both empty — dataset has no schemaMetadata)"
        report.add("list_schema_fields", f"urn={_short(urn)}",
                   [f"fieldPath ({len(ff)})"] + [f"  {p}" for p in ff],
                   [f"fieldPath ({len(lf)})"] + [f"  {p}" for p in lf],
                   match, note)


def run_get_lineage(full, lite, report: Report) -> None:
    for urn in test_cases.DATASETS_WITH_LINEAGE + test_cases.DATASETS[:4]:
        for upstream in (True, False):
            f = full.call("get_lineage", {"urn": urn, "upstream": upstream, "max_hops": 1, "max_results": 500})
            l = lite.call("get_lineage", {"urn": urn, "upstream": upstream, "max_hops": 1, "max_results": 500})
            fs = sorted(extract_lineage_datasets(f))
            ls = sorted(extract_lineage_datasets(l))
            match = fs == ls
            fd, fj, ft = extract_lineage_all(f)
            ld, lj, lt = extract_lineage_all(l)
            note = f"full:ds={fd} job={fj} total={ft} | lite:ds={ld} job={lj} total={lt}"
            direction = "upstream" if upstream else "downstream"
            report.add(
                "get_lineage", f"{direction} · urn={_short(urn)}",
                [f"datasets ({len(fs)})"] + [f"  {_short(u)}" for u in fs],
                [f"datasets ({len(ls)})"] + [f"  {_short(u)}" for u in ls],
                match, note,
            )


def run_get_lineage_paths_between(full, lite, report: Report) -> None:
    for src, tgt in test_cases.LINEAGE_PAIRS:
        fp = extract_path_count(full.call("get_lineage_paths_between", {"source_urn": src, "target_urn": tgt}))
        lp = extract_path_count(lite.call("get_lineage_paths_between", {"source_urn": src, "target_urn": tgt}))
        match = fp > 0 and lp > 0
        report.add("get_lineage_paths_between", f"{_short(src)} → {_short(tgt)}",
                   [f"pathCount: {fp}"], [f"pathCount: {lp}"],
                   match, f"full_paths={fp} lite_paths={lp}")


def run_get_dataset_queries(full, lite, report: Report) -> None:
    for urn in test_cases.DATASETS_WITH_QUERIES:
        fq = sorted(extract_query_urns(full.call("get_dataset_queries", {"urn": urn, "count": 100})))
        lq = sorted(extract_query_urns(lite.call("get_dataset_queries", {"urn": urn, "count": 100})))
        match = fq == lq and len(fq) > 0
        report.add("get_dataset_queries", f"urn={_short(urn)}",
                   [f"queries ({len(fq)})"] + [f"  {q.split(':')[-1]}" for q in fq],
                   [f"queries ({len(lq)})"] + [f"  {q.split(':')[-1]}" for q in lq],
                   match, f"full={len(fq)} lite={len(lq)}")


def _search_total(resp: Any) -> int:
    data = _result_payload(resp)
    if isinstance(data, dict) and isinstance(data.get("total"), int):
        return data["total"]
    return -1


def _search_paginate(client, args: Dict[str, Any], page_size: int = 50, limit: int = 500) -> Tuple[int, Set[str]]:
    offset = 0
    urns: Set[str] = set()
    total = 0
    while offset < limit:
        resp = client.call("search", dict(args, num_results=page_size, offset=offset))
        total = _search_total(resp)
        page = extract_search_urns(resp)
        if not page:
            break
        urns |= page
        if len(urns) >= (total if total >= 0 else limit):
            break
        offset += page_size
    return total, urns


def run_search(full, lite, report: Report) -> None:
    for label, args in test_cases.SEARCH_CASES:
        ft, fu = _search_paginate(full, args)
        lt, lu = _search_paginate(lite, args)
        match = ft == lt and fu == lu
        notes = []
        if ft != lt:
            notes.append(f"total diff ({ft} vs {lt})")
        if fu != lu:
            notes.append(f"URN diff: only_full={len(fu - lu)}, only_lite={len(lu - fu)}")
        note = "; ".join(notes) or f"all {ft} URNs equal"
        report.add(
            "search", label,
            [f"total = {ft}", f"URNs ({len(fu)}):"] + [f"  {u.split(':', 3)[-1][:56]}" for u in sorted(fu)[:100]],
            [f"total = {lt}", f"URNs ({len(lu)}):"] + [f"  {u.split(':', 3)[-1][:56]}" for u in sorted(lu)[:100]],
            match, note,
        )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


RUNNERS: Dict[str, Callable] = {
    "get_entities": run_get_entities,
    "list_schema_fields": run_list_schema_fields,
    "get_lineage": run_get_lineage,
    "get_lineage_paths_between": run_get_lineage_paths_between,
    "get_dataset_queries": run_get_dataset_queries,
    "search": run_search,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tools", default=",".join(RUNNERS.keys()),
                        help="Comma-separated list. Default: all")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--col-width", type=int, default=60)
    parser.add_argument("--html", metavar="PATH", nargs="?", const="parity-report.html",
                        help="HTML 파일로도 출력 (default path: parity-report.html)")
    parser.add_argument("--open", action="store_true", help="HTML 생성 후 브라우저에서 열기")
    parser.add_argument("--quiet", action="store_true", help="터미널 상세 출력 생략 (요약만)")
    args = parser.parse_args()

    style = Style(not args.no_color)
    report = Report()

    print(style.bold("[*] Starting both MCP servers..."))
    full_args, full_env = full_client_args()
    lite_args, lite_env = lite_client_args()

    with McpStdioClient(full_args, env=full_env, name="full") as full, \
         McpStdioClient(lite_args, env=lite_env, name="lite") as lite:
        print(style.dim(f"    full tools: {len(full.list_tools())}, lite tools: {len(lite.list_tools())}"))

        for name in args.tools.split(","):
            name = name.strip()
            if name not in RUNNERS:
                print(style.red(f"unknown tool: {name}"))
                continue
            print(style.bold(f"[*] running {name}..."))
            RUNNERS[name](full, lite, report)

    if not args.quiet:
        render_terminal(report, style, args.col_width)

    print()
    print(style.bold("══ SUMMARY ═══════════════════════════════════════════════════"))
    total_fails = 0
    for tool, p, f_ in report.summary():
        status = style.green("OK") if f_ == 0 else style.red(f"{f_} DIFF")
        print(f"  {status:<30s}  {tool}  ({p} match / {f_} diff)")
        total_fails += f_

    if args.html:
        out_path = os.path.abspath(args.html)
        render_html(report, out_path)
        print()
        print(style.bold(f"[*] HTML report -> {out_path}"))
        if args.open:
            webbrowser.open(f"file://{out_path}")

    print()
    if total_fails == 0:
        print(style.green(f"ALL MATCH ({len(report.cases)} cases)"))
        return 0
    print(style.red(f"TOTAL DIFFS: {total_fails} / {len(report.cases)}"))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
