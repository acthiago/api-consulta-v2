# 🚀 Guia de Setup - API v2.0

## 📋 Pré-requisitos

- **Python 3.11+**
- **Docker & Docker Compose** (recomendado)
- **Git**
- **MongoDB 6.0+** (local ou Docker)
- **Redis 7.0+** (local ou Docker)

## 📁 Estrutura do Projeto

```
api-consulta-v2/
├── src/
│   ├── domain/                    # ✅ Camada de Domínio
│   │   ├── entities/
│   │   │   ├── cliente.py        # Entidade Cliente
│   │   │   ├── pagamento.py      # Entidade Pagamento
│   │   │   └── boleto.py         # Entidade Boleto
│   │   └── value_objects/
│   │       ├── cpf.py            # Value Object CPF
│   │       ├── email.py          # Value Object Email
│   │       └── money.py          # Value Object Money
│   ├── application/               # ✅ Camada de Aplicação
│   │   ├── use_cases/
│   │   │   ├── auth/             # Use Cases de Autenticação
│   │   │   ├── cliente/          # Use Cases de Cliente
│   │   │   ├── pagamento/        # Use Cases de Pagamento
│   │   │   └── boleto/           # Use Cases de Boleto
│   │   ├── dtos/                 # Data Transfer Objects
│   │   └── interfaces/           # Interfaces (Ports)
│   ├── infrastructure/           # 🚧 Camada de Infraestrutura
│   ├── presentation/             # 🚧 Camada de Apresentação
│   ├── config/
│   │   └── settings.py           # Configurações
│   └── main.py                   # Ponto de entrada FastAPI
├── tests/                        # Testes
├── docs/                         # Documentação
├── k8s/                         # Configurações Kubernetes
├── monitoring/                   # Grafana + Prometheus
├── docker-compose.yml           # Docker Compose
├── Dockerfile                   # Container da aplicação
└── requirements.txt             # Dependências Python
```

## ⚙️ Setup Local

### 1. Clone e Configuração Inicial

```bash
# Clone o repositório
git clone <repository-url>
cd api-consulta-v2/api-consulta-v2

# Copie as configurações
cp .env.example .env

# Edite o arquivo .env com suas configurações
nano .env  # ou seu editor preferido
```

### 2. Configuração de Ambiente

Edite o arquivo `.env` com suas configurações:

```env
# Application
APP_NAME=API de Consulta e Cobranças v2
DEBUG=true  # Para desenvolvimento
ENVIRONMENT=development

# Security
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=api_consulta_v2

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_CLIENTE=1800  # 30 minutos
CACHE_TTL_PAGAMENTO=1800  # 30 minutos  
CACHE_TTL_BOLETO=3600  # 1 hora

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60  # Ajuste para desenvolvimento

# CORS (adicione suas URLs)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # json ou text
```

### 3. Instalação de Dependências

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

## 🐳 Setup com Docker (Recomendado)

### 1. Execução Rápida

```bash
# Execute toda a stack
docker-compose up -d

# Acompanhe os logs
docker-compose logs -f api
```

### 2. Serviços Incluídos

- **API**: http://localhost:8000
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 3. Comandos Úteis

```bash
# Parar os serviços
docker-compose down

# Rebuild da API
docker-compose build api

# Ver logs de um serviço específico
docker-compose logs -f mongo

# Executar comandos na API
docker-compose exec api python -m pytest
```

## 🧪 Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Apenas testes unitários
pytest tests/unit/

# Com logs detalhados
pytest -v -s
```

## 🔍 Verificação do Setup

### 1. Health Check

```bash
# Verifique se a API está funcionando
curl http://localhost:8000/health

# Health check detalhado
curl http://localhost:8000/health/detailed
```

### 2. Documentação da API

Acesse: http://localhost:8000/docs

### 3. Métricas

Acesse: http://localhost:8000/metrics

### 4. Teste de Funcionalidade

```bash
# Teste de validação CPF
curl -X GET "http://localhost:8000/clientes/12345678909"

# Deve retornar erro de CPF inválido
curl -X GET "http://localhost:8000/clientes/12345678901"
```

## 🔧 Configurações Avançadas

### 1. Configuração de Banco de Dados

```bash
# Conectar ao MongoDB
docker-compose exec mongo mongosh

# Criar índices
db.clientes.createIndex({ "cpf": 1 }, { unique: true })
db.dividas.createIndex({ "cliente_id": 1 })
db.pagamentos.createIndex({ "status": 1 })
```

### 2. Configuração do Redis

```bash
# Conectar ao Redis
docker-compose exec redis redis-cli

# Verificar configuração
CONFIG GET *
```

### 3. Variáveis de Ambiente Importantes

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DEBUG` | Modo debug | `false` |
| `LOG_LEVEL` | Nível de log | `INFO` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit | `60` |
| `CACHE_TTL_SECONDS` | TTL do cache | `300` |
| `ENABLE_CORS` | Habilitar CORS | `true` |
| `ENABLE_METRICS` | Habilitar métricas | `true` |

## 🐛 Solução de Problemas

### 1. Erro de Conexão com MongoDB

```bash
# Verificar se o MongoDB está rodando
docker-compose ps mongo

# Verificar logs
docker-compose logs mongo

# Restart do serviço
docker-compose restart mongo
```

### 2. Erro de Conexão com Redis

```bash
# Verificar Redis
docker-compose ps redis

# Testar conectividade
docker-compose exec redis redis-cli ping
```

### 3. Dependências Python

```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Verificar versões
pip list | grep fastapi
```

### 4. Permissões (Linux/Mac)

```bash
# Dar permissões corretas
chmod +x scripts/*.sh
sudo chown -R $USER:$USER storage/
```

## 📊 Monitoramento

### 1. Logs da Aplicação

```bash
# Logs em tempo real
docker-compose logs -f api

# Logs estruturados
tail -f logs/api.log | jq
```

### 2. Métricas Prometheus

Acesse http://localhost:9090 e use estas queries:

```promql
# Taxa de requests por minuto
rate(http_requests_total[1m])

# Latência P95
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Erros por minuto
rate(http_requests_total{status=~"5.."}[1m])
```

### 3. Dashboards Grafana

1. Acesse http://localhost:3000
2. Login: admin/admin
3. Importe dashboards da pasta `monitoring/grafana/`

## 🚀 Deploy em Produção

### 1. Variáveis de Ambiente

```env
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=chave-super-secreta-produção
MONGO_URI=mongodb://mongo-cluster:27017
REDIS_URL=redis://redis-cluster:6379
CORS_ORIGINS=["https://app.suaempresa.com"]
```

### 2. Build de Produção

```bash
# Build da imagem
docker build -t api-consulta-v2:latest .

# Tag para registry
docker tag api-consulta-v2:latest registry.suaempresa.com/api-consulta-v2:latest

# Push para registry
docker push registry.suaempresa.com/api-consulta-v2:latest
```

### 3. Health Checks

Configure health checks no seu orquestrador:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 📞 Suporte

- **Logs**: Verifique `logs/api.log`
- **Métricas**: http://localhost:8000/metrics
- **Documentação**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health/detailed

---

**🎉 Sua API v2 está pronta para desenvolvimento!**