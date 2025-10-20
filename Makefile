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
	@echo "Building mcp-scaudit Docker image..."
	docker-compose build

build-no-cache: ## Build without cache (clean build)
	@echo "Building mcp-scaudit Docker image (no cache)..."
	docker-compose build --no-cache

build-retry: pull-images ## Build with retry logic for network issues
	@echo "Building with pre-pulled images..."
	docker-compose build

build-host-network: ## Build using host network (useful for CI/CD)
	@echo "Building with host network..."
	DOCKER_BUILDKIT=1 docker build --network=host -t mcp-scaudit:latest .

run: ## Run the MCP server
	@echo "Running mcp-scaudit..."
	docker-compose run --rm mcp-scaudit

dev: ## Run in development mode
	@echo "Running mcp-scaudit in development mode..."
	docker-compose --profile dev up mcp-scaudit-dev

verify: ## Verify all tools are installed correctly
	@echo "Verifying tool installations..."
	@echo "Note: Dependency conflicts between tools may produce warnings but tools will work."
	@echo "Testing MCP server startup..."
	docker run --rm mcp-scaudit:latest sh -c "timeout 2 python3 -m mcp_scaudit 2>&1 | head -5"
	@echo "Testing tool availability..."
	docker run --rm --entrypoint sh mcp-scaudit:latest -c "slither --version && echo 'Slither: OK'"
	docker run --rm --entrypoint sh mcp-scaudit:latest -c "myth --version && echo 'Mythril: OK'"
	docker run --rm --entrypoint sh mcp-scaudit:latest -c "aderyn --version && echo 'Aderyn: OK'"

test: verify ## Run tests
	@echo "Running health checks..."
	docker run --rm --entrypoint python3 mcp-scaudit:latest -c "import slither; print('Slither: OK')"
	docker run --rm --entrypoint sh mcp-scaudit:latest -c "myth --version 2>&1 | head -1"
	docker run --rm --entrypoint sh mcp-scaudit:latest -c "aderyn --version 2>&1 | head -1"

clean: ## Remove built images and containers
	@echo "Cleaning up..."
	docker-compose down -v
	docker rmi mcp-scaudit:latest || true
	docker rmi mcp-scaudit:dev || true

logs: ## Show container logs
	docker-compose logs -f mcp-scaudit

size: ## Show image size
	@docker images mcp-scaudit:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
