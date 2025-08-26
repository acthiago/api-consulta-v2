# ===== API Consulta v2 - Makefile =====
.PHONY: help install dev test lint format security build run clean docker-build docker-run docker-stop

# Colors for output
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Variables
PYTHON := python3
PIP := pip3
DOCKER_IMAGE := poc-api-consulta-v2
DOCKER_TAG := latest

help: ## 📋 Show this help message
	@echo "$(GREEN)🚀 API Consulta v2 - Available Commands$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make $(YELLOW)<target>$(RESET)\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ 🛠️  Development
install: ## 📦 Install dependencies
	@echo "$(GREEN)📦 Installing dependencies...$(RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov pytest-asyncio black isort flake8 mypy safety bandit

dev: ## 🚀 Start development environment
	@echo "$(GREEN)🚀 Starting development environment...$(RESET)"
	docker-compose -f docker-compose.dev.yml up -d

dev-logs: ## 📄 Show development logs
	@echo "$(GREEN)📄 Showing development logs...$(RESET)"
	docker-compose -f docker-compose.dev.yml logs -f

dev-stop: ## ⏹️  Stop development environment
	@echo "$(YELLOW)⏹️  Stopping development environment...$(RESET)"
	docker-compose -f docker-compose.dev.yml down

##@ 🧪 Testing & Quality
test: ## 🧪 Run tests
	@echo "$(GREEN)🧪 Running tests...$(RESET)"
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-unit: ## 🎯 Run unit tests only
	@echo "$(GREEN)🎯 Running unit tests...$(RESET)"
	$(PYTHON) -m pytest tests/unit/ -v

test-integration: ## 🔗 Run integration tests only
	@echo "$(GREEN)🔗 Running integration tests...$(RESET)"
	$(PYTHON) -m pytest tests/integration/ -v

lint: ## 🔍 Run linting checks
	@echo "$(GREEN)🔍 Running linting checks...$(RESET)"
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports

format: ## ✨ Format code
	@echo "$(GREEN)✨ Formatting code...$(RESET)"
	black src/ tests/
	isort src/ tests/

format-check: ## 📋 Check code formatting
	@echo "$(GREEN)📋 Checking code formatting...$(RESET)"
	black --check --diff src/ tests/
	isort --check-only --diff src/ tests/

security: ## 🔒 Run security checks
	@echo "$(GREEN)🔒 Running security checks...$(RESET)"
	safety check -r requirements.txt
	bandit -r src/ -f json -o bandit-report.json || true
	@echo "$(GREEN)📊 Security report saved to bandit-report.json$(RESET)"

quality: format lint security test ## 🏆 Run all quality checks

##@ 🐳 Docker
docker-build: ## 🏗️  Build Docker image
	@echo "$(GREEN)🏗️  Building Docker image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-dev: ## � Run development environment
	@echo "$(GREEN)🚀 Starting development environment...$(RESET)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✅ Development environment running at http://localhost:8000$(RESET)"

docker-prod: ## 🏭 Run production environment
	@echo "$(GREEN)🏭 Starting production environment...$(RESET)"
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production environment running at http://localhost:8000$(RESET)"

docker-stop: ## ⏹️  Stop all Docker services
	@echo "$(YELLOW)⏹️  Stopping all Docker services...$(RESET)"
	docker-compose -f docker-compose.dev.yml down || true
	docker-compose -f docker-compose.prod.yml down || true
	docker-compose down || true

docker-logs: ## 📄 Show Docker logs
	@echo "$(GREEN)📄 Showing Docker logs...$(RESET)"
	docker-compose logs -f

##@ 🚀 Production
build: ## 🏭 Production build
	@echo "$(GREEN)🏭 Building for production...$(RESET)"
	docker build --target production -t $(DOCKER_IMAGE):prod .

run: ## ▶️  Run application locally
	@echo "$(GREEN)▶️  Running application...$(RESET)"
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

##@ 🧹 Cleanup
clean: ## 🧹 Clean up temporary files
	@echo "$(GREEN)🧹 Cleaning up...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "bandit-report.json" -delete

clean-docker: ## 🐳 Clean Docker resources
	@echo "$(GREEN)🐳 Cleaning Docker resources...$(RESET)"
	docker system prune -f
	docker image prune -f
	docker volume prune -f

##@ 📊 Monitoring
monitor: ## 📊 Open monitoring dashboards
	@echo "$(GREEN)📊 Opening monitoring dashboards...$(RESET)"
	@echo "Grafana: http://localhost:3000 (admin/admin123)"
	@echo "Prometheus: http://localhost:9090"

health: ## 🔍 Check application health
	@echo "$(GREEN)🔍 Checking application health...$(RESET)"
	curl -f http://localhost:8000/health || echo "$(RED)❌ Application is not healthy$(RESET)"

##@ 📚 Documentation
docs: ## 📚 Generate documentation
	@echo "$(GREEN)📚 Documentation available at:$(RESET)"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
	@echo "API Reference: docs/API_REFERENCE.md"
	@echo "Architecture: docs/ARCHITECTURE.md"

##@ 🔧 Utilities
env-example: ## 📝 Create .env example file
	@echo "$(GREEN)📝 Creating .env.example...$(RESET)"
	@echo "# Environment Configuration" > .env.example
	@echo "DEBUG=true" >> .env.example
	@echo "LOG_LEVEL=INFO" >> .env.example
	@echo "SECRET_KEY=your-secret-key-here" >> .env.example
	@echo "JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30" >> .env.example
	@echo "JWT_REFRESH_TOKEN_EXPIRE_DAYS=7" >> .env.example
	@echo "MONGO_URI=mongodb://localhost:27017" >> .env.example
	@echo "MONGO_DB_NAME=api_consulta_v2" >> .env.example
	@echo "REDIS_URL=redis://localhost:6379/0" >> .env.example
	@echo "CACHE_TTL_CLIENTE=1800" >> .env.example
	@echo "CACHE_TTL_PAGAMENTO=1800" >> .env.example
	@echo "CACHE_TTL_BOLETO=3600" >> .env.example
	@echo "$(GREEN)✅ .env.example created$(RESET)"

init: install env-example ## 🎯 Initialize project for development
	@echo "$(GREEN)🎯 Project initialized for development!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "1. Copy .env.example to .env and configure"
	@echo "2. Run 'make dev' to start development environment"
	@echo "3. Run 'make test' to run tests"
