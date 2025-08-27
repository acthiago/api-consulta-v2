# ===== API Consulta v2 - Makefile =====
.PHONY: help docker-dev docker-prod docker-vps docker-stop check-requirements

# Variables
DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

help:
	@echo "API Consulta v2 - Available Commands"
	@echo "Using Docker Compose: $(DOCKER_COMPOSE)"
	@echo "  check-requirements - Check system requirements"
	@echo "  docker-dev         - Start development environment"
	@echo "  docker-prod        - Start production environment"
	@echo "  docker-vps         - Start VPS production environment"  
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

docker-vps:
	@echo "🚀 Iniciando deploy para VPS com stack completo..."
	@echo "📋 Parando serviços existentes..."
	$(DOCKER_COMPOSE) -f docker-compose.vps.yml down --remove-orphans || true
	@echo "🔄 Atualizando imagens..."
	$(DOCKER_COMPOSE) -f docker-compose.vps.yml pull || true
	@echo "🏗️  Iniciando stack completo (API + Redis + Prometheus + Grafana)..."
	$(DOCKER_COMPOSE) -f docker-compose.vps.yml up -d --force-recreate
	@echo "⏳ Aguardando inicialização dos serviços..."
	@sleep 45
	@echo "🔍 Verificando status dos serviços..."
	$(DOCKER_COMPOSE) -f docker-compose.vps.yml ps
	@echo "🌐 Testando conectividade dos serviços..."
	@curl -f http://localhost/health || echo "⚠️  API health check falhou"
	@curl -f http://localhost/grafana/api/health || echo "⚠️  Grafana health check falhou"
	@curl -f http://localhost/prometheus/-/healthy || echo "⚠️  Prometheus health check falhou"
	@echo "✅ Deploy concluído! Stack completo disponível:"
	@echo "   🚀 API: http://69.62.103.163/api/docs"
	@echo "   📊 Grafana: http://69.62.103.163/grafana (admin/admin123)"
	@echo "   📈 Prometheus: http://69.62.103.163/prometheus"
	@echo "   📋 Redis: Disponível internamente na rede"

docker-stop:
	@echo "Stopping all Docker services..."
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml down || true
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml down || true
	$(DOCKER_COMPOSE) -f docker-compose.vps.yml down || true
	$(DOCKER_COMPOSE) down || true
