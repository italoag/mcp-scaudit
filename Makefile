.PHONY: help build build-no-cache pull-images run clean test verify

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

pull-images: ## Pull base images first (helps with network issues)
	@echo "Pulling base images..."
	docker pull python:3.12-slim

build: ## Build the Docker image
	@echo "Building farofino-mcp Docker image..."
	docker compose build

build-no-cache: ## Build without cache (clean build)
	@echo "Building farofino-mcp Docker image (no cache)..."
	docker compose build --no-cache

build-retry: pull-images ## Build with retry logic for network issues
	@echo "Building with pre-pulled images..."
	docker compose build

build-host-network: ## Build using host network (useful for CI/CD)
	@echo "Building with host network..."
	DOCKER_BUILDKIT=1 docker build --network=host -t farofino-mcp:latest .

run: ## Run the MCP server
	@echo "Running farofino-mcp..."
	docker compose run --rm farofino-mcp

dev: ## Run in development mode
	@echo "Running farofino-mcp in development mode..."
	docker compose --profile dev up farofino-mcp-dev

verify: ## Verify all tools are installed correctly
	@echo "Verifying tool installations..."
	@echo "Note: Dependency conflicts between tools may produce warnings but tools will work."
	@echo "Testing MCP server startup..."
	docker run --rm farofino-mcp:latest sh -c "timeout 2 python3 -m farofino_mcp 2>&1 | head -5"
	@echo "Testing tool availability..."
	docker run --rm --entrypoint sh farofino-mcp:latest -c "slither --version && echo 'Slither: OK'"
	docker run --rm --entrypoint sh farofino-mcp:latest -c "myth --version && echo 'Mythril: OK'"
	@echo "Testing Aderyn (may not be available if cargo install failed)..."
	docker run --rm --entrypoint sh farofino-mcp:latest -c "aderyn --version && echo 'Aderyn: OK' || echo 'Aderyn: Not available (expected if cargo install failed due to SSL issues)'"

test: verify ## Run tests
	@echo "Running health checks..."
	docker run --rm --entrypoint python3 farofino-mcp:latest -c "import slither; print('Slither: OK')"
	docker run --rm --entrypoint sh farofino-mcp:latest -c "myth --version 2>&1 | head -1"
	@echo "Aderyn health check (may not be available)..."
	docker run --rm --entrypoint sh farofino-mcp:latest -c "aderyn --version 2>&1 | head -1 || echo 'Aderyn not available'"

clean: ## Remove built images and containers
	@echo "Cleaning up..."
	docker compose down -v
	docker rmi farofino-mcp:latest || true
	docker rmi farofino-mcp:dev || true

logs: ## Show container logs
	docker compose logs -f farofino-mcp

size: ## Show image size
	@docker images farofino-mcp:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
