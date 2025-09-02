#!/bin/bash

# Deploy VPS - Atualização com Dashboards
set -e

echo "🚀 Iniciando deploy no VPS..."

# Configurações
VPS_HOST="69.62.103.163"
VPS_USER="root"
VPS_PATH="/opt/api-consulta-v2"

echo "📁 Verificando estrutura local..."
if [[ ! -f "docker-compose.vps.yml" ]]; then
    echo "❌ Arquivo docker-compose.vps.yml não encontrado!"
    exit 1
fi

if [[ ! -d "monitoring/grafana/dashboards" ]]; then
    echo "❌ Pasta de dashboards não encontrada!"
    exit 1
fi

echo "📋 Dashboards encontrados:"
ls -la monitoring/grafana/dashboards/

echo "📦 Preparando arquivos para deploy..."
# Criar diretório temporário
mkdir -p /tmp/api-deploy

# Copiar arquivos essenciais
cp docker-compose.vps.yml /tmp/api-deploy/
cp monitoring/prometheus.prod.yml /tmp/api-deploy/
cp -r monitoring/grafana/ /tmp/api-deploy/

# Verificar se os dashboards foram copiados
echo "✅ Arquivos preparados:"
find /tmp/api-deploy -name "*.json" -type f

echo "🔗 Conectando no VPS ${VPS_HOST}..."
# Criar estrutura no VPS
ssh ${VPS_USER}@${VPS_HOST} "mkdir -p ${VPS_PATH}/monitoring/grafana/dashboards"

echo "📤 Enviando arquivos para o VPS..."
# Enviar docker-compose
scp /tmp/api-deploy/docker-compose.vps.yml ${VPS_USER}@${VPS_HOST}:${VPS_PATH}/docker-compose.yml

# Enviar configuração do Prometheus
scp /tmp/api-deploy/prometheus.prod.yml ${VPS_USER}@${VPS_HOST}:${VPS_PATH}/monitoring/prometheus.yml

# Enviar dashboards do Grafana
scp -r /tmp/api-deploy/grafana/* ${VPS_USER}@${VPS_HOST}:${VPS_PATH}/monitoring/grafana/

echo "🔄 Atualizando serviços no VPS..."
ssh ${VPS_USER}@${VPS_HOST} << 'EOF'
cd /opt/api-consulta-v2

echo "🛑 Parando serviços..."
docker-compose down

echo "🔥 Removendo volumes antigos do Grafana..."
docker volume rm apicontolav2_grafana-storage 2>/dev/null || true

echo "📂 Verificando estrutura de arquivos..."
echo "Docker Compose:"
ls -la docker-compose.yml
echo "Prometheus config:"
ls -la monitoring/prometheus.yml
echo "Dashboards:"
ls -la monitoring/grafana/dashboards/

echo "🚀 Subindo serviços atualizados..."
docker-compose pull
docker-compose up -d

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

echo "🏥 Verificando status dos serviços..."
docker-compose ps

echo "🌐 Verificando health checks..."
curl -f http://localhost:3000/health || echo "⚠️  Grafana ainda inicializando..."
curl -f http://localhost:9090/-/healthy || echo "⚠️  Prometheus ainda inicializando..."

echo "✅ Deploy concluído!"
echo "🎯 Grafana: http://69.62.103.163:3000 (admin/admin)"
echo "📊 Prometheus: http://69.62.103.163:9090"
EOF

echo "🧹 Limpando arquivos temporários..."
rm -rf /tmp/api-deploy

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "🔗 Acesse os dashboards em: http://69.62.103.163:3000"
echo "📊 Dashboards disponíveis:"
echo "  - 🚀 API Performance & Health"
echo "  - 🔴 Redis Cache Performance"
echo "  - 🍃 MongoDB Database Performance"
echo ""
echo "🔑 Login padrão do Grafana: admin/admin"
echo "💡 Lembre-se de alterar a senha na primeira vez!"
