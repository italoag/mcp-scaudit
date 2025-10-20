# Python Migration Guide

## Overview

The MCP Smart Contract Auditor has been rewritten from TypeScript/Node.js to Python. This document explains the migration and key changes.

## Why Python?

- **Native integration** with audit tools (Slither, Mythril) which are Python-based
- **Simpler dependency management** for security analysis tools
- **Better ecosystem alignment** with smart contract security tooling
- **Improved maintainability** with Python's clarity and simplicity

## Key Changes

### 1. Language and Runtime

**Before (TypeScript/Node.js):**
```bash
npm install
npm run build
node dist/index.js
```

**After (Python):**
```bash
pip install -r requirements.txt
python3 -m mcp_scaudit
```

### 2. Package Structure

**Before:**
```
src/
├── index.ts
package.json
tsconfig.json
```

**After:**
```
mcp_scaudit/
├── __init__.py
├── __main__.py
requirements.txt
pyproject.toml
setup.py
```

### 3. Configuration

**Claude Desktop Configuration Before:**
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

**Claude Desktop Configuration After:**
```json
{
  "mcpServers": {
    "scaudit": {
      "command": "python3",
      "args": ["-m", "mcp_scaudit"],
      "cwd": "/path/to/mcp-scaudit"
    }
  }
}
```

Or with pip installation:
```json
{
  "mcpServers": {
    "scaudit": {
      "command": "mcp-scaudit"
    }
  }
}
```

### 4. Docker

**Dockerfile Changes:**
- Base image changed from `node:20-slim` to `python:3.12-slim`
- Python dependencies installed via pip instead of npm
- Entry point changed to `python3 -m mcp_scaudit`

**Docker Compose:**
```bash
# Build and run remains the same
docker-compose build
docker-compose run --rm mcp-scaudit
```

### 5. CI/CD Pipeline

New GitHub Actions workflow (`.github/workflows/release.yml`) includes:

- **Semantic versioning**: Automatically determines version based on commit messages
  - Breaking changes (e.g., `feat!:`, `BREAKING CHANGE:`) → Major version bump
  - New features (`feat:`) → Minor version bump
  - Fixes and other changes → Patch version bump

- **Python package building**: Creates distributable packages (`.tar.gz`, `.whl`)

- **Docker image publishing**: Publishes to GitHub Container Registry
  - Tagged with version number and `latest`
  - Example: `ghcr.io/italoag/mcp-scaudit:0.1.0`

- **GitHub releases**: Automatically creates releases with changelog

## Installation Methods

### 1. From Source

```bash
git clone https://github.com/italoag/mcp-scaudit.git
cd mcp-scaudit
pip install -r requirements.txt
python3 -m mcp_scaudit
```

### 2. With pip (when published)

```bash
pip install mcp-scaudit
mcp-scaudit
```

### 3. With Docker

```bash
docker pull ghcr.io/italoag/mcp-scaudit:latest
docker run -i --rm ghcr.io/italoag/mcp-scaudit:latest
```

## Functionality

All original functionality has been preserved:

- ✅ `slither_audit` - Static analysis with Slither
- ✅ `aderyn_audit` - Rust-based analysis with Aderyn
- ✅ `mythril_audit` - Symbolic execution with Mythril
- ✅ `pattern_analysis` - Basic pattern-based security checks
- ✅ `read_contract` - Read contract source code
- ✅ `check_tools` - Check available audit tools

## Development

### Running Tests

```bash
python3 -m pytest
```

### Code Formatting

```bash
pip install black
black mcp_scaudit/
```

### Type Checking

```bash
pip install mypy
mypy mcp_scaudit/
```

## Migration Notes

### For Users

If you were using the TypeScript version:

1. Remove Node.js dependencies: `rm -rf node_modules package-lock.json`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Update Claude Desktop config (see Configuration section above)
4. Run: `python3 -m mcp_scaudit`

### For Contributors

1. Python 3.8+ is required
2. Follow PEP 8 style guidelines
3. Use type hints where appropriate
4. Add docstrings to functions and classes
5. Test with multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)

## Troubleshooting

### Issue: Module not found error

**Solution:** Ensure you're in the project root and run:
```bash
python3 -m mcp_scaudit
```

### Issue: MCP SDK not found

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Audit tools not found

**Solution:** Install audit tools separately:
```bash
pip install slither-analyzer mythril
cargo install aderyn  # Optional
```

## Future Enhancements

- [ ] Publish to PyPI
- [ ] Add comprehensive test suite
- [ ] Add support for more audit tools
- [ ] Improve error handling and logging
- [ ] Add configuration file support

## Support

For issues or questions about the Python migration, please:

1. Check this document first
2. Review the [README.md](README.md)
3. Open an issue on GitHub: https://github.com/italoag/mcp-scaudit/issues
