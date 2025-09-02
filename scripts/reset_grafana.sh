#!/bin/bash

# Script para limpar e reinicializar o Grafana
# Use este script se houver problemas persistentes com datasources

echo "🧹 Limpando configurações do Grafana..."

# Parar o Grafana
echo "🛑 Parando Grafana..."
docker compose down grafana

# Remover volume do Grafana (isso apaga todas as configurações)
echo "🔥 Removendo volume do Grafana..."
docker volume rm api-consulta-v2_grafana_data 2>/dev/null || echo "Volume não existe"

# Recriar o serviço
echo "🚀 Recriando Grafana..."
docker compose up -d grafana

echo "⏳ Aguardando Grafana inicializar..."
sleep 20

# Verificar se está funcionando
echo "🏥 Verificando saúde do Grafana..."
if curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo "✅ Grafana está funcionando!"
    echo "🔗 Acesse: http://localhost:3000"
    echo "🔑 Login: admin/admin"
else
    echo "❌ Grafana não está respondendo"
fi

echo "📊 Verificando logs de provisionamento..."
docker compose logs grafana --tail 10 | grep -i "datasource\|dashboard"
