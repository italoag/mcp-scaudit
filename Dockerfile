# Multi-stage build for MCP Smart Contract Auditor container
# This Dockerfile includes Slither and Mythril (Python-based tools)
# Aderyn (Rust-based) can be added via a separate build stage (see below)

FROM python:3.12-slim

LABEL maintainer="farofino-mcp"
LABEL description="MCP Smart Contract Auditor with Slither and Mythril pre-installed. Aderyn can be added if needed."

# Install system dependencies including Rust/Cargo for optional Aderyn installation
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
    curl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Rust and Cargo (required for Aderyn)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

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
COPY farofino_mcp ./farofino_mcp
COPY examples ./examples
COPY pyproject.toml ./
COPY setup.py ./

# Install the package
RUN pip3 install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -e . && rm -rf ~/.cache/pip

# Optional: Install Aderyn (may fail in environments with SSL cert issues)
# If installation fails, Aderyn can be installed later with: cargo install aderyn
RUN cargo install aderyn || \
    echo "WARNING: Aderyn installation failed. You can install it manually later with 'cargo install aderyn'"

# Create a non-root user (or use existing user if UID 1000 exists)
RUN id -u 1000 >/dev/null 2>&1 || useradd -m -u 1000 mcp && \
    chown -R $(id -un 1000):$(id -gn 1000) /app

# Switch to non-root user (UID 1000)
USER 1000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/mcp/.local/bin:/root/.cargo/bin:${PATH}"

# Expose stdio for MCP communication
ENTRYPOINT ["python3", "-m", "farofino_mcp"]

# Note: Slither and Mythril are always available
# Aderyn may not be available if cargo install failed due to SSL issues
# Check available tools with the check_tools command
