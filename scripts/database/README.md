# MongoDB Cloud Database Management

Este diretório contém scripts para gerenciar, monitorar e organizar o banco de dados MongoDB na cloud (MongoDB Atlas), integrado com a infraestrutura de produção VPS.

## 🏗️ **Arquitetura Atual**

### **🚀 Produção VPS (69.62.103.163):**
- **API FastAPI**: `https://api.thiagoac.com`
- **MongoDB Atlas**: Cloud database com SSL
- **Traefik Gateway**: Roteamento e SSL automático
- **Monitoring**: Grafana + Prometheus + Redis
- **CI/CD**: GitHub Actions com deploy automatizado

### **🌐 URLs de Acesso:**
- 🚀 **API Docs**: `https://api.thiagoac.com/docs`
- 📊 **Grafana**: `https://monitor.thiagoac.com`  
- 📈 **Prometheus**: `https://monitor.thiagoac.com/prometheus`
- 🌐 **Traefik**: `https://gateway.thiagoac.com`

## 📋 Estrutura dos Scripts

```
scripts/database/
├── mongo_manager.py       # Gerenciador principal do banco
├── mongo-manager          # Script de conveniência para mongo_manager.py
├── migrations.py          # Sistema de migrações
├── migrate               # Script de conveniência para migrations.py
├── monitoring.py         # Monitoramento e métricas
├── monitor              # Script de conveniência para monitoring.py
├── generate_test_data.py # Gerador de dados de teste
├── generate-data        # Script de conveniência para generate_test_data.py
├── setup.sh            # Script de configuração inicial
├── .env.example        # Exemplo de configuração
├── .env                # Configuração local (não commitado)
├── README.md           # Esta documentação
├── backups/            # Backups do banco
├── logs/              # Logs dos scripts
├── config/            # Configurações
├── venv/              # Ambiente virtual Python
└── __pycache__/       # Cache Python
```

## 🚀 Configuração por Ambiente

### **💻 Desenvolvimento Local:**

#### 1. Execute o Setup
```bash
cd scripts/database/
chmod +x setup.sh
./setup.sh
```

#### 2. Configure para MongoDB Local
```bash
# .env para desenvolvimento
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=api_consulta_v2
```

### **🌐 Produção VPS:**

#### 1. Configuração Automática via CI/CD
Os scripts são executados automaticamente durante o deploy via GitHub Actions.

#### 2. Configuração Manual (se necessário)
```bash
# .env.vps para produção
MONGO_URI=mongodb+srv://user:pass@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=api_consulta_v2_prod
```

## 🔧 Setup Local Detalhado

### 1. Execute o Setup Local
```bash
cd scripts/database/
chmod +x setup.sh
./setup.sh
```

Este script irá:
- ✅ Verificar dependências Python
- 📦 Instalar pymongo e outras bibliotecas
- 📁 Criar estrutura de diretórios
- 🔧 Configurar permissões
- 📝 Criar arquivo .env para desenvolvimento

### 2. Configure a Conexão Local
```bash
nano .env
```

Substitua `<db_password>` pela senha real do seu MongoDB Atlas:
```bash
# Para desenvolvimento local
MONGO_URI=mongodb://localhost:27017

# Para produção VPS (MongoDB Atlas)
MONGO_URI=mongodb+srv://seu_usuario:sua_senha@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=api_consulta_v2_prod
```

> **⚠️ Importante**: Em produção (VPS), use sempre MongoDB Atlas com SSL e autenticação.

## 📚 Scripts Disponíveis

### 🛠️ mongo_manager.py - Gerenciador Principal

O script principal para organização e manutenção do banco.

#### Uso Interativo:
```bash
python3 mongo_manager.py
```

#### Funcionalidades:
1. **Ver informações do banco** - Estatísticas gerais
2. **Criar/Atualizar estrutura** - Coleções e índices
3. **Otimizar banco** - Reindexação e limpeza
4. **Fazer backup** - Exporta dados em JSON
5. **Limpar dados** - Remove duplicados e órfãos

