#!/usr/bin/env python3
"""
MCP Smart Contract Auditor Server - Python Implementation
A Model Context Protocol (MCP) server for auditing smart contracts using Slither, Mythril, and other tools.
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class AuditResult:
    """Result of an audit operation"""
    
    def __init__(self, success: bool, output: Optional[str] = None, 
                 error: Optional[str] = None, findings: Optional[List[Any]] = None):
        self.success = success
        self.output = output
        self.error = error
        self.findings = findings or []


def command_exists(command: str) -> bool:
    """Check if a command exists in the system"""
    return shutil.which(command) is not None


def file_exists(path: str) -> bool:
    """Check if a file exists"""
    return Path(path).is_file()


async def run_slither(contract_path: str, 
                      detectors: Optional[str] = None,
                      exclude_detectors: Optional[str] = None) -> AuditResult:
    """Run Slither analysis on a smart contract"""
    try:
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


async def run_aderyn(contract_path: str) -> AuditResult:
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
                error="Aderyn is not installed. Please install it with: cargo install aderyn"
            )
        
        result = subprocess.run(
            ["aderyn", contract_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
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


async def run_mythril(contract_path: str, 
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


async def analyze_contract_patterns(contract_path: str) -> AuditResult:
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
        
        if not "SafeMath" in content and re.search(r'[\+\-\*\/]', content) and not is_solidity_08_plus:
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
        
        output_msg = (
            f"Pattern Analysis Results:\n\n{chr(10).join(findings)}\n\nTotal: {len(findings)} potential issues found"
            if findings
            else "No security issues found in pattern analysis"
        )
        
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


async def read_contract(contract_path: str) -> AuditResult:
    """Read contract source code"""
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


async def check_tools() -> AuditResult:
    """Check availability of audit tools"""
    tools = {
        "slither": command_exists("slither"),
        "aderyn": command_exists("aderyn"),
        "mythril": command_exists("myth"),
    }
    
    available = [tool for tool, exists in tools.items() if exists]
    missing = [tool for tool, exists in tools.items() if not exists]
    
    output = json.dumps(
        {
            "available": available,
            "missing": missing,
            "installInstructions": {
                "slither": "pip install slither-analyzer",
                "aderyn": "cargo install aderyn",
                "mythril": "pip install mythril",
            },
        },
        indent=2
    )
    
    return AuditResult(
        success=True,
        output=output,
        findings=[tools]
    )


async def main():
    """Main entry point for the MCP server"""
    server = Server("mcp-scaudit")
    
    # Define available tools
    tools = [
        Tool(
            name="slither_audit",
            description="Run Slither static analysis on a smart contract. Slither is a powerful Solidity & Vyper static analysis framework that detects vulnerabilities and code quality issues.",
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
            description="Run Aderyn static analysis on a smart contract. Aderyn is a Rust-based static analyzer for Solidity that focuses on finding common vulnerabilities and code smells.",
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
            description="Run Mythril symbolic execution analysis on a smart contract. Mythril uses symbolic execution to detect security vulnerabilities in Ethereum smart contracts.",
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
            description="Perform basic pattern-based security analysis on a smart contract. Checks for common anti-patterns and potential vulnerabilities like reentrancy, tx.origin usage, selfdestruct, etc.",
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
            description="Read and return the source code of a smart contract file. Useful for reviewing the contract before or after analysis.",
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
            description="Check which audit tools are installed and available on the system. Returns a list of available and missing tools with installation instructions.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return tools
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            result: AuditResult
            
            if name == "slither_audit":
                contract_path = arguments.get("contract_path")
                detectors = arguments.get("detectors")
                exclude_detectors = arguments.get("exclude_detectors")
                result = await run_slither(contract_path, detectors, exclude_detectors)
            
            elif name == "aderyn_audit":
                contract_path = arguments.get("contract_path")
                result = await run_aderyn(contract_path)
            
            elif name == "mythril_audit":
                contract_path = arguments.get("contract_path")
                execution_timeout = arguments.get("execution_timeout")
                result = await run_mythril(contract_path, execution_timeout)
            
            elif name == "pattern_analysis":
                contract_path = arguments.get("contract_path")
                result = await analyze_contract_patterns(contract_path)
            
            elif name == "read_contract":
                contract_path = arguments.get("contract_path")
                result = await read_contract(contract_path)
            
            elif name == "check_tools":
                result = await check_tools()
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            if not result.success:
                return [TextContent(
                    type="text",
                    text=result.error or "Unknown error occurred"
                )]
            
            return [TextContent(
                type="text",
                text=result.output or json.dumps(result.findings, indent=2)
            )]
        
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing tool: {str(e)}"
            )]
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        print("MCP Smart Contract Auditor Server running on stdio", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
