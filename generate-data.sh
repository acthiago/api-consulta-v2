#!/bin/bash

# Script de conveniência para gerar massa de dados
# Uso: ./generate-data.sh [opção]
# Opções: small, medium, large

cd "$(dirname "$0")"

case "$1" in
    "small")
        echo -e "2\ns\ns" | python scripts/database/generate_test_data.py
        ;;
    "medium")
        echo -e "1\ns\ns" | python scripts/database/generate_test_data.py
        ;;
    "large")
        echo -e "3\ns\ns" | python scripts/database/generate_test_data.py
        ;;
    *)
        echo "🎲 Gerador de Massa de Dados - API Consulta V2"
        echo "==============================================="
        echo ""
        echo "Uso: $0 [opção]"
        echo ""
        echo "Opções disponíveis:"
        echo "  small   - 20 clientes, 50 pagamentos, 30 boletos"
        echo "  medium  - 50 clientes, 200 pagamentos, 150 boletos"
        echo "  large   - 100 clientes, 500 pagamentos, 300 boletos"
        echo ""
        echo "Exemplos:"
        echo "  $0 small    # Gera dados para desenvolvimento"
        echo "  $0 medium   # Gera dados para testes"
        echo "  $0 large    # Gera dados para stress test"
        echo ""
        echo "Executando modo interativo..."
        python scripts/database/generate_test_data.py
        ;;
esac
