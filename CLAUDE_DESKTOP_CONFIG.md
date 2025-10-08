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

### Option 1: Using npx (Recommended for local development)

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "npx",
      "args": ["-y", "mcp-scaudit"]
    }
  }
}
```

### Option 2: Using global installation

If you've installed the package globally with `npm install -g mcp-scaudit`:

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "mcp-scaudit"
    }
  }
}
```

### Option 3: Using local repository (for development)

If you're developing or testing locally:

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "node",
      "args": ["/path/to/mcp-scaudit/dist/index.js"]
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
      "command": "npx",
      "args": ["-y", "mcp-scaudit"]
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
