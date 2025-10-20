# Docker Build Guide for MCP-scaudit

## Overview

This document explains the Docker setup for the MCP Smart Contract Auditor project, which is a Python-based MCP server that integrates multiple smart contract auditing tools.

## What Changed

### Fixed Issues

1. **Makefile Alignment**: The Makefile was incorrectly referencing Rust and Node.js base images (`rust:1.75-slim`, `node:20-slim`) which were not appropriate for this Python-based project. The Makefile has been updated to use `python:3.12-slim` as the base image.

2. **Docker Compose Syntax**: Updated all `docker-compose` commands to `docker compose` (Docker Compose v2 syntax) which is the current standard.

3. **Aderyn Support**: Added Rust/Cargo installation to the Dockerfile to enable Aderyn (Rust-based Solidity auditor) to be installed alongside the Python-based tools (Slither and Mythril).

### Dockerfile Structure

The Dockerfile now:
- Uses `python:3.12-slim` as the base image (appropriate for Python project)
- Installs Rust/Cargo toolchain for Aderyn compilation
- Installs Slither and Mythril (Python-based audit tools) - **always available**
- Attempts to install Aderyn (Rust-based audit tool) - **may be optional depending on build environment**
- Gracefully handles SSL certificate issues that may prevent Aderyn installation in restricted environments

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

### Always Available (Python-based)

1. **Slither** (`slither-analyzer==0.10.0`)
   - Static analysis framework for Solidity & Vyper
   - Always installed successfully

2. **Mythril** (`mythril==0.24.8`)
   - Symbolic execution analysis for Ethereum smart contracts
   - Always installed successfully

### Optionally Available (Rust-based)

3. **Aderyn**
   - Rust-based static analyzer for Solidity
   - Installed via `cargo install aderyn`
   - May not be available if SSL certificate issues occur during build
   - Can be installed manually later if needed

## Handling Aderyn Installation Issues

### During Build

If you see a warning during build:
```
WARNING: Aderyn installation failed. You can install it manually later with 'cargo install aderyn'
```

This is expected in environments with SSL certificate restrictions (common in CI/CD systems). The Docker image will still be functional with Slither and Mythril.

### Manual Aderyn Installation

If Aderyn is not available in your built image, you can install it manually:

```bash
# Enter the container as root
docker run --rm -it --entrypoint /bin/bash --user root mcp-scaudit:latest

# Inside the container, install Aderyn
cargo install aderyn

# Exit and commit the changes (optional)
exit
```

Alternatively, build in an environment with proper SSL certificates or configure cargo to use a different crate mirror.

## Verification

After building, verify which tools are available:

```bash
make verify
```

Expected output:
```
Testing MCP server startup...
MCP Smart Contract Auditor Server running on stdio

Testing tool availability...
Slither: OK
Mythril: OK

Testing Aderyn (may not be available if cargo install failed)...
Aderyn: OK
# OR
Aderyn: Not available (expected if cargo install failed due to SSL issues)
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
- Build in a different environment with proper certificates
- Install Aderyn manually after the build (see above)
- Use Slither and Mythril only (both are fully functional)

### Image Size

The final image includes:
- Python 3.12 runtime
- Rust/Cargo toolchain (for Aderyn)
- Slither, Mythril, and optionally Aderyn
- MCP server code

Expected size: ~1.5-2GB (depending on whether Aderyn is included)

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
- [Mythril Documentation](https://github.com/ConsenSys/mythril)
- [Aderyn Documentation](https://github.com/Cyfrin/aderyn)
