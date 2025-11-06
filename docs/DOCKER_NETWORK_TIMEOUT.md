# Docker Network Timeout - Quick Fix Guide

If you're experiencing Docker build timeouts with errors like:
```
failed to resolve source metadata for docker.io/library/node:20-slim
dial tcp ... i/o timeout
```

## Quick Fixes (Choose One)

### 1. Pre-pull Images (Recommended)
```bash
docker pull rust:1.75-slim
docker pull node:20-slim
docker-compose build
```

### 2. Use Makefile (Easiest)
```bash
make build-retry
```

### 3. Increase Timeout
```bash
COMPOSE_HTTP_TIMEOUT=300 docker-compose build
```

### 4. Use Host Network (For CI/CD)
```bash
DOCKER_BUILDKIT=1 docker build --network=host -t farofino-mcp:latest .
```

### 5. Behind Corporate Proxy
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
docker-compose build
```

### 6. For Restricted Regions
Edit `/etc/docker/daemon.json` (Linux) or Docker Desktop Settings → Docker Engine (Mac/Windows):
```json
{
  "registry-mirrors": ["https://mirror.gcr.io"]
}
```
Restart Docker daemon, then:
```bash
docker-compose build
```

## For CI/CD (GitHub Actions Example)
```yaml
- name: Build with retry
  run: |
    for i in {1..3}; do
      docker-compose build && break || sleep 15
    done
```

## See DOCKER.md for detailed troubleshooting
