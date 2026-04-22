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


from tests.test_cases import (  # noqa: E402,F401
    DATASETS as SAMPLE_DATASETS,
    LINEAGE_PAIRS as SAMPLE_LINEAGE_PAIRS,
)