#### Exemplo de Uso:
```bash
# Modo interativo
./mongo-manager

# Ou diretamente
python3 mongo_manager.py
```

### 🔄 migrations.py - Sistema de Migrações

Gerencia versionamento e evolução do schema do banco.

#### Comandos Disponíveis:
```bash
# Ver status das migrações
python3 migrations.py status

# Aplicar todas as migrações pendentes
python3 migrations.py up

# Aplicar até uma versão específica
python3 migrations.py up 003

# Reverter até uma versão
python3 migrations.py down 002

# Reverter migração específica
python3 migrations.py rollback 003
```

#### Migrações Incluídas:
- **001** - Estrutura inicial (clientes)
- **002** - Coleção de pagamentos
- **003** - Status "bloqueado" para clientes
- **004** - Coleção de boletos
- **005** - Usuários e auditoria

#### Exemplo:
```bash
# Script de conveniência
./migrate status
./migrate up

# Ou diretamente
python3 migrations.py status
python3 migrations.py up
```

### 📊 monitoring.py - Monitoramento e Métricas

Monitora performance, consultas lentas e uso de recursos.

#### Comandos Disponíveis:
```bash
# Status atual do banco
python3 monitoring.py status

# Métricas detalhadas (JSON)
python3 monitoring.py metrics

# Consultas lentas (últimos 5 minutos)
python3 monitoring.py slow-queries

# Consultas lentas (últimos 30 minutos)
python3 monitoring.py slow-queries 30

# Uso de índices
python3 monitoring.py index-usage

# Relatório completo de performance
python3 monitoring.py report

# Monitoramento em tempo real
python3 monitoring.py monitor

# Monitor personalizado (30s por 5 minutos)
python3 monitoring.py monitor 30 5
```

#### Exemplo de Monitoramento:
```bash
# Script de conveniência
./monitor status
./monitor report

# Monitoramento em tempo real
./monitor monitor 15 10  # A cada 15s por 10 minutos

# Ou diretamente
python3 monitoring.py report
```

```

### 🛡️ Validações e Constraints:

```
                          VALIDAÇÕES ATIVAS
    ┌─────────────────────────────────────────────────────────┐
    │                    CLIENTES                             │
    ├─────────────────────────────────────────────────────────┤
    │ • CPF: Exatamente 11 dígitos numéricos                 │
    │ • Email: Formato de email válido                       │
    │ • Nome: Mínimo 2 caracteres                           │
    │ • Status: Enum [ativo, inativo, bloqueado]            │
    │ • CPF e Email: Únicos no banco                        │
    └─────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────┐
    │                   PAGAMENTOS                            │
    ├─────────────────────────────────────────────────────────┤
    │ • Cliente_ID: Deve existir na coleção clientes        │
    │ • Valor: Tipo decimal obrigatório                     │
    │ • Status: Enum [pendente, pago, cancelado, vencido]   │
    │ • Tipo: Enum [boleto, pix, cartao]                    │
    └─────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────┐
    │                     BOLETOS                             │
    ├─────────────────────────────────────────────────────────┤
    │ • Número: Único no banco                               │
    │ • Cliente_ID: Deve existir na coleção clientes        │
    │ • Pagamento_ID: Deve existir na coleção pagamentos    │
    │ • Status: Enum [ativo, pago, cancelado, vencido]      │
    └─────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────┐
    │                    USUARIOS                             │
    ├─────────────────────────────────────────────────────────┤
    │ • Username: Mínimo 3 caracteres, único                │
    │ • Email: Formato válido, único                         │
    │ • Role: Enum [admin, user, readonly]                  │
    │ • Status: Enum [ativo, inativo, bloqueado]            │
    └─────────────────────────────────────────────────────────┘
