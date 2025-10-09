# Multi-stage build for a slim MCP Smart Contract Auditor container
# Note: Aderyn installation is skipped due to SSL certificate issues in build environment
# Users can install Aderyn separately if needed

# Stage 1: Final image
FROM node:20-slim

LABEL maintainer="mcp-scaudit"
LABEL description="MCP Smart Contract Auditor with Slither and Mythril pre-installed (Aderyn optional)"

# Install system dependencies
# Fix for GPG signature issues with Debian repositories
RUN apt-get update -o Acquire::Check-Valid-Until=false || \
    (apt-get clean && \
     rm -rf /var/lib/apt/lists/* && \
     apt-get update -o Acquire::Check-Valid-Until=false) && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    python3 \
    python3-pip \
    python3-dev \
    git \
    build-essential \
    libssl-dev \
    pkg-config \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python-based tools (Slither and Mythril)
# Using --break-system-packages flag required for Debian bookworm (PEP 668)
RUN pip3 install --no-cache-dir --break-system-packages \
    slither-analyzer==0.10.0 \
    mythril==0.24.8 \
    && rm -rf ~/.cache/pip

# Note: Aderyn installation is skipped due to SSL certificate issues in build environment
# Aderyn can be installed manually if needed: cargo install aderyn

# Verify installations
RUN slither --version && \
    myth version

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install Node.js dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY src ./src
COPY examples ./examples

# Build TypeScript
RUN npm run build

# Create a non-root user
RUN useradd -m -u 1000 mcp && \
    chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Set environment variables
ENV NODE_ENV=production
ENV PATH="/usr/local/bin:${PATH}"

# Expose stdio for MCP communication
ENTRYPOINT ["node", "dist/index.js"]

# Health check to verify tools are available (Slither and Mythril)
# Note: Aderyn check removed due to optional installation
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "const {execSync} = require('child_process'); \
    try { \
        execSync('slither --version', {stdio: 'ignore'}); \
        execSync('myth version', {stdio: 'ignore'}); \
        process.exit(0); \
    } catch (e) { \
        process.exit(1); \
    }"
