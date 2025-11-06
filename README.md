# Faro Fino - Smart Contract Audit MCP Server

A Model Context Protocol (MCP) server for auditing smart contracts using industry-standard tools like Slither, Mythril, Aderyn, and custom pattern analysis.

## Overview

This MCP server provides a unified interface for running multiple smart contract security analysis tools through the Model Context Protocol. It enables AI assistants and other MCP clients to perform comprehensive security audits on Solidity and Vyper smart contracts.

## Features

- **Slither Integration**: Static analysis framework for Solidity & Vyper
- **Mythril Integration**: Symbolic execution analysis for vulnerability detection
- **Aderyn Integration**: Rust-based static analyzer for Solidity
- **Pattern Analysis**: Custom pattern-based security checks for common vulnerabilities
- **Contract Reading**: Read and inspect contract source code
- **Tool Management**: Check which audit tools are installed and get installation instructions

## Installation

### Option 1: Docker (Recommended - All Tools Pre-installed) 🐳

Use Docker for a hassle-free setup with all audit tools pre-installed:

```bash
# Clone the repository
git clone https://github.com/italoag/farofino-mcp.git
cd farofino-mcp

# Build and run with Docker Compose
docker-compose build
docker-compose run --rm farofino-mcp
```

**If you encounter network timeout errors during build**, see [DOCKER_NETWORK_TIMEOUT.md](DOCKER_NETWORK_TIMEOUT.md) for quick fixes or use:

```bash
make build-retry  # Automatically handles network issues
```

**Advantages:**

- ✅ Aderyn, Slither, and Mythril pre-installed
- ✅ Consistent environment across all platforms
- ✅ No dependency conflicts
- ✅ Optimized slim image (~1.3-1.4GB)

See [DOCKER.md](DOCKER.md) for detailed Docker setup and configuration.

### Option 2: pip Installation

#### Prerequisites

- Python 3.9 or higher
- pip

#### Install the MCP Server

```bash
pip install farofino-mcp
```

Or install locally from source:

```bash
git clone https://github.com/italoag/farofino-mcp.git
cd farofino-mcp
pip install -r requirements.txt
pip install -e .
```

#### Install Audit Tools (Optional)

The server works with various external audit tools. Install the ones you need:

**Slither:**

```bash
pip install slither-analyzer
```

**Aderyn:** (via [Cyfrinup](https://github.com/Cyfrin/up))

```bash
curl -LsSf https://raw.githubusercontent.com/Cyfrin/up/main/install | bash
CYFRINUP_ONLY_INSTALL=aderyn cyfrinup
```

**Mythril:**

```bash
pip install mythril
```

You can check which tools are installed using the `check_tools` command.

## Usage

### With Docker

```bash
# Using Docker Compose
docker-compose run --rm farofino-mcp

# Or with Docker directly
docker run -i --rm -v $(pwd)/contracts:/contracts:ro farofino-mcp:latest
```

See [DOCKER.md](DOCKER.md) for detailed Docker usage and configuration.

### Without Docker

#### Running the Server

```bash
python3 -m farofino_mcp
```

Or if installed as a package:

```bash
farofino-mcp
```

### Available Tools

#### 1. slither_audit

Run Slither static analysis on a smart contract.

**Parameters:**

- `contract_path` (required): Path to the contract file (.sol or .vy)
- `detectors` (optional): Comma-separated list of specific detectors to run
- `exclude_detectors` (optional): Comma-separated list of detectors to exclude

**Example:** (replace `/path/to/MyContract.sol` with your actual file path)

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

**Example:** (replace `/path/to/MyContract.sol` with your actual file path)

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

**Example:** (replace `/path/to/MyContract.sol` with your actual file path)

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

**Example:** (replace `/path/to/MyContract.sol` with your actual file path)

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

**Example:** (replace `/path/to/MyContract.sol` with your actual file path)

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

### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Option 1: Using Docker (Recommended - All Tools Pre-installed)

```json
{
  "mcpServers": {
    "farofino": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "${PWD}/contracts:/contracts:ro", "farofino-mcp:latest"],
      "cwd": "/path/to/farofino-mcp"
    }
  }
}
```

**Notes:**
- Replace `/path/to/farofino-mcp` with the absolute path to this repository on your host machine so Docker sees the right directory.
- On Windows, replace `${PWD}` with `%CD%`.

### Option 2: Using Docker Compose

```json
{
  "mcpServers": {
    "farofino": {
      "command": "docker-compose",
      "args": ["run", "--rm", "farofino-mcp"],
      "cwd": "/path/to/farofino-mcp"
    }
  }
}
```

**Tip:** Replace `/path/to/farofino-mcp` with the absolute host path so `docker-compose` finds the repo configuration.

### Option 3: Using Python Module (No Docker)

```json
{
  "mcpServers": {
    "farofino": {
      "command": "python3",
      "args": ["-m", "farofino_mcp"],
      "cwd": "/path/to/farofino-mcp"
    }
  }
}
```

**Tip:** Replace the `cwd` placeholder with the absolute directory where you installed `farofino-mcp`.

### Option 4: Using pip Installation (No Docker)

```json
{
  "mcpServers": {
    "farofino": {
      "command": "farofino-mcp"
    }
  }
}
```

For more Docker configuration options, see [DOCKER.md](DOCKER.md).

## Example Workflow

Replace `/path/to/contract.sol` with the actual location of your Solidity file in the steps below.

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
  - Aderyn for Rust-based analysis (pre-installed in the Docker image or via Cyfrinup)
   - Mythril for symbolic execution

## Development

### Building from Source

```bash
git clone https://github.com/italoag/farofino-mcp.git
cd farofino-mcp
pip install -r requirements.txt
pip install -e .
```

### Development Mode

```bash
# Run directly from source
python3 -m farofino_mcp

# With debugging
python3 -u -m farofino_mcp
```

### Project Structure

```
farofino-mcp/
├── farofino_mcp/
│   ├── __init__.py          # Package initialization
│   └── __main__.py          # Main server implementation
├── pyproject.toml           # Python project configuration
├── requirements.txt         # Python dependencies
├── setup.py                 # Setup configuration
├── Dockerfile               # Docker configuration
└── README.md               # This file
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