```

#### ⚠️ **Validações em Tempo Real:**
- ✅ **Schema Validation** ativo em todas as coleções
- ✅ **Unique Constraints** em CPF, email, username
- ✅ **Foreign Key Validation** via aplicação
- ✅ **Data Type Enforcement** automático
- ✅ **Enum Validation** para campos de status

## 🏗️ Estrutura do Banco de Dados

### 📊 Diagrama da Estrutura:

```
                        MongoDB Atlas - api_consulta_v2
                     ╔══════════════════════════════════════╗
                     ║          CLOUD DATABASE              ║
                     ╚══════════════════════════════════════╝
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
        ▼                               ▼                               ▼
┌─────────────┐                ┌─────────────┐                ┌─────────────┐
│   CLIENTES  │                │ PAGAMENTOS  │                │   BOLETOS   │
├─────────────┤                ├─────────────┤                ├─────────────┤
│ _id (PK)    │◄──────────────┐│ _id (PK)    │◄──────────────┐│ _id (PK)    │
│ cpf (UK)    │               ││ cliente_id  │               ││ numero (UK) │
│ nome        │               ││ valor       │               ││ cliente_id  │
│ email (UK)  │               ││ status      │               ││ pagamento_id│
│ telefone    │               ││ tipo_pagto  │               ││ valor       │
│ endereco    │               ││ data_venc   │               ││ data_venc   │
│ status      │               ││ data_pagto  │               ││ linha_digit │
│ created_at  │               ││ created_at  │               ││ cod_barras  │
│ updated_at  │               ││ updated_at  │               ││ status      │
└─────────────┘               │└─────────────┘               ││ created_at  │
                              │                              ││ updated_at  │
                              │                              │└─────────────┘
                              │                              │
┌─────────────┐               │                              │
│  USUARIOS   │               │                              │
├─────────────┤               │                              │
│ _id (PK)    │               │                              │
│ username(UK)│               │                              │
│ email (UK)  │               │                              │
│ password_h  │               │                              │
│ nome        │               │                              │
│ role        │               │                              │
│ status      │               │                              │
│ last_login  │               │                              │
│ created_at  │               │                              │
│ updated_at  │               │                              │
└─────────────┘               │                              │
                              │                              │
┌─────────────┐               │                              │
│  AUDITORIA  │               │                              │
├─────────────┤               │                              │
│ _id (PK)    │               │                              │
│ usuario_id  │◄──────────────┘                              │
│ acao        │                                              │
│ recurso     │                                              │
│ detalhes    │                                              │
│ ip_address  │                                              │
│ user_agent  │                                              │
│ created_at  │                                              │
└─────────────┘                                              │
                                                             │
┌─────────────┐                                              │
│ MIGRATIONS  │                                              │
├─────────────┤                                              │
│ _id (PK)    │                                              │
│ version     │                                              │
│ description │                                              │
│ applied_at  │                                              │
└─────────────┘                                              │
                                                             │
                              ┌──────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │    RELACIONAMENTOS │
                    ├───────────────────┤
                    │ 1 Cliente : N Pag │
                    │ 1 Pagto : N Bolet │
                    │ 1 User : N Audit  │
                    └───────────────────┘

LEGENDA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PK = Primary Key (_id)          UK = Unique Key (índice único)
◄─ = Foreign Key (relacionamento)     N = Muitos (1:N)
```

### 🔍 Índices Otimizados:

```
CLIENTES                    PAGAMENTOS                 BOLETOS
├── _id_ (PK)              ├── _id_ (PK)              ├── _id_ (PK)
├── cpf_1 (UNIQUE)         ├── cliente_id_1          ├── numero_boleto_1 (UNIQUE)
├── email_1 (UNIQUE)       ├── status_1              ├── cliente_id_1
├── status_1               ├── created_at_1          ├── status_1
└── created_at_1           └── data_vencimento_1     └── data_vencimento_1

