# Docker Build Guide for farofino-mcp

## Overview

This document explains the Docker setup for the MCP Smart Contract Auditor project, which is a Python-based MCP server that integrates multiple smart contract auditing tools.

## What Changed

### Fixed Issues

1. **Makefile Alignment**: The Makefile was incorrectly referencing Rust and Node.js base images (`rust:1.75-slim`, `node:20-slim`) which were not appropriate for this Python-based project. The Makefile has been updated to use `python:3.12-slim` as the base image.

2. **Docker Compose Syntax**: Updated all `docker-compose` commands to `docker compose` (Docker Compose v2 syntax) which is the current standard.

3. **Aderyn Support**: Integrated the Cyfrinup installer into the Dockerfile so Aderyn (Rust-based Solidity auditor) ships with the image alongside Slither.

### Dockerfile Structure

The Dockerfile now:

- Uses `python:3.12-slim` as the base image (appropriate for Python project)
- Installs build essentials required by Python tooling
- Installs Slither (Python-based audit tool) - **always available**
- Installs Aderyn (Rust-based audit tool) via Cyfrinup and validates the binary - **always available**
- Gracefully handles SSL certificate issues that may affect downloads by forcing modern TLS settings

## Build Instructions

### Prerequisites

- Docker installed (with Docker Compose v2)
- Internet connection for downloading dependencies

### Quick Start

```bash
# Pull base images (helps with network issues)
make pull-images

# Build the Docker image
make build

# Verify all tools are installed
make verify

# Run the MCP server
make run
```

### Alternative Build Methods

```bash
# Build without cache (clean build)
make build-no-cache

# Build with pre-pulled images (better for network issues)
make build-retry

# Build using host network (useful for CI/CD)
make build-host-network
```

### Makefile Targets

| Target | Description |
|--------|-------------|
| `help` | Show all available targets |
| `pull-images` | Pull Python base image |
| `build` | Build the Docker image using docker compose |
| `build-no-cache` | Build without using cache |
| `build-retry` | Build with pre-pulled images |
| `build-host-network` | Build using host network |
| `run` | Run the MCP server |
| `dev` | Run in development mode |
| `verify` | Verify all tools are installed correctly |
| `test` | Run health checks for all tools |
| `clean` | Remove built images and containers |
| `logs` | Show container logs |
| `size` | Show image size |

## Included Tools

### Always Available Tools

1. **Slither** (`slither-analyzer`)
   - Static analysis framework for Solidity & Vyper
   - Installed via pip with trusted-host flags for reliability

2. **Aderyn** (latest release via [Cyfrinup](https://github.com/Cyfrin/up))
   - Rust-based static analyzer for Solidity
   - Downloaded as a prebuilt binary through Cyfrinup during the Docker build
   - Version is validated via `aderyn --version` in the build pipeline

## Cyfrinup Considerations

Cyfrinup downloads prebuilt binaries directly from the Cyfrin release repositories. Ensure that outbound HTTPS traffic to `githubusercontent.com` is allowed during the Docker build. If your environment performs SSL interception, add the appropriate CA certificates to the base image or execute the build behind a trusted proxy. Should the download fail, rerun `make build` after restoring connectivity; the build will stop with an explicit error when Aderyn cannot be provisioned.

## Verification

After building, verify which tools are available:

```bash
make verify
```

Expected output:

```log
Testing MCP server startup...
MCP Smart Contract Auditor Server running on stdio

Testing tool availability...
Slither: OK

Testing Aderyn...
Aderyn: OK
```

You can also use the MCP server's `check_tools` command to see which tools are available at runtime.

## Troubleshooting

### Build Timeouts

If you experience network timeouts during build:

1. Use `make build-retry` which pre-pulls base images
2. Try building with host network: `make build-host-network`
3. Increase Docker build timeout in your Docker settings
4. Consider using a local mirror for PyPI and crates.io

### SSL Certificate Issues

SSL certificate issues typically occur in:

- Corporate networks with SSL inspection
- CI/CD environments with self-signed certificates
- Restricted build environments

Solutions:

- Build in an environment with trusted certificates or with TLS inspection support configured
- Inject the required certificate authorities into the base image so curl/Cyfrinup trusts your corporate proxy
- Re-run `make build` after connectivity is restored so Cyfrinup can download the Aderyn binary

### Image Size

The final image includes:

- Python 3.12 runtime
- Cyfrinup-managed security tooling (Aderyn binary)
- Slither and Aderyn
- MCP server code

Expected size: ~1.5-2GB

To check your image size:

```bash
make size
```

## Development Mode

For development with hot-reload:

```bash
make dev
```

This mounts your local code directory into the container, allowing you to make changes without rebuilding.

## Clean Up

To remove all built images and containers:

```bash
make clean
```

## Additional Resources

- [MCP Protocol Documentation](https://github.com/anthropics/mcp)
- [Slither Documentation](https://github.com/crytic/slither)
- [Aderyn Documentation](https://github.com/Cyfrin/aderyn)
