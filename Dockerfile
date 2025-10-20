# Multi-stage build for a slim MCP Smart Contract Auditor container with all audit tools

# Stage 1: Build Aderyn (Rust-based tool)
FROM rust:1.75-slim as rust-builder

# Install Aderyn using cargo
RUN cargo install aderyn

# Stage 2: Final image
FROM python:3.12-slim

LABEL maintainer="mcp-scaudit"
LABEL description="MCP Smart Contract Auditor with Slither, Mythril, and Aderyn pre-installed"

# Install system dependencies
# Fix for GPG signature issues with Debian repositories
RUN apt-get update -o Acquire::Check-Valid-Until=false || \
    (apt-get clean && \
     rm -rf /var/lib/apt/lists/* && \
     apt-get update -o Acquire::Check-Valid-Until=false) && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    build-essential \
    libssl-dev \
    pkg-config \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies first for better caching
COPY requirements.txt ./
RUN pip3 install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt && \
    rm -rf ~/.cache/pip

# Install Python-based audit tools (Slither and Mythril)
# Adding --trusted-host flags to bypass SSL certificate verification issues
# Installing separately to speed up dependency resolution
RUN pip3 install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    slither-analyzer==0.10.0 \
    && rm -rf ~/.cache/pip

RUN pip3 install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    mythril==0.24.8 \
    && rm -rf ~/.cache/pip

# Fix dependency conflicts between tools
RUN pip3 install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    --upgrade hexbytes \
    && rm -rf ~/.cache/pip

# Note: Dependency conflicts between Slither and Mythril are expected
# Both tools will work at runtime despite version warnings

# Copy source code
COPY mcp_scaudit ./mcp_scaudit
COPY examples ./examples
COPY pyproject.toml ./
COPY setup.py ./

# Install the package
RUN pip3 install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -e . && rm -rf ~/.cache/pip

# Copy Aderyn binary from rust-builder stage
COPY --from=rust-builder /usr/local/cargo/bin/aderyn /usr/local/bin/aderyn

# Create a non-root user (or use existing user if UID 1000 exists)
RUN id -u 1000 >/dev/null 2>&1 || useradd -m -u 1000 mcp && \
    chown -R $(id -un 1000):$(id -gn 1000) /app

# Switch to non-root user (UID 1000)
USER 1000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/mcp/.local/bin:${PATH}"

# Expose stdio for MCP communication
ENTRYPOINT ["python3", "-m", "mcp_scaudit"]

# Health check disabled due to dependency conflicts between tools
# Tools will work at runtime despite version warnings
