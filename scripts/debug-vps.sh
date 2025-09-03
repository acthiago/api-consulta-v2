#!/bin/bash

# Script de debugging para ambiente VPS
echo "=== API Consulta V2 - Debug VPS ==="
echo "Data: $(date)"
echo

# Função para verificar status de containers
check_containers() {
    echo "=== STATUS DOS CONTAINERS ==="
    docker-compose -f docker-compose.vps.yml ps
    echo
}

# Função para verificar logs
check_logs() {
    echo "=== LOGS DOS PRINCIPAIS SERVIÇOS ==="
    
    echo "--- Prometheus ---"
    docker-compose -f docker-compose.vps.yml logs --tail=20 prometheus
    echo
    
    echo "--- Grafana ---"
    docker-compose -f docker-compose.vps.yml logs --tail=20 grafana
    echo
    
    echo "--- API ---"
    docker-compose -f docker-compose.vps.yml logs --tail=20 api
    echo
}

# Função para verificar conectividade
check_connectivity() {
    echo "=== TESTE DE CONECTIVIDADE ==="
    
    # Testar se Prometheus está respondendo
    echo "Testando Prometheus (porta 9090)..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy | grep -q "200"; then
        echo "✅ Prometheus respondendo"
    else
        echo "❌ Prometheus não está respondendo"
    fi
    
    # Testar se Grafana está respondendo
    echo "Testando Grafana (porta 3000)..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health | grep -q "200"; then
        echo "✅ Grafana respondendo"
    else
        echo "❌ Grafana não está respondendo"
    fi
    
    # Testar se API está respondendo
    echo "Testando API (porta 8000)..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
        echo "✅ API respondendo"
    else
        echo "❌ API não está respondendo"
    fi
    echo
}

# Função para verificar configurações
check_configs() {
    echo "=== VERIFICAÇÃO DE CONFIGURAÇÕES ==="
    
    echo "Arquivos de configuração do Prometheus:"
    if [ -f "./monitoring/prometheus-vps/prometheus-robust.yml" ]; then
        echo "✅ prometheus-robust.yml existe"
    else
        echo "❌ prometheus-robust.yml não encontrado"
    fi
    
    echo "Arquivos de provisioning do Grafana:"
    if [ -d "./monitoring/grafana/provisioning-vps" ]; then
        echo "✅ Diretório provisioning-vps existe"
        ls -la ./monitoring/grafana/provisioning-vps/datasources/
    else
        echo "❌ Diretório provisioning-vps não encontrado"
    fi
    echo
}

# Função para restart inteligente
restart_services() {
    echo "=== RESTART DOS SERVIÇOS ==="
    
    echo "Parando serviços..."
    docker-compose -f docker-compose.vps.yml down
    
    echo "Aguardando 5 segundos..."
    sleep 5
    
    echo "Iniciando serviços..."
    docker-compose -f docker-compose.vps.yml up -d
    
    echo "Aguardando inicialização..."
    sleep 30
    
    check_containers
}

# Menu principal
case "$1" in
    "status")
        check_containers
        ;;
    "logs")
        check_logs
        ;;
    "connectivity")
        check_connectivity
        ;;
    "config")
        check_configs
        ;;
    "restart")
        restart_services
        ;;
    "full")
        check_containers
        check_connectivity
        check_configs
        check_logs
        ;;
    *)
        echo "Uso: $0 {status|logs|connectivity|config|restart|full}"
        echo
        echo "status       - Mostra status dos containers"
        echo "logs         - Mostra logs recentes dos serviços"
        echo "connectivity - Testa conectividade dos serviços"
        echo "config       - Verifica configurações"
        echo "restart      - Restart completo dos serviços"
        echo "full         - Executa todos os checks"
        ;;
esac
