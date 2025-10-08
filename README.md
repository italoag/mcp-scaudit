# mcp-scaudit

A Model Context Protocol (MCP) server for auditing smart contracts using industry-standard tools like Slither, Aderyn, Mythril, and custom pattern analysis.

## Overview

This MCP server provides a unified interface for running multiple smart contract security analysis tools through the Model Context Protocol. It enables AI assistants and other MCP clients to perform comprehensive security audits on Solidity and Vyper smart contracts.

## Features

- **Slither Integration**: Static analysis framework for Solidity & Vyper
- **Aderyn Integration**: Rust-based static analyzer for Solidity
- **Mythril Integration**: Symbolic execution analysis for vulnerability detection
- **Pattern Analysis**: Custom pattern-based security checks for common vulnerabilities
- **Contract Reading**: Read and inspect contract source code
- **Tool Management**: Check which audit tools are installed and get installation instructions

## Installation

### Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn

### Install the MCP Server

```bash
npm install -g mcp-scaudit
```

Or install locally:

```bash
git clone https://github.com/italoag/mcp-scaudit.git
cd mcp-scaudit
npm install
npm run build
```

### Install Audit Tools (Optional)

The server works with various external audit tools. Install the ones you need:

#### Slither
```bash
pip install slither-analyzer
```

#### Aderyn
```bash
cargo install aderyn
```

#### Mythril
```bash
pip install mythril
```

You can check which tools are installed using the `check_tools` command.

## Usage

### Running the Server

```bash
npx mcp-scaudit
```

Or if installed globally:
```bash
mcp-scaudit
```

### Available Tools

#### 1. slither_audit

Run Slither static analysis on a smart contract.

**Parameters:**
- `contract_path` (required): Path to the contract file (.sol or .vy)
- `detectors` (optional): Comma-separated list of specific detectors to run
- `exclude_detectors` (optional): Comma-separated list of detectors to exclude

**Example:**
```json
{
  "contract_path": "/path/to/MyContract.sol",
  "detectors": "reentrancy-eth,unchecked-transfer"
}
```

#### 2. aderyn_audit

Run Aderyn static analysis on a smart contract.

**Parameters:**
- `contract_path` (required): Path to the contract file or project root

**Example:**
```json
{
  "contract_path": "/path/to/MyContract.sol"
}
```

#### 3. mythril_audit

Run Mythril symbolic execution analysis.

**Parameters:**
- `contract_path` (required): Path to the contract file (.sol)
- `execution_timeout` (optional): Maximum execution time in seconds

**Example:**
```json
{
  "contract_path": "/path/to/MyContract.sol",
  "execution_timeout": 300
}
```

#### 4. pattern_analysis

Perform basic pattern-based security analysis.

**Parameters:**
- `contract_path` (required): Path to the contract file

**Example:**
```json
{
  "contract_path": "/path/to/MyContract.sol"
}
```

Checks for:
- `selfdestruct` usage
- `delegatecall` usage
- `tx.origin` authentication
- Missing SafeMath (pre-0.8.0)
- `block.timestamp` manipulation risks
- Potential reentrancy patterns

#### 5. read_contract

Read and return the source code of a smart contract.

**Parameters:**
- `contract_path` (required): Path to the contract file

**Example:**
```json
{
  "contract_path": "/path/to/MyContract.sol"
}
```

#### 6. check_tools

Check which audit tools are installed and available.

**Parameters:** None

**Example:**
```json
{}
```

Returns a list of available and missing tools with installation instructions.

## Configuration with Claude Desktop

Add this to your Claude Desktop configuration file:

### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Location: `%APPDATA%/Claude/claude_desktop_config.json`

### Linux
Location: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "npx",
      "args": ["mcp-scaudit"]
    }
  }
}
```

Or if installed globally:
```json
{
  "mcpServers": {
    "scaudit": {
      "command": "mcp-scaudit"
    }
  }
}
```

## Example Workflow

1. **Check available tools:**
   ```
   Use check_tools to see which audit tools are installed
   ```

2. **Read the contract:**
   ```
   Use read_contract with contract_path="/path/to/contract.sol"
   ```

3. **Run pattern analysis (always available):**
   ```
   Use pattern_analysis with contract_path="/path/to/contract.sol"
   ```

4. **Run Slither analysis (if installed):**
   ```
   Use slither_audit with contract_path="/path/to/contract.sol"
   ```

5. **Run additional tools as needed:**
   - Aderyn for Rust-based analysis
   - Mythril for symbolic execution

## Development

### Building from Source

```bash
git clone https://github.com/italoag/mcp-scaudit.git
cd mcp-scaudit
npm install
npm run build
```

### Development Mode

```bash
npm run watch  # Watch for changes
npm run dev    # Build and run
```

### Project Structure

```
mcp-scaudit/
├── src/
│   └── index.ts          # Main server implementation
├── dist/                 # Built output (generated)
├── package.json          # Project dependencies
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

## Troubleshooting

### Tool not found errors

If you get errors about tools not being found:
1. Run the `check_tools` command to see which tools are installed
2. Install missing tools following the installation instructions above
3. Ensure the tools are in your system PATH

### Permission errors

If you get permission errors when running audit tools:
- Ensure the contract files are readable
- Check that audit tools have proper execution permissions

### Large contracts timing out

For large contracts or complex analysis:
- Use the `execution_timeout` parameter with Mythril
- Use `exclude_detectors` with Slither to skip certain checks
- Run pattern analysis first for a quick overview

## License

Apache-2.0

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Security

This tool is for educational and professional security auditing purposes. Always:
- Verify audit results manually
- Use multiple tools for comprehensive analysis
- Follow secure development best practices
- Never rely solely on automated tools for security guarantees
