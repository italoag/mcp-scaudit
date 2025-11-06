#!/usr/bin/env python3
"""
MCP Smart Contract Auditor Server - Python Implementation
A Model Context Protocol (MCP) server for auditing smart contracts using Slither, Mythril, and other tools.
"""

import asyncio
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


TOOL_INSTALL_INSTRUCTIONS: Dict[str, str] = {
    "slither": "pip install slither-analyzer",
    "aderyn": "curl -LsSf https://raw.githubusercontent.com/Cyfrin/up/main/install | bash && CYFRINUP_ONLY_INSTALL=aderyn cyfrinup",
    "mythril": "pip install mythril",
}


TOOL_VERSION_COMMANDS: Dict[str, List[List[str]]] = {
    "slither": [["slither", "--version"]],
    "aderyn": [["aderyn", "--version"]],
    "mythril": [["myth", "--version"], ["myth", "version"]],
}


@dataclass
class AuditResult:
    """Result of an audit operation."""

    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    findings: List[Any] = field(default_factory=list)


def command_exists(command: str) -> bool:
    """Check if a command exists in the system."""
    return shutil.which(command) is not None


def file_exists(path: Optional[str]) -> bool:
    """Check if a file exists."""
    if not path:
        return False
    return Path(path).is_file()


async def run_slither(contract_path: Optional[str], 
                      detectors: Optional[str] = None,
                      exclude_detectors: Optional[str] = None) -> AuditResult:
    """Run Slither analysis on a smart contract."""
    try:
        if not contract_path:
            return AuditResult(
                success=False,
                error="Missing required argument: contract_path"
            )

        if not file_exists(contract_path):
            return AuditResult(
                success=False,
                error=f"Contract file not found: {contract_path}"
            )
        
        if not command_exists("slither"):
            return AuditResult(
                success=False,
                error="Slither is not installed. Please install it with: pip install slither-analyzer"
            )
        
        args = ["slither", contract_path, "--json", "-"]
        if detectors:
            args.extend(["--detect", detectors])
        if exclude_detectors:
            args.extend(["--exclude", exclude_detectors])
        
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            message = error_output or f"Slither exited with code {result.returncode}"
            return AuditResult(success=False, error=f"Slither analysis failed: {message}")
        
        findings = []
        try:
            json_output = json.loads(result.stdout)
            findings = json_output.get("results", {}).get("detectors", [])
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw output
            pass
        
        return AuditResult(
            success=True,
            output=result.stdout,
            findings=findings
        )
    except subprocess.TimeoutExpired:
        return AuditResult(
            success=False,
            error="Slither analysis timed out"
        )
    except Exception as e:
        return AuditResult(
            success=False,
            error=f"Slither analysis failed: {str(e)}"
        )


