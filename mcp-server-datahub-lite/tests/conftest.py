"""Shared pytest fixtures: spin up both MCP servers once per session."""

from __future__ import annotations

import pytest

from tests.mcp_client import (
    McpStdioClient,
    full_client_args,
    lite_client_args,
)


@pytest.fixture(scope="session")
def full_client() -> McpStdioClient:
    args, env = full_client_args()
    client = McpStdioClient(args, env=env, name="full")
    yield client
    client.close()


@pytest.fixture(scope="session")
def lite_client() -> McpStdioClient:
    args, env = lite_client_args()
    client = McpStdioClient(args, env=env, name="lite")
    yield client
    client.close()


SAMPLE_DATASETS = [
    "urn:li:dataset:(urn:li:dataPlatform:mysql,sequence_ai.cust_evnt_dtl_itm_dev,DEV)",
    "urn:li:dataset:(urn:li:dataPlatform:universe,ptag_age_group,DEV)",
    "urn:li:dataset:(urn:li:dataPlatform:universe,dtag_card_loan_pred,DEV)",
    "urn:li:dataset:(urn:li:dataPlatform:mysql,sequence_ai.evt_B01,DEV)",
]

SAMPLE_LINEAGE_PAIRS = [
    (
        "urn:li:dataset:(urn:li:dataPlatform:universe,ptag_age_group,DEV)",
        "urn:li:dataset:(urn:li:dataPlatform:universe,dtag_card_loan_pred,DEV)",
    ),
]
