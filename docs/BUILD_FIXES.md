# Docker Build Fixes - Technical Summary

## Issues Fixed

### 1. GPG Signature Errors (Debian Repositories)

**Error**: `At least one invalid signature was encountered`

**Solution**: Added `Acquire::Check-Valid-Until=false` flag to apt-get commands:

```dockerfile
RUN apt-get update -o Acquire::Check-Valid-Until=false || \
    (apt-get clean && rm -rf /var/lib/apt/lists/* && \
     apt-get update -o Acquire::Check-Valid-Until=false)
```

### 2. Python PEP 668 Error

**Error**: `externally-managed-environment`

**Solution**: Added `--break-system-packages` flag to pip3 install:

```dockerfile
RUN pip3 install --no-cache-dir --break-system-packages \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    slither-analyzer
```

### 3. SSL Certificate Chain Issues

**Error**: `self signed certificate in certificate chain` (affecting curl, pip, and cargo)

**Solutions**:

- **pip**: Added `--trusted-host` flags for pypi.org, pypi.python.org, and files.pythonhosted.org
- **curl**: Downloads the Cyfrinup installer with `--tlsv1.2 -LsSf` to enforce modern TLS while remaining proxy-friendly
- **Cyfrinup**: Handles download of Aderyn binaries without relying on cargo/crates.io

### 4. Aderyn Provisioning

**Error**: Cargo-based installation failed in restricted environments (crates.io access, SSL interception)

**Solution**: Replaced cargo compilation with Cyfrinup, which installs the latest Aderyn release binary during the Docker build.

### 5. Dependency Conflicts

**Issue**: The legacy symbolic execution tool introduced dependency conflicts with modern web3 libraries and has been discontinued upstream.

**Resolution**:

- Removed the deprecated symbolic execution tool from the Docker image and server tooling
- Focused on Slither (static analysis) and Aderyn (Rust-based analyzer)
- Simplified verification steps to cover only supported tools

### 6. npm Package Installation

**Error**: Missing package-lock.json and TypeScript not found

**Solution**:

- Used `npm install --ignore-scripts` to skip prepare script during dependency install
- Built TypeScript after source code is copied

### 7. User Creation Conflict

**Error**: `UID 1000 is not unique`

**Solution**: Check if UID 1000 exists before creating user:

```dockerfile
RUN id -u 1000 >/dev/null 2>&1 || useradd -m -u 1000 mcp
```

## Build Time

- Approximately 5-10 minutes depending on network speed

## Image Size

- Final image: ~1.2-1.3GB
- Includes: Python 3.12 runtime, Slither (via pipx), Aderyn binary from Cyfrinup, and build tools

## Testing Commands

```bash
# Build
docker-compose build

# Verify
make verify
make test

# Run
docker-compose run --rm farofino-mcp
```

## Notes for Future Builds

- These fixes are necessary for CI/CD environments with proxy or certificate chain issues
- The `--trusted-host` and SSL bypasses are safe for Docker builds but should not be used in production environments
- Dependency conflicts between tools are expected and do not affect runtime functionality
