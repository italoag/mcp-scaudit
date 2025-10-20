# Claude Desktop Configuration Example

This file shows how to configure the MCP Smart Contract Auditor for use with Claude Desktop.

## Configuration File Location

### macOS
`~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
`%APPDATA%/Claude/claude_desktop_config.json`

### Linux
`~/.config/Claude/claude_desktop_config.json`

## Configuration Options

### Option 1: Using Docker (Recommended - All Tools Pre-installed)

**Best option for having all audit tools (Slither, Aderyn, Mythril) pre-installed:**

Replace `/absolute/path/to/mcp-scaudit` with the actual absolute path where you cloned this repository.

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "${PWD}/contracts:/contracts:ro", "mcp-scaudit:latest"],
      "cwd": "/absolute/path/to/mcp-scaudit"
    }
  }
}
```

**Note for Windows users:** Replace `${PWD}` with `%CD%` and use Windows-style paths:
```json
{
  "mcpServers": {
    "scaudit": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "%CD%/contracts:/contracts:ro", "mcp-scaudit:latest"],
      "cwd": "C:\\absolute\\path\\to\\mcp-scaudit"
    }
  }
}
```

### Option 2: Using Docker Compose (Recommended Alternative)

Replace `/absolute/path/to/mcp-scaudit` with the actual absolute path where you cloned this repository.

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "docker-compose",
      "args": ["run", "--rm", "mcp-scaudit"],
      "cwd": "/absolute/path/to/mcp-scaudit"
    }
  }
}
```

**Benefits:**
- All tools pre-installed (Slither, Aderyn, Mythril)
- No dependency conflicts
- Consistent environment
- Easy updates with `docker-compose pull`

See [DOCKER.md](DOCKER.md) for detailed Docker setup.

### Option 3: Using Python Module (No Docker - Tools Need Manual Installation)

Replace `/absolute/path/to/mcp-scaudit` with the actual absolute path where you cloned this repository.

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "python3",
      "args": ["-m", "mcp_scaudit"],
      "cwd": "/absolute/path/to/mcp-scaudit"
    }
  }
}
```

### Option 4: Using pip Installation (No Docker)

If you've installed the package globally with `pip install mcp-scaudit`:

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "mcp-scaudit"
    }
  }
}
```

### Option 5: Using local repository (for development)

If you're developing or testing locally, replace `/absolute/path/to/mcp-scaudit` with the actual absolute path:

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "python3",
      "args": ["-m", "mcp_scaudit"],
      "cwd": "/absolute/path/to/mcp-scaudit"
    }
  }
}
```

## Multiple Servers Configuration

You can have multiple MCP servers configured at once:

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "python3",
      "args": ["-m", "mcp_scaudit"],
      "cwd": "/absolute/path/to/mcp-scaudit"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/contracts"]
    }
  }
}
```

## After Configuration

1. Save the configuration file
2. Restart Claude Desktop
3. The server tools should now be available in Claude
4. You can verify by asking Claude to "check which audit tools are available" - it will use the `check_tools` function

## Example Prompts

Once configured, you can ask Claude:

- "Can you audit this smart contract for security issues?" (and provide the contract code)
- "Run Slither analysis on /path/to/MyContract.sol"
- "What audit tools are available on this system?"
- "Analyze this contract for common vulnerability patterns"
- "Read and explain the contract at /path/to/contract.sol"

## Troubleshooting

### Server not appearing in Claude

1. Check that the configuration file is in the correct location
2. Verify the JSON syntax is valid (use a JSON validator)
3. Restart Claude Desktop completely
4. Check Claude's logs for any error messages

### Tools not found errors

1. Use the `check_tools` function to see which tools are installed
2. Install missing tools:
   - Slither: `pip install slither-analyzer`
   - Aderyn: `cargo install aderyn`
   - Mythril: `pip install mythril`
3. Ensure tools are in your system PATH

### Permission issues

- Ensure the contract files are readable by the user running Claude Desktop
- On Unix systems, you may need to make the script executable
