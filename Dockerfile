# Multi-stage build for a slim MCP Smart Contract Auditor container
# Stage 1: Build Rust-based tools (Aderyn)
FROM rust:1.75-slim AS rust-builder

WORKDIR /build

# Install Aderyn
RUN cargo install aderyn

# Stage 2: Final slim image
FROM node:20-slim

LABEL maintainer="mcp-scaudit"
LABEL description="MCP Smart Contract Auditor with Slither, Aderyn, and Mythril pre-installed"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    git \
    build-essential \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python-based tools (Slither and Mythril)
RUN pip3 install --no-cache-dir \
    slither-analyzer==0.10.0 \
    mythril==0.24.8 \
    && rm -rf ~/.cache/pip

# Copy Aderyn from rust-builder stage
COPY --from=rust-builder /usr/local/cargo/bin/aderyn /usr/local/bin/aderyn

# Verify installations
RUN slither --version && \
    aderyn --version && \
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

# Health check to verify all tools are available
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "const {execSync} = require('child_process'); \
    try { \
        execSync('slither --version', {stdio: 'ignore'}); \
        execSync('aderyn --version', {stdio: 'ignore'}); \
        execSync('myth version', {stdio: 'ignore'}); \
        process.exit(0); \
    } catch (e) { \
        process.exit(1); \
    }"
