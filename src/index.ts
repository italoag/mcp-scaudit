#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { execFile } from "child_process";
import { promisify } from "util";
import { readFile, access } from "fs/promises";
import { constants } from "fs";

const execFileAsync = promisify(execFile);

interface AuditResult {
  success: boolean;
  output?: string;
  error?: string;
  findings?: any[];
}

/**
 * Check if a command exists in the system
 */
async function commandExists(command: string): Promise<boolean> {
  try {
    await execFileAsync("which", [command]);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if a file exists
 */
async function fileExists(path: string): Promise<boolean> {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

/**
 * Run Slither analysis on a smart contract
 */
async function runSlither(
  contractPath: string,
  options?: { detectors?: string; excludeDetectors?: string }
): Promise<AuditResult> {
  try {
    const exists = await fileExists(contractPath);
    if (!exists) {
      return {
        success: false,
        error: `Contract file not found: ${contractPath}`,
      };
    }

    const hasSlither = await commandExists("slither");
    if (!hasSlither) {
      return {
        success: false,
        error:
          "Slither is not installed. Please install it with: pip install slither-analyzer",
      };
    }

    const args = [contractPath, "--json", "-"];
    if (options?.detectors) {
      args.push("--detect", options.detectors);
    }
    if (options?.excludeDetectors) {
      args.push("--exclude", options.excludeDetectors);
    }

    const { stdout, stderr } = await execFileAsync("slither", args, {
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
    });

    let findings = [];
    try {
      const jsonOutput = JSON.parse(stdout);
      findings = jsonOutput.results?.detectors || [];
    } catch {
      // If JSON parsing fails, return raw output
    }

    return {
      success: true,
      output: stdout,
      findings,
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Slither analysis failed: ${error.message}`,
      output: error.stderr || error.stdout,
    };
  }
}

/**
 * Run Aderyn analysis on a smart contract
 */
async function runAderyn(contractPath: string): Promise<AuditResult> {
  try {
    const exists = await fileExists(contractPath);
    if (!exists) {
      return {
        success: false,
        error: `Contract file not found: ${contractPath}`,
      };
    }

    const hasAderyn = await commandExists("aderyn");
    if (!hasAderyn) {
      return {
        success: false,
        error:
          "Aderyn is not installed. Please install it with: cargo install aderyn",
      };
    }

    const { stdout, stderr } = await execFileAsync("aderyn", [contractPath], {
      maxBuffer: 10 * 1024 * 1024,
    });

    return {
      success: true,
      output: stdout,
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Aderyn analysis failed: ${error.message}`,
      output: error.stderr || error.stdout,
    };
  }
}

/**
 * Run Mythril analysis on a smart contract
 */
async function runMythril(
  contractPath: string,
  options?: { executionTimeout?: number }
): Promise<AuditResult> {
  try {
    const exists = await fileExists(contractPath);
    if (!exists) {
      return {
        success: false,
        error: `Contract file not found: ${contractPath}`,
      };
    }

    const hasMythril = await commandExists("myth");
    if (!hasMythril) {
      return {
        success: false,
        error:
          "Mythril is not installed. Please install it with: pip install mythril",
      };
    }

    const args = ["analyze", contractPath, "-o", "json"];
    if (options?.executionTimeout) {
      args.push("--execution-timeout", options.executionTimeout.toString());
    }

    const { stdout } = await execFileAsync("myth", args, {
      maxBuffer: 10 * 1024 * 1024,
    });

    let findings = [];
    try {
      const jsonOutput = JSON.parse(stdout);
      findings = jsonOutput.issues || [];
    } catch {
      // If JSON parsing fails, return raw output
    }

    return {
      success: true,
      output: stdout,
      findings,
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Mythril analysis failed: ${error.message}`,
      output: error.stderr || error.stdout,
    };
  }
}

/**
 * Read and analyze a contract file for basic patterns
 */
async function analyzeContractPatterns(
  contractPath: string
): Promise<AuditResult> {
  try {
    const exists = await fileExists(contractPath);
    if (!exists) {
      return {
        success: false,
        error: `Contract file not found: ${contractPath}`,
      };
    }

    const content = await readFile(contractPath, "utf-8");
    const findings: string[] = [];

    // Basic pattern checks
    if (content.includes("selfdestruct")) {
      findings.push(
        "WARNING: Contract contains selfdestruct - potential security risk"
      );
    }

    if (content.includes("delegatecall")) {
      findings.push(
        "WARNING: Contract uses delegatecall - ensure proper access control"
      );
    }

    if (content.includes("tx.origin")) {
      findings.push(
        "WARNING: Contract uses tx.origin - vulnerable to phishing attacks"
      );
    }

    // Check for Solidity version
    const versionMatch = content.match(/pragma solidity\s+[\^]?([\d.]+)/);
    const isSolidity08Plus =
      versionMatch && parseFloat(versionMatch[1]) >= 0.8;

    if (!content.includes("SafeMath") && content.match(/\+|\-|\*|\//) && !isSolidity08Plus) {
      findings.push(
        "WARNING: Consider using SafeMath library or upgrading to Solidity 0.8+ for arithmetic overflow protection"
      );
    }

    if (content.includes("block.timestamp")) {
      findings.push(
        "INFO: Contract uses block.timestamp - be aware of miner manipulation"
      );
    }

    const reentrancyPattern = /\.call\{value:/;
    if (reentrancyPattern.test(content)) {
      findings.push(
        "WARNING: Potential reentrancy risk - ensure checks-effects-interactions pattern"
      );
    }

    return {
      success: true,
      output: findings.length > 0 
        ? `Pattern Analysis Results:\n\n${findings.join('\n')}\n\nTotal: ${findings.length} potential issues found`
        : 'No security issues found in pattern analysis',
      findings,
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Pattern analysis failed: ${error.message}`,
    };
  }
}

/**
 * Read contract source code
 */
async function readContract(contractPath: string): Promise<AuditResult> {
  try {
    const exists = await fileExists(contractPath);
    if (!exists) {
      return {
        success: false,
        error: `Contract file not found: ${contractPath}`,
      };
    }

    const content = await readFile(contractPath, "utf-8");
    return {
      success: true,
      output: content,
    };
  } catch (error: any) {
    return {
      success: false,
      error: `Failed to read contract: ${error.message}`,
    };
  }
}

/**
 * Check availability of audit tools
 */
async function checkTools(): Promise<AuditResult> {
  const tools = {
    slither: await commandExists("slither"),
    aderyn: await commandExists("aderyn"),
    mythril: await commandExists("myth"),
  };

  const available = Object.entries(tools)
    .filter(([_, exists]) => exists)
    .map(([tool]) => tool);

  const missing = Object.entries(tools)
    .filter(([_, exists]) => !exists)
    .map(([tool]) => tool);

  return {
    success: true,
    output: JSON.stringify(
      {
        available,
        missing,
        installInstructions: {
          slither: "pip install slither-analyzer",
          aderyn: "cargo install aderyn",
          mythril: "pip install mythril",
        },
      },
      null,
      2
    ),
    findings: [tools],
  };
}

const server = new Server(
  {
    name: "mcp-scaudit",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const tools: Tool[] = [
  {
    name: "slither_audit",
    description:
      "Run Slither static analysis on a smart contract. Slither is a powerful Solidity & Vyper static analysis framework that detects vulnerabilities and code quality issues.",
    inputSchema: {
      type: "object",
      properties: {
        contract_path: {
          type: "string",
          description: "Path to the smart contract file (.sol or .vy)",
        },
        detectors: {
          type: "string",
          description:
            "Optional: Comma-separated list of specific detectors to run",
        },
        exclude_detectors: {
          type: "string",
          description: "Optional: Comma-separated list of detectors to exclude",
        },
      },
      required: ["contract_path"],
    },
  },
  {
    name: "aderyn_audit",
    description:
      "Run Aderyn static analysis on a smart contract. Aderyn is a Rust-based static analyzer for Solidity that focuses on finding common vulnerabilities and code smells.",
    inputSchema: {
      type: "object",
      properties: {
        contract_path: {
          type: "string",
          description: "Path to the smart contract file or project root",
        },
      },
      required: ["contract_path"],
    },
  },
  {
    name: "mythril_audit",
    description:
      "Run Mythril symbolic execution analysis on a smart contract. Mythril uses symbolic execution to detect security vulnerabilities in Ethereum smart contracts.",
    inputSchema: {
      type: "object",
      properties: {
        contract_path: {
          type: "string",
          description: "Path to the smart contract file (.sol)",
        },
        execution_timeout: {
          type: "number",
          description:
            "Optional: Maximum execution time in seconds (default: 300)",
        },
      },
      required: ["contract_path"],
    },
  },
  {
    name: "pattern_analysis",
    description:
      "Perform basic pattern-based security analysis on a smart contract. Checks for common anti-patterns and potential vulnerabilities like reentrancy, tx.origin usage, selfdestruct, etc.",
    inputSchema: {
      type: "object",
      properties: {
        contract_path: {
          type: "string",
          description: "Path to the smart contract file",
        },
      },
      required: ["contract_path"],
    },
  },
  {
    name: "read_contract",
    description:
      "Read and return the source code of a smart contract file. Useful for reviewing the contract before or after analysis.",
    inputSchema: {
      type: "object",
      properties: {
        contract_path: {
          type: "string",
          description: "Path to the smart contract file",
        },
      },
      required: ["contract_path"],
    },
  },
  {
    name: "check_tools",
    description:
      "Check which audit tools are installed and available on the system. Returns a list of available and missing tools with installation instructions.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
];

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result: AuditResult;

    switch (name) {
      case "slither_audit": {
        const contractPath = args?.contract_path as string;
        const detectors = args?.detectors as string | undefined;
        const excludeDetectors = args?.exclude_detectors as string | undefined;
        result = await runSlither(contractPath, { detectors, excludeDetectors });
        break;
      }

      case "aderyn_audit": {
        const contractPath = args?.contract_path as string;
        result = await runAderyn(contractPath);
        break;
      }

      case "mythril_audit": {
        const contractPath = args?.contract_path as string;
        const executionTimeout = args?.execution_timeout as number | undefined;
        result = await runMythril(contractPath, { executionTimeout });
        break;
      }

      case "pattern_analysis": {
        const contractPath = args?.contract_path as string;
        result = await analyzeContractPatterns(contractPath);
        break;
      }

      case "read_contract": {
        const contractPath = args?.contract_path as string;
        result = await readContract(contractPath);
        break;
      }

      case "check_tools": {
        result = await checkTools();
        break;
      }

      default:
        return {
          content: [
            {
              type: "text",
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }

    if (!result.success) {
      return {
        content: [
          {
            type: "text",
            text: result.error || "Unknown error occurred",
          },
        ],
        isError: true,
      };
    }

    return {
      content: [
        {
          type: "text",
          text: result.output || JSON.stringify(result.findings, null, 2),
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error executing tool: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Smart Contract Auditor Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
