"""Shared test input set. Imported by both pytest and the side-by-side compare script.

확장 시엔 여기 한 곳만 늘리면 양쪽에 자동 반영됩니다.
"""

from __future__ import annotations


def ds(platform: str, name: str, env: str = "DEV") -> str:
    return f"urn:li:dataset:(urn:li:dataPlatform:{platform},{name},{env})"


def job(flow_orch: str, flow_id: str, job_id: str, env: str = "DEV") -> str:
    return f"urn:li:dataJob:(urn:li:dataFlow:({flow_orch},{flow_id},{env}),{job_id})"


# 대표성: 여러 플랫폼 + 여러 용도 (event/xseq/dtag/score/eval/model)
DATASETS = [
    # mysql / sequence_ai — 이벤트 테이블
    ds("mysql", "sequence_ai.cust_evnt_dtl_itm_dev"),
    ds("mysql", "sequence_ai.evt_A01"),
    ds("mysql", "sequence_ai.evt_B01"),
    ds("mysql", "sequence_ai.evt_K01"),
    # xseq 그룹
    ds("mysql", "sequence_ai.xseq_fin30d"),
    ds("mysql", "sequence_ai.xseq_churn30d"),
    # 모델 score / target_y / eval (ess4di = 카드론신청)
    ds("mysql", "sequence_ai.score_ess4di"),
    ds("mysql", "sequence_ai.target_y_ess4di"),
    # universe 플랫폼 — ptag/dtag
    ds("universe", "ptag_age_group"),
    ds("universe", "dtag_card_loan_pred"),
    ds("universe", "dtag_card_loan"),
    ds("universe", "dtag_churn_pred"),
    # 중간 테이블 (upstreamLineage 가 있는 dataset)
    ds("universe", "mid_A01"),
    ds("universe", "action_table"),
    ds("universe", "prediction_result"),
    # sequence_ai 대시보드 테이블
    ds("mysql", "sequence_ai.evaluation_report"),
]


DATASETS_WITH_SCHEMA = [
    ds("mysql", "sequence_ai.evt_A01"),
    ds("mysql", "sequence_ai.evt_B01"),
    ds("mysql", "sequence_ai.evt_K01"),
    ds("mysql", "sequence_ai.cust_evnt_dtl_itm_dev"),
    ds("mysql", "sequence_ai.hcc_sequence_data"),
    ds("mysql", "sequence_ai.score_ess4di"),
]


# upstreamLineage aspect 가 실제로 있는 dataset 들 (populate 확인됨)
DATASETS_WITH_LINEAGE = [
    ds("universe", "dtag_card_loan_pred"),
    ds("universe", "dtag_churn_pred"),
    ds("universe", "dtag_dormant_pred"),
    ds("universe", "action_table"),
    ds("universe", "mid_A01"),
    ds("universe", "mid_B01"),
    ds("universe", "sequence_data"),
    ds("universe", "prediction_result"),
    ds("universe", "goldilocks_diagnosis"),
]


# querySubjects 역인덱스로 확인된 쿼리 많은 dataset 들
DATASETS_WITH_QUERIES = [
    ds("mysql", "sequence_ai.cust_evnt_dtl_itm_dev"),   # 28 queries
    ds("mysql", "sequence_ai.xseq_fin30d"),             # 3
    ds("mysql", "sequence_ai.xseq_churn30d"),           # 3
    ds("mysql", "sequence_ai.evt_B01"),                 # 2
    ds("mysql", "sequence_ai.score_ess4di"),            # 2
    ds("mysql", "sequence_ai.target_y_ess4di"),         # 2
]


LINEAGE_PAIRS = [
    (ds("universe", "ptag_age_group"), ds("universe", "dtag_card_loan_pred")),
    (ds("universe", "ptag_card_loan_amt"), ds("universe", "dtag_card_loan_pred")),
    (ds("universe", "ptag_revolving_yn"), ds("universe", "dtag_churn_pred")),
]


SEARCH_CASES = [
    # (label, {query, filter})
    ("entity_type = query", {"query": "*", "filter": "entity_type = query"}),
    ("entity_type = dataFlow", {"query": "*", "filter": "entity_type = dataFlow"}),
    ("entity_type = mlModel", {"query": "*", "filter": "entity_type = mlModel"}),
    ("entity_type = tag", {"query": "*", "filter": "entity_type = tag"}),
    ("entity_type = glossaryTerm", {"query": "*", "filter": "entity_type = glossaryTerm"}),
    ("entity_type=dataset AND platform=mysql", {"query": "*", "filter": "entity_type = dataset AND platform = mysql"}),
]
