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

### Option 1: Using Docker (Recommended - All Tools Pre-installed) 🐳

**Best option for having all audit tools (Slither, Aderyn, Mythril) pre-installed:**

> Replace `/absolute/path/to/farofino-mcp` with the full path to this repository on **your host machine** (for example, `/Users/YourUser/projects/farofino-mcp`). Claude invokes the command from the host before Docker starts, so the path must exist locally, not inside the container.

```json
{
  "mcpServers": {
    "farofino": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "${PWD}/contracts:/contracts:ro", "farofino-mcp:latest"],
      "cwd": "/absolute/path/to/farofino-mcp"
    }
  }
}
```

**Note for Windows users:** Replace `${PWD}` with `%CD%`, and update the `cwd` value to the absolute Windows path to the repository (for example, `C:\Users\YourUser\Projects\farofino-mcp`).

```json
{
  "mcpServers": {
    "farofino": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "%CD%/contracts:/contracts:ro", "farofino-mcp:latest"],
      "cwd": "C:\\path\\to\\farofino-mcp"
    }
  }
}
```

### Option 2: Using Docker Compose (Recommended Alternative)

```json
{
  "mcpServers": {
    "farofino": {
      "command": "docker-compose",
      "args": ["run", "--rm", "farofino-mcp"],
      "cwd": "/absolute/path/to/farofino-mcp"
    }
  }
}
```

> The `cwd` entry always points to the directory on your computer that contains `docker-compose.yml`. Claude uses it so `docker-compose` can locate the configuration file.

**Benefits:**

- ✅ All tools pre-installed (Slither, Aderyn, Mythril)
- ✅ No dependency conflicts
- ✅ Consistent environment
- ✅ Easy updates with `docker-compose pull`

See [DOCKER.md](DOCKER.md) for detailed Docker setup.

### Option 3: Using npx (No Docker - Tools Need Manual Installation)

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

### Option 4: Using global installation

If you've installed the package globally with `npm install -g farofino-mcp`:

```json
{
  "mcpServers": {
    "farofino": {
      "command": "farofino-mcp"
    }
  }
}
```

### Option 5: Using local repository (for development)

If you're developing or testing locally:

```json
{
  "mcpServers": {
    "farofino": {
      "command": "node",
      "args": ["/path/to/farofino-mcp/dist/index.js"]
    }
  }
}
```

Point `/path/to/farofino-mcp/dist/index.js` to the actual build output on your machine.

## Multiple Servers Configuration

You can have multiple MCP servers configured at once:

```json
{
  "mcpServers": {
    "farofino": {
      "command": "npx",
      "args": ["-y", "farofino-mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/contracts"]
    }
  }
}
```

Replace `/path/to/contracts` with the directory you want Claude to access from your host.

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

Update the `/path/to/...` placeholders with the actual contract locations on your system.

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
- Aderyn: `curl -LsSf https://raw.githubusercontent.com/Cyfrin/up/main/install | bash && CYFRINUP_ONLY_INSTALL=aderyn cyfrinup`
- Mythril: `pip install mythril`

3. Ensure tools are in your system PATH

### Permission issues

- Ensure the contract files are readable by the user running Claude Desktop
- On Unix systems, you may need to make the script executable
