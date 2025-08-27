#!/bin/bash

# Script para testar o build Docker localmente
echo "🐳 Testando build Docker local..."

# Build da imagem
echo "📦 Fazendo build da imagem..."
docker build \
  --build-arg VERSION="local-test" \
  --build-arg BUILDTIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -t poc-api-consulta-v2:local-test \
  .

if [ $? -eq 0 ]; then
    echo "✅ Build realizado com sucesso!"
    
    echo "🚀 Testando execução do container..."
    docker run --rm -d \
      --name api-test \
      -p 8000:8000 \
      poc-api-consulta-v2:local-test
    
    echo "⏳ Aguardando 10 segundos para a API inicializar..."
    sleep 10
    
    echo "🏥 Testando health check..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API funcionando corretamente!"
    else
        echo "❌ API não respondeu ao health check"
    fi
    
    echo "🛑 Parando container de teste..."
    docker stop api-test
    
else
    echo "❌ Erro no build da imagem!"
    exit 1
fi