USUARIOS                    AUDITORIA
├── _id_ (PK)              ├── _id_ (PK)
├── username_1 (UNIQUE)    ├── usuario_id_1
├── email_1 (UNIQUE)       ├── acao_1
├── role_1                 ├── created_at_1
└── status_1               └── recurso_1
```

### Coleções Criadas:

#### 👥 clientes
- **Função**: Dados dos clientes
- **Índices**: CPF (único), email (único), status, created_at
- **Validação**: CPF (11 dígitos), email válido, status enum

#### 💰 pagamentos
- **Função**: Histórico de pagamentos
- **Índices**: cliente_id, status, data_vencimento, valor
- **Relacionamento**: cliente_id → clientes._id

#### 🧾 boletos
- **Função**: Boletos gerados
- **Índices**: numero_boleto (único), cliente_id, pagamento_id
- **Relacionamento**: pagamento_id → pagamentos._id

#### 👤 usuarios
- **Função**: Usuários do sistema
- **Índices**: username (único), email (único), role, status
- **Roles**: admin, user, readonly

#### 📝 auditoria
- **Função**: Log de auditoria
- **Índices**: usuario_id, acao, created_at, recurso
- **Função**: Rastreamento de todas as operações

### 🔄 Fluxo de Dados e Operações:

```
                          ARQUITETURA DE PRODUÇÃO VPS
    ┌─────────────────────────────────────────────────────────────────────┐
    │                          CLOUDFLARE DNS                             │
    │   api.thiagoac.com  │  monitor.thiagoac.com  │  gateway.thiagoac.com│
    └──────────────┬──────────────────┬──────────────────┬───────────────┘
                   │                  │                  │
                   │ (SSL/HTTPS)      │ (SSL/HTTPS)      │ (SSL/HTTPS)
                   │                  │                  │
    ┌──────────────▼──────────────────▼──────────────────▼───────────────┐
    │                        VPS (69.62.103.163)                         │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │                  TRAEFIK GATEWAY v3.0                      │   │
    │  │            Auto-discovery │ Rate Limiting │ Metrics        │   │
    │  └─────────────────────┬───────────────────┬─────────────────────┘   │
    │                        │                   │                         │
    │    ┌───────────────────▼─────┐   ┌─────────▼─────────────────────┐   │
    │    │     FastAPI             │   │      MONITORING STACK        │   │
    │    │  api.thiagoac.com       │   │   monitor.thiagoac.com       │   │
    │    │ ┌─────────────────────┐ │   │ ┌─────────────────────────┐   │   │
    │    │ │   MongoDB Atlas     │ │   │ │      Grafana            │   │   │
    │    │ │   (Cloud DB)        │◄┼───┼─┤      Dashboards         │   │   │
    │    │ │                     │ │   │ └─────────────────────────┘   │   │
    │    │ └─────────────────────┘ │   │ ┌─────────────────────────┐   │   │
    │    │ ┌─────────────────────┐ │   │ │      Prometheus         │   │   │
    │    │ │      Redis          │ │   │ │   /prometheus endpoint  │   │   │
    │    │ │      Cache          │ │   │ └─────────────────────────┘   │   │
    │    │ └─────────────────────┘ │   │ ┌─────────────────────────┐   │   │
    │    └─────────────────────────┘   │ │      Redis              │   │   │
    │                                  │ │      Metrics Cache      │   │   │
    │                                  │ └─────────────────────────┘   │   │
    │                                  └───────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────────┘
                                       │
                   ┌───────────────────▼────────────────────┐
                   │            FLUXO DE DADOS              │
                   └────────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│   API REQUESTS  │          │   AUDIT LOG     │          │   MONITORING    │
