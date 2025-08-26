# ===== API Consulta v2 - Makefile =====
.PHONY: help docker-dev docker-prod docker-stop check-requirements

# Variables
DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

help:
	@echo "API Consulta v2 - Available Commands"
	@echo "Using Docker Compose: $(DOCKER_COMPOSE)"
	@echo "  check-requirements - Check system requirements"
	@echo "  docker-dev         - Start development environment"
	@echo "  docker-prod        - Start production environment"  
	@echo "  docker-stop        - Stop all Docker services"

check-requirements:
	@echo "Checking system requirements..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed"; exit 1; }
	@echo "✅ Docker: $$(docker --version)"
	@echo "✅ Docker Compose: $(DOCKER_COMPOSE)"
	@$(DOCKER_COMPOSE) version >/dev/null 2>&1 || { echo "❌ Docker Compose is not working"; exit 1; }
	@echo "✅ All requirements satisfied"

docker-dev:
	@echo "Starting development environment..."
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up -d
	@echo "Development environment running at http://localhost:8000"

docker-prod:
	@echo "Starting production environment..."
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d
	@echo "Production environment running at http://localhost:8000"

docker-stop:
	@echo "Stopping all Docker services..."
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml down || true
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml down || true
	$(DOCKER_COMPOSE) down || true
