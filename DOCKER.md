# Docker Setup for MCP Smart Contract Auditor

This document explains how to use the MCP Smart Contract Auditor with Docker, providing a pre-configured environment with all audit tools (Slither, Aderyn, and Mythril) installed.

## Overview

The Docker container provides:
- ✅ **Slither** (v0.10.0) - Python-based static analyzer
- ✅ **Aderyn** (latest) - Rust-based static analyzer
- ✅ **Mythril** (v0.24.8) - Symbolic execution analyzer
- ✅ **Node.js 20** - Runtime environment
- ✅ **MCP Server** - Pre-built and ready to use

## Quick Start

### Using Docker Compose (Recommended)

1. **Build the container:**
   ```bash
   docker-compose build
   ```

2. **Run the MCP server:**
   ```bash
   docker-compose run --rm mcp-scaudit
   ```

3. **Audit a contract:**
   ```bash
   # Place your contracts in ./contracts directory
   mkdir -p contracts
   cp YourContract.sol contracts/
   
   # Run audit
   docker-compose run --rm mcp-scaudit
   ```

### Using Docker Directly

1. **Build the image:**
   ```bash
   docker build -t mcp-scaudit:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -i mcp-scaudit:latest
   ```

3. **With contract volume mount:**
   ```bash
   docker run -i -v $(pwd)/contracts:/contracts:ro mcp-scaudit:latest
   ```

## Configuration for Claude Desktop

### Option 1: Using Docker with stdin/stdout

Add to your Claude Desktop configuration:

**macOS/Linux:**
```json
{
  "mcpServers": {
    "scaudit": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "${PWD}/contracts:/contracts:ro", "mcp-scaudit:latest"]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "scaudit": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "%CD%/contracts:/contracts:ro", "mcp-scaudit:latest"]
    }
  }
}
```

### Option 2: Using Docker Compose

```json
{
  "mcpServers": {
    "scaudit": {
      "command": "docker-compose",
      "args": ["run", "--rm", "mcp-scaudit"],
      "cwd": "/path/to/mcp-scaudit"
    }
  }
}
```

## Volume Mounts

### Contracts Directory
Mount your contracts for analysis:
```bash
docker run -i -v /path/to/contracts:/contracts:ro mcp-scaudit:latest
```

Then in your MCP calls, use `/contracts/YourContract.sol` as the path.

### Configuration Directory (Optional)
```bash
docker run -i -v /path/to/config:/config:ro mcp-scaudit:latest
```

## Building the Image

### Standard Build
```bash
docker build -t mcp-scaudit:latest .
```

### Build with specific versions
```bash
docker build \
  --build-arg SLITHER_VERSION=0.10.0 \
  --build-arg MYTHRIL_VERSION=0.24.8 \
  -t mcp-scaudit:custom .
```

### Multi-platform Build
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t mcp-scaudit:latest \
  --push .
```

## Verifying Installation

### Check tool versions:
```bash
docker run --rm mcp-scaudit:latest sh -c "slither --version && aderyn --version && myth version"
```

### Run health check:
```bash
docker run --rm mcp-scaudit:latest node -e "
const {execSync} = require('child_process');
console.log('Slither:', execSync('slither --version').toString());
console.log('Aderyn:', execSync('aderyn --version').toString());
console.log('Mythril:', execSync('myth version').toString());
"
```

## Development Mode

For development with hot reload:

```bash
docker-compose --profile dev up mcp-scaudit-dev
```

This mounts your source code and watches for changes.

## Container Size Optimization

The container is optimized for size:
- Multi-stage build to exclude Rust compiler
- Slim base images (node:20-slim)
- Only production dependencies
- Build artifacts cached efficiently
- Cleaned package manager caches

Expected image size: ~800MB-1GB (including all tools)

## Troubleshooting

### Container fails to start
```bash
# Check logs
docker-compose logs mcp-scaudit

# Verify health check
docker inspect mcp-scaudit --format='{{.State.Health.Status}}'
```

### Tools not found
```bash
# Rebuild without cache
docker-compose build --no-cache

# Verify tools in container
docker run --rm mcp-scaudit:latest sh -c "which slither && which aderyn && which myth"
```

### Permission issues with mounted volumes
```bash
# Use proper permissions
chmod -R 755 contracts/

# Or run as current user
docker run -i --user $(id -u):$(id -g) -v $(pwd)/contracts:/contracts:ro mcp-scaudit:latest
```

### Out of memory during build
```bash
# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory

# Or build with resource limits
docker build --memory=4g -t mcp-scaudit:latest .
```

## Security Considerations

1. **Read-only volumes**: Contracts are mounted as read-only (`:ro`) by default
2. **Non-root user**: Container runs as user `mcp` (UID 1000)
3. **No privileged access**: Container doesn't require elevated permissions
4. **Network isolation**: No exposed ports by default

## Performance Tips

1. **Use volume mounts** instead of copying files into the container
2. **Keep contracts organized** in a dedicated directory
3. **Use .dockerignore** to exclude unnecessary files
4. **Cache layers** by keeping package.json changes minimal

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run MCP Audit
  run: |
    docker build -t mcp-scaudit:latest .
    docker run -i -v ${{ github.workspace }}/contracts:/contracts:ro mcp-scaudit:latest
```

### GitLab CI Example
```yaml
audit:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t mcp-scaudit:latest .
    - docker run -i -v $(pwd)/contracts:/contracts:ro mcp-scaudit:latest
```

## Publishing to Registry

### Docker Hub
```bash
docker tag mcp-scaudit:latest yourusername/mcp-scaudit:latest
docker push yourusername/mcp-scaudit:latest
```

### GitHub Container Registry
```bash
docker tag mcp-scaudit:latest ghcr.io/yourusername/mcp-scaudit:latest
docker push ghcr.io/yourusername/mcp-scaudit:latest
```

## Additional Resources

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MCP Protocol Specification](https://github.com/modelcontextprotocol/specification)

## Support

For issues related to:
- **Docker setup**: Check this document and Docker logs
- **MCP server**: See main [README.md](README.md)
- **Audit tools**: Refer to tool-specific documentation (Slither, Aderyn, Mythril)