│ ┌─────────────┐ │          │ ┌─────────────┐ │          │ ┌─────────────┐ │
│ │ CREATE      │ │          │ │ All Actions │ │          │ │ Metrics     │ │
│ │ READ        │ │ ────────►│ │ Users       │ │ ────────►│ │ Dashboards  │ │
│ │ UPDATE      │ │          │ │ Operations  │ │          │ │ Alerts      │ │
│ │ DELETE      │ │          │ └─────────────┘ │          │ └─────────────┘ │
│ └─────────────┘ │          └─────────────────┘          └─────────────────┘
└─────────────────┘
```

                          RELACIONAMENTOS
                    ┌─────────────────────────┐
                    │  1 Cliente              │
                    │     ↓                   │
                    │  N Pagamentos           │
                    │     ↓                   │
                    │  N Boletos              │
                    └─────────────────────────┘
```

### 📈 Status e Health Score:

```
                          MONITORAMENTO
    ┌─────────────────────────────────────────────────────────┐
    │                  HEALTH SCORE: 100                     │
    │  ████████████████████████████████████████████████████  │
    │                    EXCELENTE                           │
    └─────────────────────────────────────────────────────────┘
    
    MÉTRICAS ATUAIS:
    ┌─────────────┬─────────────┬─────────────┬─────────────┐
    │ DOCUMENTOS  │  COLEÇÕES   │   ÍNDICES   │  CONEXÕES   │
    │      5      │      6      │     19      │  Estáveis   │
    └─────────────┴─────────────┴─────────────┴─────────────┘
    
    STATUS DAS COLEÇÕES:
    ┌─────────────┬─────────────┬─────────────┬─────────────┐
    │   clientes  │ pagamentos  │   boletos   │  usuarios   │
    │      ✅     │      ✅     │      ✅     │      ✅     │
    │ 0 documentos│ 0 documentos│ 0 documentos│ 0 documentos│
    │  3 índices  │  4 índices  │  4 índices  │  3 índices  │
    └─────────────┴─────────────┴─────────────┴─────────────┘
    
    ┌─────────────┬─────────────┐
    │  auditoria  │ migrations  │
    │      ✅     │      ✅     │
    │ 0 documentos│ 5 documentos│
    │  4 índices  │  1 índice   │
    └─────────────┴─────────────┘
```

## 📋 Casos de Uso Comuns

### 🆕 Setup Inicial Completo
```bash
# 1. Configurar ambiente
./setup.sh

# 2. Editar .env com credenciais reais
nano .env

# 3. Aplicar migrações
./migrate up

# 4. Verificar estrutura
./mongo-manager
# Escolher opção 1 (Ver informações)
```

### 🔍 Análise de Performance
```bash
# Relatório completo
./monitor report

# Consultas lentas da última hora
./monitor slow-queries 60

# Monitoramento em tempo real
./monitor monitor 30 15
```

### 💾 Backup e Manutenção
```bash
# Backup completo
./mongo-manager
# Escolher opção 4 (Fazer backup)

# Limpeza e otimização
./mongo-manager
# Escolher opção 5 (Limpar dados)
# Depois opção 3 (Otimizar)
```

### 🔄 Atualização de Schema
```bash
# Ver status atual
./migrate status

# Aplicar novas migrações
./migrate up

# Em caso de problema, reverter
./migrate down 004
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente (.env):
```bash
# Conexão
MONGO_URI=sua_string_de_conexao
DATABASE_NAME=api_consulta_v2

# Monitoramento
MONITOR_INTERVAL_SECONDS=30
SLOW_QUERY_THRESHOLD_MS=100

# Backup
BACKUP_DIRECTORY=./backups
BACKUP_RETENTION_DAYS=30

# Auditoria
AUDIT_ENABLED=true
CLEANUP_OLD_AUDIT_DAYS=90
```

### 📊 Métricas Monitoradas:
- **Performance**: Tempo de resposta, throughput
- **Recursos**: Uso de memória, conexões ativas
- **Consultas**: Queries lentas, uso de índices
- **Dados**: Tamanho das coleções, contagem de documentos
- **Health Score**: Score de 0-100 baseado em métricas

### 🎯 Health Score Calculation:
- **100 pontos** base
- **-30 pontos** se >50 consultas lentas
- **-5 pontos** por coleção sem índices adequados
- **-10 pontos** por coleção com documentos >1MB
- **+5 pontos** por uso adequado de índices

## 🚨 Troubleshooting

### Erro de Conexão:
```bash
# Verifique a string de conexão
echo $MONGO_URI

