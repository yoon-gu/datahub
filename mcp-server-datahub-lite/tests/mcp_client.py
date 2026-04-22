"""Minimal synchronous stdio JSON-RPC client for MCP servers.

Starts a server subprocess, performs the MCP handshake, and exposes
`call(tool_name, **args)` that returns the parsed tool result as a Python dict.
Used by the parity test suite to drive both `mcp-server-datahub` (full,
GMS-backed) and `mcp-server-datahub-lite` (DuckDB-backed) side by side.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional


class McpStdioClient:
    def __init__(
        self,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        name: str = "client",
        startup_timeout: float = 60.0,
    ):
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        self.name = name
        self.proc = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
            text=True,
            bufsize=1,
        )
        self._next_id = 1
        self._lock = threading.Lock()
        self._stderr_buf: List[str] = []
        self._stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr_thread.start()
        self._handshake(timeout=startup_timeout)

    def _drain_stderr(self) -> None:
        assert self.proc.stderr is not None
        for line in self.proc.stderr:
            self._stderr_buf.append(line)

    def _send(self, obj: Dict[str, Any]) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _recv(self, timeout: float = 60.0) -> Dict[str, Any]:
        assert self.proc.stdout is not None
        deadline = time.time() + timeout
        while True:
            line = self.proc.stdout.readline()
            if not line:
                if self.proc.poll() is not None:
                    raise RuntimeError(
                        f"[{self.name}] server exited (code={self.proc.returncode}). stderr tail:\n"
                        + "".join(self._stderr_buf[-20:])
                    )
                if time.time() > deadline:
                    raise TimeoutError(f"[{self.name}] no stdout response within {timeout}s")
                time.sleep(0.02)
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

    def _handshake(self, timeout: float) -> None:
        with self._lock:
            self._send(
                {
                    "jsonrpc": "2.0",
                    "id": self._next_id,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "parity-tests", "version": "0"},
                    },
                }
            )
            self._next_id += 1
            self._recv(timeout=timeout)
            self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def list_tools(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._send({"jsonrpc": "2.0", "id": self._next_id, "method": "tools/list"})
            self._next_id += 1
            resp = self._recv()
        return resp["result"]["tools"]

    def call(self, name: str, arguments: Optional[Dict[str, Any]] = None, timeout: float = 60.0) -> Any:
        with self._lock:
            req_id = self._next_id
            self._next_id += 1
            self._send(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "method": "tools/call",
                    "params": {"name": name, "arguments": arguments or {}},
                }
            )
            resp = self._recv(timeout=timeout)

        if "error" in resp:
            raise RuntimeError(f"[{self.name}] tool {name} error: {resp['error']}")

        content = resp.get("result", {}).get("content") or []
        structured = resp.get("result", {}).get("structuredContent")
        if structured is not None:
            return structured
        for item in content:
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except Exception:
                    return item["text"]
        return resp.get("result", {})

    def close(self) -> None:
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass

    def __enter__(self) -> "McpStdioClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


def full_client_args() -> tuple[List[str], Dict[str, str]]:
    """Command + env for the upstream `mcp-server-datahub` (GMS-backed)."""
    uvx = os.environ.get("UVX_BIN", os.path.expanduser("~/.local/bin/uvx"))
    gms_url = os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080")
    gms_token = os.environ.get("DATAHUB_GMS_TOKEN")
    if not gms_token:
        raise RuntimeError("DATAHUB_GMS_TOKEN is required to drive the full mcp-server-datahub")
    return (
        [uvx, "mcp-server-datahub@latest"],
        {"DATAHUB_GMS_URL": gms_url, "DATAHUB_GMS_TOKEN": gms_token},
    )


def lite_client_args() -> tuple[List[str], Dict[str, str]]:
    """Command + env for the lite server (DuckDB-backed)."""
    bin_path = os.environ.get("LITE_BIN")
    if bin_path is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        candidate = os.path.join(repo_root, ".venv", "bin", "mcp-server-datahub-lite")
        bin_path = candidate if os.path.exists(candidate) else "mcp-server-datahub-lite"
    lite_db = os.environ.get("DATAHUB_LITE_DB", os.path.expanduser("~/.datahub/lite/datahub.duckdb"))
    return (
        [bin_path, "--transport", "stdio", "--lite-db", lite_db],
        {},
    )
