# Docker Setup for MCP Smart Contract Auditor

This document explains how to use the MCP Smart Contract Auditor with Docker, providing a pre-configured environment with audit tools (Slither and Aderyn) installed.

## Overview

The Docker container provides:

- ✅ **Slither** Python-based static analyzer
- ✅ **Aderyn** (latest via Cyfrinup) - Rust-based static analyzer
- ✅ **Python 3.12 runtime** - Base environment
- ✅ **MCP Server** - Pre-built and ready to use

**Note**: The build process includes workarounds for SSL certificate issues in certain environments. If you encounter SSL errors, the build should handle them automatically using --trusted-host flags and SSL verification bypasses.

## Quick Start

### Using Docker Compose (Recommended)

1. **Build the container:**

   ```bash
   docker-compose build
   ```

   **Build time**: Approximately 5-10 minutes depending on network speed.

   **If you encounter SSL certificate errors**, the Dockerfile includes automatic workarounds:
   - GPG signature verification bypass for apt-get
   - Trusted host configuration for pip
   - SSL verification disable for npm

   These are necessary for some CI/CD environments with proxy or certificate chain issues.

2. **Run the MCP server:**

   ```bash
   docker-compose run --rm farofino-mcp
   ```

3. **Audit a contract:**

   ```bash
   # Place your contracts in ./contracts directory
   mkdir -p contracts
   cp YourContract.sol contracts/
   
   # Run audit
   docker-compose run --rm farofino-mcp
   ```

### Using Makefile (Recommended for Development)

The repository includes a Makefile for easier management:

```bash
# Show all available commands
make help

# Build with automatic retry on network issues
make build-retry

# Build without cache
make build-no-cache

# Verify installation
make verify

# Run the server
make run
```

### Using Docker Directly

1. **Build the image:**

   ```bash
   docker build -t farofino-mcp:latest .
   ```

2. **Run the container:**

   ```bash
   docker run -i farofino-mcp:latest
   ```

3. **With contract volume mount:**

   ```bash
   docker run -i -v $(pwd)/contracts:/contracts:ro farofino-mcp:latest
   ```

## Configuration for Claude Desktop

### Option 1: Using Docker with stdin/stdout

Add to your Claude Desktop configuration:

**macOS/Linux:**

```json
{
  "mcpServers": {
    "farofino": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "${PWD}/contracts:/contracts:ro", "farofino-mcp:latest"]
    }
  }
}
```

Replace `${PWD}` with the absolute path to your repository if Claude Desktop does not expand it automatically.

**Windows:**

```json
{
  "mcpServers": {
    "farofino": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "%CD%/contracts:/contracts:ro", "farofino-mcp:latest"]
    }
  }
}
```

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

Make sure `/path/to/farofino-mcp` is the actual host path where this repository lives so `docker-compose` can find `docker-compose.yml`.

## Volume Mounts

### Contracts Directory

Mount your contracts for analysis:

```bash
docker run -i -v /path/to/contracts:/contracts:ro farofino-mcp:latest
```

Swap `/path/to/contracts` for the real directory on your host that contains the Solidity files you want to audit.

Then in your MCP calls, use `/contracts/YourContract.sol` as the path.

### Configuration Directory (Optional)

```bash
docker run -i -v /path/to/config:/config:ro farofino-mcp:latest
```

Replace `/path/to/config` with the full host path to your configuration files.

## Building the Image

### Standard Build

```bash
docker build -t farofino-mcp:latest .
```

### Build with specific versions

```bash
docker build \
  --build-arg SLITHER_VERSION=0.10.0 \
  -t farofino-mcp:custom .
```

### Multi-platform Build

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t farofino-mcp:latest \
  --push .