# Teste de conectividade
python3 -c "
import pymongo
client = pymongo.MongoClient('sua_string_aqui')
client.admin.command('ping')
print('Conexão OK')
"
```

### Dependências Ausentes:
```bash
# Reinstalar dependências
pip3 install pymongo python-dotenv click tabulate colorama --user

# Ou executar setup novamente
./setup.sh
```

### Permissões:
```bash
# Corrigir permissões
chmod +x *.py *.sh
chmod +x mongo-manager migrate monitor
```

## 📈 Exemplos de Output

### Status do Banco:
```
📊 Status do Banco: api_consulta_v2
🕐 Timestamp: 2024-01-20 10:30:00
📄 Documentos: 15,234
📁 Coleções: 5
💾 Tamanho: 45.67 MB
📇 Índices: 12
🔗 Conexões: 3
```

### Relatório de Performance:
```json
{
  "health_score": 85,
  "metrics": {
    "total_documents": 15234,
    "total_size_mb": 45.67,
    "connections_current": 3
  },
  "recommendations": [
    "⚠️ Coleção 'logs' tem 5000 documentos mas apenas 1 índice(s)"
  ]
}
```

## 🔗 Integração com a API

Estes scripts podem ser integrados ao ciclo de vida da API FastAPI:

### 🚀 **Ambiente de Produção VPS:**
```bash
# Stack completo com Traefik Gateway
make docker-vps

# URLs da API em produção:
# 🚀 API: https://api.thiagoac.com
# 📊 Grafana: https://monitor.thiagoac.com  
# 📈 Prometheus: https://monitor.thiagoac.com/prometheus
# 🌐 Traefik: https://gateway.thiagoac.com
```

### 🔄 **Pipeline CI/CD:**
```bash
# Em GitHub Actions (.github/workflows/python-app.yml)
./migrate up                    # Aplicar migrações antes do deploy
./monitor status               # Verificar saúde do banco
./mongo-manager                # Backup automático
```

### 📊 **Monitoramento Integrado:**
```bash
# Monitoramento contínuo (24h)
./monitor monitor 60 1440      

# Integração com Prometheus (VPS)
# Métricas disponíveis em: https://monitor.thiagoac.com/prometheus
```

### 🔧 **Configuração por Ambiente:**
```bash
# Desenvolvimento (.env local)
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=api_consulta_v2

# Produção VPS (.env.vps)
MONGO_URI=mongodb+srv://user:pass@cluster0.wjwnv.mongodb.net/
DATABASE_NAME=api_consulta_v2_prod
```

## 📞 Suporte

### 🔍 **Troubleshooting Local:**
1. Verifique os logs em `logs/`
2. Execute `./setup.sh` novamente
3. Confirme se MongoDB local está rodando: `brew services list | grep mongodb`
4. Verifique as variáveis de ambiente no `.env`

### 🌐 **Troubleshooting Produção:**
1. **Monitoramento**: Acesse `https://monitor.thiagoac.com`
2. **Logs da API**: `docker logs api-consulta-v2-production`
3. **Status do banco**: Execute `./monitor status` via SSH na VPS
4. **Métricas**: Consulte Prometheus em `https://monitor.thiagoac.com/prometheus`

### 🚨 **Contatos de Emergência:**
- **VPS**: 69.62.103.163 (SSH com chave configurada)
- **MongoDB Atlas**: Console web oficial
- **Cloudflare**: Dashboard para gestão de DNS/SSL
- **GitHub Actions**: Logs de CI/CD no repositório

### 📚 **Documentação Adicional:**
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Traefik v3.0 Documentation](https://doc.traefik.io/traefik/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
