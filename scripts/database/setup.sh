#!/bin/bash

# MongoDB Database Scripts Setup
# Este script configura o ambiente para os scripts de gerenciamento do banco

set -e

echo "🚀 Configurando scripts de gerenciamento do MongoDB..."
echo "=================================================="

# Diretório dos scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se Python está instalado
check_python() {
    print_status "Verificando instalação do Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION encontrado"
    else
        print_error "Python 3 não encontrado. Por favor, instale Python 3.8+"
        exit 1
    fi
}

# Verifica se pip está instalado
check_pip() {
    print_status "Verificando instalação do pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 encontrado"
    else
        print_error "pip3 não encontrado. Instalando..."
        sudo apt-get update
        sudo apt-get install -y python3-pip
    fi
}

# Instala dependências Python
install_dependencies() {
    print_status "Instalando dependências Python..."
    
    # Lista de dependências necessárias
    DEPENDENCIES=(
        "pymongo>=4.5.0"
        "python-dotenv>=1.0.0"
        "click>=8.0.0"
        "tabulate>=0.9.0"
        "colorama>=0.4.6"
    )
    
    for dep in "${DEPENDENCIES[@]}"; do
        print_status "Instalando $dep..."
        pip3 install "$dep" --user
    done
    
    print_success "Todas as dependências foram instaladas"
}

# Cria estrutura de diretórios
create_directories() {
    print_status "Criando estrutura de diretórios..."
    
    # Cria diretórios necessários
    mkdir -p "$SCRIPT_DIR/logs"
    mkdir -p "$SCRIPT_DIR/backups"
    mkdir -p "$SCRIPT_DIR/config"
    
    print_success "Estrutura de diretórios criada"
}

# Configura permissões
setup_permissions() {
    print_status "Configurando permissões dos scripts..."
    
    # Torna os scripts executáveis
    chmod +x "$SCRIPT_DIR"/*.py
    chmod +x "$SCRIPT_DIR/setup.sh"
    
    # Define permissões adequadas para diretórios
    chmod 755 "$SCRIPT_DIR/logs"
    chmod 755 "$SCRIPT_DIR/backups"
    chmod 755 "$SCRIPT_DIR/config"
    
    print_success "Permissões configuradas"
}

# Cria arquivo de configuração se não existir
setup_config() {
    print_status "Configurando arquivo de ambiente..."
    
    ENV_FILE="$SCRIPT_DIR/.env"
    EXAMPLE_FILE="$SCRIPT_DIR/.env.example"
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$EXAMPLE_FILE" ]; then
            cp "$EXAMPLE_FILE" "$ENV_FILE"
            print_success "Arquivo .env criado a partir do exemplo"
            print_warning "IMPORTANTE: Configure sua string de conexão MongoDB no arquivo .env"
        else
            print_error "Arquivo .env.example não encontrado"
        fi
    else
        print_success "Arquivo .env já existe"
    fi
}

# Cria scripts de conveniência
create_convenience_scripts() {
    print_status "Criando scripts de conveniência..."
    
    # Script para gerenciador do MongoDB
    cat > "$SCRIPT_DIR/mongo-manager" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 mongo_manager.py "$@"
EOF
    
    # Script para migrações
    cat > "$SCRIPT_DIR/migrate" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 migrations.py "$@"
EOF
    
    # Script para monitoramento
    cat > "$SCRIPT_DIR/monitor" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 monitoring.py "$@"
EOF
    
    # Torna os scripts executáveis
    chmod +x "$SCRIPT_DIR/mongo-manager"
    chmod +x "$SCRIPT_DIR/migrate"
    chmod +x "$SCRIPT_DIR/monitor"
    
    print_success "Scripts de conveniência criados"
}

# Testa a instalação
test_installation() {
    print_status "Testando instalação..."
    
    # Testa importação do pymongo
    if python3 -c "import pymongo; print('PyMongo OK')" &> /dev/null; then
        print_success "PyMongo funcionando corretamente"
    else
        print_error "Erro ao importar PyMongo"
        return 1
    fi
    
    # Verifica se os scripts podem ser executados
    if python3 -c "import sys; sys.path.append('$SCRIPT_DIR'); import mongo_manager" &> /dev/null; then
        print_success "Scripts do MongoDB funcionando"
    else
        print_error "Erro ao carregar scripts do MongoDB"
        return 1
    fi
    
    return 0
}

# Mostra instruções de uso
show_usage_instructions() {
    echo ""
    echo "🎉 Setup concluído com sucesso!"
    echo "================================"
    echo ""
    echo "📋 Próximos passos:"
    echo ""
    echo "1. Configure sua string de conexão MongoDB:"
    echo "   Edit $SCRIPT_DIR/.env"
    echo "   Substitua <db_password> pela senha real"
    echo ""
    echo "2. Use os scripts:"
    echo "   • Gerenciador: ./mongo-manager"
    echo "   • Migrações:   ./migrate status"
    echo "   • Monitor:     ./monitor status"
    echo ""
    echo "3. Ou use diretamente:"
    echo "   • python3 mongo_manager.py"
    echo "   • python3 migrations.py status"
    echo "   • python3 monitoring.py status"
    echo ""
    echo "📖 Documentação:"
    echo "   • mongo_manager.py  - Gerenciamento geral do banco"
    echo "   • migrations.py     - Sistema de migrações"
    echo "   • monitoring.py     - Monitoramento e métricas"
    echo ""
    echo "🔧 Logs e backups serão salvos em:"
    echo "   • Logs: $SCRIPT_DIR/logs/"
    echo "   • Backups: $SCRIPT_DIR/backups/"
    echo ""
}

# Função principal
main() {
    print_status "Iniciando setup dos scripts de banco de dados..."
    
    check_python
    check_pip
    install_dependencies
    create_directories
    setup_permissions
    setup_config
    create_convenience_scripts
    
    if test_installation; then
        show_usage_instructions
    else
        print_error "Setup falhou nos testes finais"
        exit 1
    fi
}

# Executa apenas se for chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
