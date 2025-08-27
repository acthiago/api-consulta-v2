# MongoDB Cloud Database Management

Este diretório contém scripts para gerenciar, monitorar e organizar o banco de dados MongoDB na cloud (MongoDB Atlas).

## 📋 Estrutura dos Scripts

```
scripts/database/
├── mongo_manager.py    # Gerenciador principal do banco
├── migrations.py       # Sistema de migrações
├── monitoring.py       # Monitoramento e métricas
├── setup.sh           # Script de configuração
├── .env.example       # Exemplo de configuração
├── README.md          # Esta documentação
└── logs/              # Logs dos scripts
└── backups/           # Backups do banco
└── config/            # Configurações
```

## 🚀 Configuração Inicial

### 1. Execute o Setup
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
- 📝 Criar arquivo .env

### 2. Configure a Conexão
Edite o arquivo `.env` e configure sua string de conexão:

```bash
nano .env
```

Substitua `<db_password>` pela senha real do seu MongoDB Atlas:
```
MONGO_URI=mongodb+srv://thiago:SUA_SENHA_AQUI@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

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
                          FLUXO DE OPERAÇÕES
                     ┌─────────────────────────────┐
                     │       API REQUESTS          │
                     └─────────────┬───────────────┘
                                   │
                     ┌─────────────▼───────────────┐
                     │     AUTHENTICATION          │
                     │    (Collection: usuarios)   │
                     └─────────────┬───────────────┘
                                   │
                     ┌─────────────▼───────────────┐
                     │       AUDIT LOG             │
                     │   (Collection: auditoria)   │ ◄─── Log de todas as operações
                     └─────────────┬───────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
               ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   GESTÃO DE     │ │   GESTÃO DE     │ │   GESTÃO DE     │
    │    CLIENTES     │ │   PAGAMENTOS    │ │    BOLETOS      │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
             │                   │                   │
             │                   │                   │
        ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
        │CREATE   │         │CREATE   │         │CREATE   │
        │READ     │         │READ     │         │READ     │
        │UPDATE   │         │UPDATE   │         │UPDATE   │
        │DELETE   │         │DELETE   │         │DELETE   │
        └─────────┘         └─────────┘         └─────────┘

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

Estes scripts podem ser integrados ao ciclo de vida da API:

```bash
# Em CI/CD
./migrate up                    # Aplicar migrações
./monitor status               # Verificar saúde
./mongo-manager                # Backup automático

# Monitoramento contínuo
./monitor monitor 60 1440      # 24h de monitoramento
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/`
2. Execute `./setup.sh` novamente
3. Consulte a documentação do MongoDB Atlas
4. Verifique as variáveis de ambiente no `.env`
