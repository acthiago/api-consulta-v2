#!/bin/bash

# Deploy script para VPS de produção
# Uso: ./deploy-vps.sh [tag_da_imagem]

set -e

VPS_IP="69.62.103.163"
VPS_USER="root"
PROJECT_DIR="/opt/api-consulta-v2"
IMAGE_TAG="${1:-latest}"

echo "🚀 Iniciando deploy para VPS de produção..."
echo "📍 VPS IP: $VPS_IP"
echo "🏷️  Image tag: $IMAGE_TAG"

# Função para executar comandos na VPS
run_on_vps() {
    ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "$1"
}

# Função para copiar arquivos para VPS
copy_to_vps() {
    scp -o StrictHostKeyChecking=no "$1" $VPS_USER@$VPS_IP:"$2"
}

echo "📋 Verificando conectividade com VPS..."
if ! run_on_vps "echo 'Conexão OK'"; then
    echo "❌ Erro: Não foi possível conectar na VPS"
    exit 1
fi

echo "📁 Criando estrutura de diretórios na VPS..."
run_on_vps "mkdir -p $PROJECT_DIR/logs $PROJECT_DIR/storage $PROJECT_DIR/monitoring/grafana/dashboards"

echo "📄 Copiando arquivos de configuração..."
copy_to_vps "docker-compose.vps.yml" "$PROJECT_DIR/docker-compose.yml"
copy_to_vps "nginx.vps.conf" "$PROJECT_DIR/nginx.conf"
copy_to_vps "monitoring/prometheus.prod.yml" "$PROJECT_DIR/monitoring/prometheus.yml"

echo "📊 Copiando configurações do Grafana..."
if [ -f "monitoring/grafana/dashboards/api-monitoring.json" ]; then
    copy_to_vps "monitoring/grafana/dashboards/api-monitoring.json" "$PROJECT_DIR/monitoring/grafana/dashboards/"
fi

echo "📦 Parando containers existentes..."
run_on_vps "cd $PROJECT_DIR && docker compose down || echo 'Nenhum container rodando'"

echo "🔄 Baixando nova imagem..."
run_on_vps "docker pull \${DOCKER_HUB_USERNAME}/poc-api-consulta-v2:$IMAGE_TAG"

echo "🏷️  Atualizando tag da imagem..."
run_on_vps "cd $PROJECT_DIR && sed -i 's|image:.*poc-api-consulta-v2:.*|image: \${DOCKER_HUB_USERNAME}/poc-api-consulta-v2:$IMAGE_TAG|' docker-compose.yml"

echo "🚀 Iniciando novos containers..."
run_on_vps "cd $PROJECT_DIR && docker compose up -d"

echo "⏳ Aguardando containers iniciarem..."
sleep 15

echo "🏥 Verificando saúde da API..."
if run_on_vps "curl -f http://localhost:8000/health"; then
    echo "✅ API está saudável!"
else
    echo "❌ Erro: API não está respondendo"
    echo "📝 Logs da API:"
    run_on_vps "cd $PROJECT_DIR && docker compose logs api --tail=20"
    exit 1
fi

echo "📊 Verificando Redis Exporter..."
if run_on_vps "curl -f http://localhost:9121/metrics > /dev/null"; then
    echo "✅ Redis Exporter funcionando!"
else
    echo "❌ Erro: Redis Exporter não está respondendo"
    echo "📝 Logs do Redis Exporter:"
    run_on_vps "cd $PROJECT_DIR && docker compose logs redis-exporter --tail=10"
fi

echo "🔍 Verificando Prometheus..."
if run_on_vps "curl -f http://localhost:9090/prometheus/-/healthy > /dev/null"; then
    echo "✅ Prometheus funcionando!"
else
    echo "❌ Erro: Prometheus não está respondendo"
    echo "📝 Logs do Prometheus:"
    run_on_vps "cd $PROJECT_DIR && docker compose logs prometheus --tail=10"
fi

echo "🌐 Testando acesso externo..."
if curl -f "http://$VPS_IP:8000/health"; then
    echo "✅ API acessível externamente!"
else
    echo "⚠️  Aviso: API não acessível externamente (firewall?)"
fi

echo "📊 Status dos containers:"
run_on_vps "cd $PROJECT_DIR && docker compose ps"

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "🌐 API disponível em: http://$VPS_IP:8000"
echo "📊 Documentação: http://$VPS_IP:8000/docs"
echo "🏥 Health check: http://$VPS_IP:8000/health"
echo "📈 Métricas: http://$VPS_IP:9090 (Prometheus)"
echo ""
echo "🔧 Comandos úteis:"
echo "  Logs da API: ssh $VPS_USER@$VPS_IP 'cd $PROJECT_DIR && docker compose logs api'"
echo "  Restart: ssh $VPS_USER@$VPS_IP 'cd $PROJECT_DIR && docker compose restart api'"
echo "  Status: ssh $VPS_USER@$VPS_IP 'cd $PROJECT_DIR && docker compose ps'"