async def run_aderyn(contract_path: Optional[str]) -> AuditResult:
    """Run Aderyn analysis on a smart contract"""
    try:
        if not file_exists(contract_path):
            return AuditResult(
                success=False,
                error=f"Contract file not found: {contract_path}"
            )
        
        if not command_exists("aderyn"):
            return AuditResult(
                success=False,
                error=(
                    "Aderyn is not installed. Install it with Cyfrinup: "
                    "curl -LsSf https://raw.githubusercontent.com/Cyfrin/up/main/install | bash && "
                    "CYFRINUP_ONLY_INSTALL=aderyn cyfrinup"
                ),
            )
        
        result = subprocess.run(
            ["aderyn", contract_path],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            message = error_output or f"Aderyn exited with code {result.returncode}"
            return AuditResult(success=False, error=f"Aderyn analysis failed: {message}")
        
        return AuditResult(
            success=True,
            output=result.stdout
        )
    except subprocess.TimeoutExpired:
        return AuditResult(
            success=False,
            error="Aderyn analysis timed out"
        )
    except Exception as e:
        return AuditResult(
            success=False,
            error=f"Aderyn analysis failed: {str(e)}"
        )


async def run_mythril(contract_path: Optional[str], 
                      execution_timeout: Optional[int] = None) -> AuditResult:
    """Run Mythril analysis on a smart contract"""
    try:
        if not file_exists(contract_path):
            return AuditResult(
                success=False,
                error=f"Contract file not found: {contract_path}"
            )
        
        if not command_exists("myth"):
            return AuditResult(
                success=False,
                error="Mythril is not installed. Please install it with: pip install mythril"
            )
        
        args = ["myth", "analyze", contract_path, "-o", "json"]
        if execution_timeout:
            args.extend(["--execution-timeout", str(execution_timeout)])
        
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            message = error_output or f"Mythril exited with code {result.returncode}"
            return AuditResult(success=False, error=f"Mythril analysis failed: {message}")
        
        findings = []
        try:
            json_output = json.loads(result.stdout)
            findings = json_output.get("issues", [])
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw output
            pass
        
        return AuditResult(
            success=True,
            output=result.stdout,
            findings=findings
        )
    except subprocess.TimeoutExpired:
        return AuditResult(
            success=False,
            error="Mythril analysis timed out"
        )
    except Exception as e:
        return AuditResult(
            success=False,
            error=f"Mythril analysis failed: {str(e)}"
        )


async def analyze_contract_patterns(contract_path: Optional[str]) -> AuditResult:
    """Read and analyze a contract file for basic patterns"""
    try:
        if not file_exists(contract_path):
            return AuditResult(
                success=False,
                error=f"Contract file not found: {contract_path}"
            )
        
        with open(contract_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        findings = []
        
        # Basic pattern checks
        if "selfdestruct" in content:
            findings.append(
                "WARNING: Contract contains selfdestruct - potential security risk"
            )
        
        if "delegatecall" in content:
            findings.append(
                "WARNING: Contract uses delegatecall - ensure proper access control"
            )
        
        if "tx.origin" in content:
            findings.append(
                "WARNING: Contract uses tx.origin - vulnerable to phishing attacks"
            )
        
        # Check for Solidity version
        version_match = re.search(r'pragma solidity\s+[\^]?([\d.]+)', content)
        is_solidity_08_plus = False
        if version_match:
            version_str = version_match.group(1)
            try:
                major, minor = version_str.split('.')[:2]
                is_solidity_08_plus = int(major) == 0 and int(minor) >= 8
            except (ValueError, IndexError):
                pass
        
        if "SafeMath" not in content and re.search(r'[\+\-\*\/]', content) and not is_solidity_08_plus:
            findings.append(
                "WARNING: Consider using SafeMath library or upgrading to Solidity 0.8+ for arithmetic overflow protection"
            )
        
        if "block.timestamp" in content:
            findings.append(
                "INFO: Contract uses block.timestamp - be aware of miner manipulation"
            )
        
        if re.search(r'\.call\{value:', content):
            findings.append(
                "WARNING: Potential reentrancy risk - ensure checks-effects-interactions pattern"
            )
        
        if findings:
            output_lines = [
                "Pattern Analysis Results:",
                "",
                *findings,
                "",
                f"Total: {len(findings)} potential issues found",
            ]
            output_msg = "\n".join(output_lines)
        else:
            output_msg = "No security issues found in pattern analysis"
        
        return AuditResult(
            success=True,
            output=output_msg,
            findings=findings
        )
    except Exception as e:
        return AuditResult(
            success=False,
            error=f"Pattern analysis failed: {str(e)}"
        )


async def read_contract(contract_path: Optional[str]) -> AuditResult:
    """Read contract source code."""
    try:
        if not file_exists(contract_path):
            return AuditResult(
                success=False,
                error=f"Contract file not found: {contract_path}"
            )
        
        with open(contract_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return AuditResult(
            success=True,
            output=content
        )
    except Exception as e:
        return AuditResult(
            success=False,
            error=f"Failed to read contract: {str(e)}"
        )


def _get_tool_version(commands: List[List[str]]) -> Optional[str]:
    """Attempt to retrieve a tool version using the provided commands."""
    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            continue

        if result.returncode != 0:
            continue

        candidate = (result.stdout or result.stderr or "").strip()
        if candidate:
            return candidate.splitlines()[0]

    return None


async def check_tools() -> AuditResult:
    """Check availability of audit tools."""
    tool_status: Dict[str, Dict[str, Optional[str]]] = {}

    for tool, binary in {
        "slither": "slither",
        "aderyn": "aderyn",
        "mythril": "myth",
    }.items():
        installed = command_exists(binary)
        version = None
        if installed:
            version = _get_tool_version(TOOL_VERSION_COMMANDS.get(tool, []))

        tool_status[tool] = {
            "installed": installed,
            "version": version,
        }

    available = [name for name, status in tool_status.items() if status["installed"]]
    missing = [name for name in tool_status if name not in available]

    payload = {
        "available": available,
        "missing": missing,
        "toolDetails": tool_status,
        "installInstructions": TOOL_INSTALL_INSTRUCTIONS,
    }

    return AuditResult(
        success=True,
        output=json.dumps(payload, indent=2),
        findings=[tool_status],
    )


def get_tool_definitions() -> List[Tool]:
    """Return the MCP tool definitions exposed by this server."""

    return [
        Tool(
            name="slither_audit",
            description=(
                "Run Slither static analysis on a smart contract. Slither is a powerful "
                "Solidity & Vyper static analysis framework that detects vulnerabilities and "
                "code quality issues."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_path": {
                        "type": "string",
                        "description": "Path to the smart contract file (.sol or .vy)",
                    },
                    "detectors": {
                        "type": "string",
                        "description": "Optional: Comma-separated list of specific detectors to run",
                    },
                    "exclude_detectors": {
                        "type": "string",
                        "description": "Optional: Comma-separated list of detectors to exclude",
                    },
                },
                "required": ["contract_path"],
            },
        ),
        Tool(
            name="aderyn_audit",
            description=(
                "Run Aderyn static analysis on a smart contract. Aderyn is a Rust-based static "
                "analyzer for Solidity that focuses on finding common vulnerabilities and code smells."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_path": {
                        "type": "string",
                        "description": "Path to the smart contract file or project root",
                    },
                },
                "required": ["contract_path"],
            },
        ),
        Tool(
            name="mythril_audit",
            description=(
                "Run Mythril symbolic execution analysis on a smart contract. Mythril uses "
                "symbolic execution to detect security vulnerabilities in Ethereum smart contracts."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_path": {
                        "type": "string",
                        "description": "Path to the smart contract file (.sol)",
                    },
                    "execution_timeout": {
                        "type": "number",
                        "description": "Optional: Maximum execution time in seconds (default: 300)",
                    },
                },
                "required": ["contract_path"],
            },
        ),
        Tool(
            name="pattern_analysis",
            description=(
                "Perform basic pattern-based security analysis on a smart contract. Checks for "
                "common anti-patterns and potential vulnerabilities like reentrancy, tx.origin usage, "
                "selfdestruct, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_path": {
                        "type": "string",
                        "description": "Path to the smart contract file",
                    },
                },
                "required": ["contract_path"],
            },
        ),
        Tool(
            name="read_contract",
            description=(
                "Read and return the source code of a smart contract file. Useful for reviewing the "
                "contract before or after analysis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_path": {
                        "type": "string",
                        "description": "Path to the smart contract file",
                    },
                },
                "required": ["contract_path"],
            },
        ),
        Tool(
            name="check_tools",
            description=(
                "Check which audit tools are installed and available on the system. Returns a list of "
                "available and missing tools with installation instructions."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


async def execute_tool(name: str, arguments: Dict[str, Any]) -> AuditResult:
    """Dispatch execution to the correct tool handler."""

    if name == "slither_audit":
        contract_path = arguments.get("contract_path")
        detectors = arguments.get("detectors")
        exclude_detectors = arguments.get("exclude_detectors")
        return await run_slither(contract_path, detectors, exclude_detectors)

    if name == "aderyn_audit":
        contract_path = arguments.get("contract_path")
        return await run_aderyn(contract_path)

    if name == "mythril_audit":
        contract_path = arguments.get("contract_path")
        execution_timeout = arguments.get("execution_timeout")
        return await run_mythril(contract_path, execution_timeout)

    if name == "pattern_analysis":
        contract_path = arguments.get("contract_path")
        return await analyze_contract_patterns(contract_path)

    if name == "read_contract":
        contract_path = arguments.get("contract_path")
        return await read_contract(contract_path)

    if name == "check_tools":
        return await check_tools()

    return AuditResult(success=False, error=f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server"""
    server = Server("farofino-mcp")
    tools = get_tool_definitions()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return tools
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            result = await execute_tool(name, arguments)

            if not result.success:
                return [TextContent(
                    type="text",
                    text=result.error or "Unknown error occurred",
                )]

            payload = result.output
            if payload is None and result.findings:
                payload = json.dumps(result.findings, indent=2)

            return [TextContent(
                type="text",
                text=payload or "",
            )]

        except Exception as exc:  # pragma: no cover - defensive guard
            return [TextContent(
                type="text",
                text=f"Error executing tool: {exc}",
            )]
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        print("MCP Smart Contract Auditor Server running on stdio", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def run():
    """Entry point for the console script"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
