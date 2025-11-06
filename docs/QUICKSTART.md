# Quick Start Guide

Get started with the MCP Smart Contract Auditor in minutes!

## Installation

### Option 1: Using Docker (Recommended - All Tools Pre-installed) 🐳

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
    "scaudit": {
      "command": "docker-compose",
      "args": ["run", "--rm", "farofino-mcp"],
      "cwd": "/path/to/farofino-mcp"
    }
  }
}
```

**Benefits:** ✅ Slither and Mythril pre-installed | ✅ No dependency issues | ✅ Works everywhere

**Note:** Aderyn is not pre-installed in Docker due to build environment issues, but Slither and Mythril provide comprehensive coverage.

See [DOCKER.md](DOCKER.md) for detailed Docker setup.

### Option 2: Using npx (No Docker)
No installation needed! Just configure Claude Desktop:

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "npx",
      "args": ["-y", "farofino-mcp"]
    }
  }
}
```

**Note:** External tools (Slither, Aderyn, Mythril) must be installed separately.

### Option 3: Global Installation
```bash
npm install -g farofino-mcp
```

Then configure Claude Desktop:
```json
{
  "mcpServers": {
    "scaudit": {
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

**With Docker:** Slither and Mythril will be available (Aderyn not pre-installed) ✅  
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

**Aderyn** (Rust-based):
```bash
cargo install aderyn
```

**Mythril** (Symbolic execution):
```bash
pip install mythril
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
> "Run a security audit on /path/to/MyContract.sol using all available tools"

Claude will:
1. Check which tools are available
2. Read the contract
3. Run pattern analysis
4. Run Slither (if installed)
5. Run Aderyn (if installed)
6. Run Mythril (if installed)
7. Summarize findings

### Quick Pattern Check
> "Check this contract for common vulnerabilities"
> ```solidity
> // paste your contract code
> ```

### Compare Tool Results
> "Run both Slither and pattern analysis on my contract and compare the results"

## Common Patterns Detected

The built-in pattern analysis (no external tools needed) checks for:

- ✅ Reentrancy vulnerabilities
- ✅ tx.origin authentication
- ✅ selfdestruct usage
- ✅ delegatecall risks
- ✅ block.timestamp manipulation
- ✅ Missing overflow protection (pre-Solidity 0.8)

## Tips

1. **Start with pattern_analysis** - it requires no additional tools
2. **Install Slither first** - it's the most comprehensive and widely used
3. **Use multiple tools** - different tools catch different issues
4. **Review findings manually** - automated tools may have false positives
5. **Keep tools updated** - `pip install --upgrade slither-analyzer`

## Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Getting Help

- Check the [README](README.md) for detailed documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development info
- View [CLAUDE_DESKTOP_CONFIG.md](CLAUDE_DESKTOP_CONFIG.md) for configuration details
- Open an issue on GitHub for bugs or questions

## Example Workflow

1. **Initial Setup** (one time):
   ```bash
   pip install slither-analyzer  # Install tools
   ```

2. **Configure Claude Desktop** (one time):
   Edit config file, add scaudit server, restart Claude

3. **Use with Claude**:
   > "Hey Claude, can you audit this smart contract for me?"
   > ```solidity
   > // Your contract code here
   > ```

That's it! You're ready to audit smart contracts with Claude and the MCP Smart Contract Auditor.
