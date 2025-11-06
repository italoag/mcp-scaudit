"""Unit tests for the farofino MCP server."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from farofino_mcp import __main__ as server


@pytest.mark.asyncio
async def test_run_slither_success(monkeypatch, tmp_path):
    contract = tmp_path / "Test.sol"
    contract.write_text("pragma solidity ^0.8.0; contract Test {}")

    monkeypatch.setattr(server, "command_exists", lambda name: name == "slither")

    def fake_run(args, capture_output, text, timeout):
        assert args[0] == "slither"
        payload = {"results": {"detectors": []}}
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(server.subprocess, "run", fake_run)

    result = await server.run_slither(str(contract))
    assert result.success
    assert result.findings == []


@pytest.mark.asyncio
async def test_run_slither_missing_file():
    result = await server.run_slither("/non/existent.sol")
    assert not result.success
    assert "Contract file not found" in (result.error or "")


@pytest.mark.asyncio
async def test_run_aderyn_requires_binary(monkeypatch, tmp_path):
    contract = tmp_path / "Test.sol"
    contract.write_text("pragma solidity ^0.8.0;")

    monkeypatch.setattr(server, "command_exists", lambda _: False)

    result = await server.run_aderyn(str(contract))
    assert not result.success
    assert "Aderyn is not installed" in (result.error or "")


@pytest.mark.asyncio
async def test_pattern_analysis_detects_warning(tmp_path):
    contract = tmp_path / "Risky.sol"
    contract.write_text(
        """// SPDX-License-Identifier: MIT\npragma solidity ^0.6.0;\ncontract Risky {\n    function bad(address target) external {\n        (bool ok, ) = target.call{value: 1 ether}("");\n        require(ok);\n    }\n}\n"""
    )

    result = await server.analyze_contract_patterns(str(contract))
    assert result.success
    assert any("reentrancy" in finding.lower() for finding in result.findings)


@pytest.mark.asyncio
async def test_read_contract_returns_source(tmp_path):
    contract = tmp_path / "Read.sol"
    contract.write_text("pragma solidity ^0.8.0;")

    result = await server.read_contract(str(contract))
    assert result.success
    assert "pragma solidity" in (result.output or "")


@pytest.mark.asyncio
async def test_check_tools_reports_availability(monkeypatch):
    states = {"slither": True, "aderyn": False}
    monkeypatch.setattr(server, "command_exists", lambda name: states.get(name, False))
    monkeypatch.setattr(server, "_get_tool_version", lambda cmds: "1.2.3")

    result = await server.check_tools()
    assert result.success

    payload = json.loads(result.output or "{}")
    assert payload["available"] == ["slither"]
    assert payload["missing"] == ["aderyn"]
    assert payload["toolDetails"]["slither"]["version"] == "1.2.3"


@pytest.mark.asyncio
async def test_execute_tool_unknown():
    result = await server.execute_tool("unknown", {})
    assert not result.success
    assert "Unknown tool" in (result.error or "")


@pytest.mark.asyncio
async def test_execute_tool_slither_missing_argument():
    result = await server.execute_tool("slither_audit", {})
    assert not result.success
    assert "Missing required argument" in (result.error or "")


def test_tool_definitions_match_expected():
    tool_names = {tool.name for tool in server.get_tool_definitions()}
    assert tool_names == {
        "slither_audit",
        "aderyn_audit",
        "pattern_analysis",
        "read_contract",
        "check_tools",
    }