```

## Verifying Installation

**Note**: The build includes workarounds for SSL issues and may emit benign warnings from third-party dependencies.

### Check that the MCP server starts

```bash
docker run --rm farofino-mcp:latest sh -c "timeout 2 python3 -m farofino_mcp" 2>&1 | head -5
```

You should see: `MCP Smart Contract Auditor Server running on stdio`

### Test Slither availability

```bash
docker run --rm --entrypoint python3 farofino-mcp:latest -c "import slither; print('Slither: OK')"
```

### Test Aderyn availability

```bash
docker run --rm --entrypoint sh farofino-mcp:latest -c "aderyn --version"
```

## Development Mode

For development with hot reload:

```bash
docker-compose --profile dev up farofino-mcp-dev
```

This mounts your source code and watches for changes.

## Container Size Optimization

The container is optimized for size:

- Single-stage build with Cyfrinup-managed tooling
- Slim base image (python:3.12-slim)
- Separate installation of Python packages to speed up builds
- Build artifacts cached efficiently
- Cleaned package manager caches

Expected image size: ~1.3-1.4GB (including Slither, Aderyn, and Python runtime)

## Troubleshooting

### Container fails to start

```bash
# Check logs
docker-compose logs farofino-mcp

# Verify health check
docker inspect farofino-mcp --format='{{.State.Health.Status}}'
```

### Tools not found

```bash
# Rebuild without cache
docker-compose build --no-cache

# Verify tools in container
docker run --rm farofino-mcp:latest sh -c "which slither && which aderyn"
```

### Permission issues with mounted volumes

```bash
# Use proper permissions
chmod -R 755 contracts/

# Or run as current user
docker run -i --user $(id -u):$(id -g) -v $(pwd)/contracts:/contracts:ro farofino-mcp:latest
```

### Out of memory during build

```bash
# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory

# Or build with resource limits
docker build --memory=4g -t farofino-mcp:latest .
```

### Network timeout when pulling images

If you encounter timeout errors like `failed to resolve source metadata` or `dial tcp ... i/o timeout`:

```bash
# Solution 1: Increase Docker daemon timeout
# Add to Docker daemon.json (Linux: /etc/docker/daemon.json, Mac/Windows: Docker Desktop Settings -> Docker Engine)
{
  "max-concurrent-downloads": 3,
  "max-concurrent-uploads": 5,
  "registry-mirrors": []
}

# Solution 2: Use BuildKit with host network (better for CI/CD)
DOCKER_BUILDKIT=1 docker build --network=host -t farofino-mcp:latest .

# Solution 3: Pull base images first (manual retry)
docker pull python:3.12-slim
docker-compose build

# Solution 4: Use docker-compose with increased timeout
COMPOSE_HTTP_TIMEOUT=300 docker-compose build

# Solution 5: If behind a corporate proxy
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1
docker-compose build

# Solution 6: Use an alternative registry mirror (for China/restricted regions)
# Edit daemon.json to add registry mirrors:
{
  "registry-mirrors": ["https://mirror.gcr.io"]
}
# Then restart Docker daemon and retry build
```

**For CI/CD environments:**

```bash
# GitHub Actions - add retry logic
- name: Build Docker image
  run: |
    for i in {1..3}; do
      docker-compose build && break || sleep 15
    done

# Or use Docker Layer Caching action
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2
  
- name: Build and cache
  uses: docker/build-push-action@v4
  with:
    context: .
    file: ./Dockerfile
    cache-from: type=gha
    cache-to: type=gha,mode=max
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
    docker build -t farofino-mcp:latest .
    docker run -i -v ${{ github.workspace }}/contracts:/contracts:ro farofino-mcp:latest
```

### GitLab CI Example

```yaml
audit:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t farofino-mcp:latest .
    - docker run -i -v $(pwd)/contracts:/contracts:ro farofino-mcp:latest
```

## Publishing to Registry

### Docker Hub

```bash
docker tag farofino-mcp:latest yourusername/farofino-mcp:latest
docker push yourusername/farofino-mcp:latest
```

### GitHub Container Registry

```bash
docker tag farofino-mcp:latest ghcr.io/yourusername/farofino-mcp:latest
docker push ghcr.io/yourusername/farofino-mcp:latest
```

## Additional Resources

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MCP Protocol Specification](https://github.com/modelcontextprotocol/specification)

## Support

For issues related to:

- **Docker setup**: Check this document and Docker logs
- **MCP server**: See main [README.md](README.md)
- **Audit tools**: Refer to tool-specific documentation (Slither, Aderyn)
