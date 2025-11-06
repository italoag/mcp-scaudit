# Quick Start Guide

Get started with the MCP Smart Contract Auditor in minutes!

## Installation

### Option 1: Using Docker (Recommended - All Tools Pre-installed)

**Fastest way to get started with all audit tools!**

```bash
# Clone and build
git clone https://github.com/italoag/farofino-mcp.git
cd farofino-mcp
docker-compose build
```

Configure Claude Desktop:

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

Swap `/path/to/farofino-mcp` for the absolute path to the repository on your machine so `docker-compose` can find the project files.

**Benefits:** Slither and Aderyn pre-installed | No dependency issues | Works everywhere

See [DOCKER.md](DOCKER.md) for detailed Docker setup.

### Option 2: Using npx (No Docker)

No installation needed! Just configure Claude Desktop:

```json
{
  "mcpServers": {
    "farofino": {
      "command": "npx",
      "args": ["-y", "farofino-mcp"]
    }
  }
}
```

**Note:** External tools (Slither, Aderyn) must be installed separately.

### Option 3: Global Installation

```bash
npm install -g farofino-mcp
```

Then configure Claude Desktop:

```json
{
  "mcpServers": {
    "farofino": {
      "command": "farofino-mcp"
    }
  }
}
```

## First Steps

### 1. Check Available Tools

Ask Claude:
> "What audit tools are available?"

This will run the `check_tools` function and show which tools are installed.

**With Docker:** Slither and Aderyn will be available ✅  
**Without Docker:** Only pattern_analysis available unless you install tools separately

### 2. Run Pattern Analysis (No Additional Tools Needed)

Ask Claude:
> "Can you analyze this contract for security issues?"

Then paste your Solidity contract code. Claude will use the `pattern_analysis` tool which works out of the box.

### 3. Install Additional Tools (Optional - Skip if Using Docker)

**If you're using Docker, all tools are pre-installed! Skip this section.**

For non-Docker setup, install these tools for comprehensive analysis:

**Slither** (Python-based, highly recommended):

```bash
pip install slither-analyzer
```

**Aderyn** (Rust-based via Cyfrinup):

```bash
curl -LsSf https://raw.githubusercontent.com/Cyfrin/up/main/install | bash
CYFRINUP_ONLY_INSTALL=aderyn cyfrinup
```

## Example Usage

### With Docker - Place Contracts in ./contracts/

```bash
# Create contracts directory
mkdir -p contracts
cp YourContract.sol contracts/

# Claude will access files at /contracts/YourContract.sol
```

Then ask Claude:
> "Run a security audit on /contracts/MyContract.sol using all available tools"

### Without Docker - Use Full Paths
>
> "Run a security audit on /path/to/MyContract.sol using all available tools"

Replace `/path/to/MyContract.sol` with the real file path on your host system.

Claude will:

1. Check which tools are available
2. Read the contract
3. Run pattern analysis
4. Run Slither (if installed)
5. Run Aderyn (if installed)
6. Summarize findings

### Quick Pattern Check
>
> "Check this contract for common vulnerabilities"
>
> ```solidity
> // paste your contract code
> ```

### Compare Tool Results
>
> "Run both Slither and pattern analysis on my contract and compare the results"

## Common Patterns Detected

The built-in pattern analysis (no external tools needed) checks for:

- Reentrancy vulnerabilities
- tx.origin authentication
- selfdestruct usage
- delegatecall risks
- block.timestamp manipulation
- Missing overflow protection (pre-Solidity 0.8)

## Tips

1. **Start with pattern_analysis** - it requires no additional tools
2. **Install Slither first** - it's the most comprehensive and widely used
3. **Use multiple tools** - different tools catch different issues (pattern analysis, Slither, Aderyn)
4. **Review findings manually** - automated tools may have false positives
5. **Keep tools updated** - `pip install --upgrade slither-analyzer`

## Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Getting Help

- Check the [../README.md](../README.md) for detailed documentation
- See [../CONTRIBUTING.md](../CONTRIBUTING.md) for development info
- View [CLAUDE_DESKTOP_CONFIG.md](CLAUDE_DESKTOP_CONFIG.md) for configuration details
- Open an issue on GitHub for bugs or questions

## Example Workflow

1. **Initial Setup** (one time):

   ```bash
   pip install slither-analyzer  # Install tools
   ```

2. **Configure Claude Desktop** (one time):
   Edit config file, add farofino server, restart Claude

3. **Use with Claude**:
   > "Hey Claude, can you audit this smart contract for me?"
>
   > ```solidity
   > // Your contract code here
   > ```

That's it! You're ready to audit smart contracts with Claude and the MCP Smart Contract Auditor.
