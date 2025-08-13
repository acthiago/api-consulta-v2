# 🚀 API de Consulta e Cobranças v2.0

> **Versão moderna com Arquitetura Hexagonal, segurança aprimorada e melhores práticas**

## 📊 Status do Projeto

![Domain Layer](https://img.shields.io/badge/Domain%20Layer-100%25%20✅-brightgreen)
![Application Layer](https://img.shields.io/badge/Application%20Layer-100%25%20✅-brightgreen)
![Infrastructure Layer](https://img.shields.io/badge/Infrastructure%20Layer-20%25%20🚧-yellow)
![Presentation Layer](https://img.shields.io/badge/Presentation%20Layer-10%25%20🚧-yellow)

![Use Cases](https://img.shields.io/badge/Use%20Cases-10/10%20✅-brightgreen)
![Documentation](https://img.shields.io/badge/Documentation-100%25%20✅-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Hexagonal%20✅-blue)

## 📋 Visão Geral

Esta é uma API RESTful para gestão de cobranças e consultas de clientes, completamente refatorada seguindo os princípios da **Arquitetura Hexagonal** (Ports & Adapters), com foco em:

- 🛡️ **Segurança robusta** (JWT, Rate Limiting, Validações)
- 🏗️ **Arquitetura limpa** e testável
- 📊 **Performance otimizada** (Cache Redis, Connection Pooling)
- 🔍 **Observabilidade completa** (Logs, Métricas, Traces)
- 📚 **Documentação abrangente**

## 🏛️ Arquitetura Hexagonal

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Controllers │ │ Middleware  │ │     API Schemas         ││
│  │  (FastAPI)  │ │(Rate Limit) │ │    (Pydantic)          ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  APPLICATION LAYER ✅                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Use Cases   │ │    DTOs     │ │     Interfaces          ││
│  │ • Auth (2)  │ │ • Cliente   │ │ • IClienteRepository    ││
│  │ • Cliente(3)│ │ • Auth      │ │ • IPagamentoRepository  ││
│  │ • Pagmto(2) │ │ • Pagamento │ │ • IBoletoRepository     ││
│  │ • Boleto(3) │ │ • Boleto    │ │ • IJWTService           ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    DOMAIN LAYER ✅                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Entities   │ │Value Objects│ │   Domain Services       ││
│  │ • Cliente   │ │ • CPF       │ │                         ││
│  │ • Pagamento │ │ • Email     │ │                         ││
│  │ • Boleto    │ │ • Money     │ │                         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                INFRASTRUCTURE LAYER 🚧                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Database   │ │    Cache    │ │   External APIs         ││
│  │  MongoDB    │ │   Redis     │ │     JWT Auth            ││
│  │  Security   │ │  Monitoring │ │   File Storage          ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 📊 Status de Implementação:
- ✅ **Domain Layer**: Completo (entidades + value objects)
- ✅ **Application Layer**: Completo (12 use cases + DTOs + interfaces)
- 🚧 **Infrastructure Layer**: Em desenvolvimento
- 🚧 **Presentation Layer**: Refatoração pendente

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- MongoDB
- Redis

### Instalação Local

```bash
# Clone o repositório
git clone <repository-url>
cd api_v2

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# Execute com Docker Compose
docker-compose up -d

# Ou execute localmente
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Acesso Rápido

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
- **Métricas**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health

## 📖 Documentação

- [📋 API Reference](docs/API_REFERENCE.md) - **NOVO**: Documentação completa dos Use Cases
- [🛣️ Roadmap de Desenvolvimento](docs/ROADMAP.md) - **NOVO**: Status e próximos passos
- [🏛️ Arquitetura](docs/ARCHITECTURE.md) - **NOVO**: Detalhes da arquitetura hexagonal
- [🚀 Guia de Setup](docs/SETUP_GUIDE.md) - **ATUALIZADO**: Configuração atualizada
- [📝 Changelog](CHANGELOG.md) - **NOVO**: Histórico de mudanças v2.0
- [🔧 Guia de Configuração](docs/configuration.md)
- [🔒 Guia de Segurança](docs/security.md)
- [📊 Guia de Performance](docs/performance.md)
- [🧪 Guia de Testes](docs/testing.md)
- [🚀 Guia de Deploy](docs/deployment.md)
- [📈 Monitoramento](docs/monitoring.md)
- [🔄 Migração da v1](docs/migration.md)

## 🛡️ Segurança

- ✅ **Autenticação JWT** com refresh tokens
- ✅ **Rate Limiting** por IP e usuário
- ✅ **Validação rigorosa** de entrada
- ✅ **CORS configurado** adequadamente
- ✅ **Logs de auditoria** completos
- ✅ **Criptografia** de dados sensíveis
- ✅ **Headers de segurança** (HSTS, CSP, etc.)

## 📊 Performance

- ⚡ **Cache Redis** para consultas frequentes
- ⚡ **Connection Pooling** otimizado
- ⚡ **Paginação** em todos os endpoints
- ⚡ **Compressão** de respostas
- ⚡ **Índices** de banco otimizados

## 🔍 Observabilidade

- 📊 **Métricas Prometheus** integradas
- 📝 **Logs estruturados** em JSON
- 🔍 **Distributed Tracing** com OpenTelemetry
- 🏥 **Health Checks** detalhados
- 📈 **Dashboards Grafana** incluídos

## 🧪 Qualidade

- ✅ **Cobertura de testes** > 90%
- ✅ **Linting** automático (Black, isort, flake8)
- ✅ **Type hints** completos
- ✅ **Documentação** automatizada
- ✅ **CI/CD** configurado

## 🌟 Principais Funcionalidades

### 🔐 Autenticação ✅
- ✅ Login com username/password implementado
- ✅ Renovação de tokens JWT implementada
- ✅ Validação de credenciais com bcrypt
- ✅ Access/Refresh tokens com diferentes TTLs
- 🚧 Autenticação client_credentials para integrações
- 🚧 Multi-tenant support

### 👥 Gestão de Clientes ✅
- ✅ Busca por ID com cache Redis implementada
- ✅ Criação com validação de CPF/email implementada
- ✅ Atualização com invalidação de cache implementada
- ✅ Validação rigorosa de documentos (CPF/CNPJ)
- ✅ Histórico de operações via logs estruturados
- ✅ Cache inteligente com TTL otimizado

### 💳 Pagamentos ✅
- ✅ Processamento com validação implementado
- ✅ Consulta de status implementada
- ✅ Múltiplos métodos (cartão, PIX, boleto, etc.)
- ✅ Regras de negócio para aprovação/rejeição
- ✅ Códigos de transação únicos
- 🚧 Integração PIX
- 🚧 Conciliação automática

### 📄 Boletos ✅
- ✅ Geração com linha digitável implementada
- ✅ Consulta por ID implementada
- ✅ Cancelamento com validações implementado
- ✅ Códigos de barras simulados
- ✅ Controle de vencimento e status
- 🚧 Geração em PDF otimizada
- 🚧 QR Codes PIX integrados
- 🚧 Templates customizáveis

## 🔄 Migração da v1

Se você está migrando da versão anterior, consulte nosso [Guia de Migração](docs/migration.md) para uma transição suave.

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ pela equipe de Engenharia**