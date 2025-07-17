# 🚀 API de Consulta e Cobranças v2.0

> **Versão moderna com Arquitetura Hexagonal, segurança aprimorada e melhores práticas**

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
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  APPLICATION LAYER                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Use Cases   │ │    DTOs     │ │      Interfaces         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    DOMAIN LAYER                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Entities   │ │Value Objects│ │   Domain Services       ││
│  │             │ │             │ │   Repository Ports      ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                INFRASTRUCTURE LAYER                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Database   │ │    Cache    │ │   External APIs         ││
│  │  Security   │ │  Monitoring │ │   File Storage          ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

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

- [📋 Guia de Arquitetura](docs/architecture.md)
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

### 🔐 Autenticação
- Login com username/password
- Autenticação client_credentials para integrações
- Refresh tokens automáticos
- Multi-tenant support

### 👥 Gestão de Clientes
- Consulta por CPF/CNPJ
- Validação de documentos
- Histórico completo
- Cache inteligente

### 💳 Pagamentos
- Múltiplas formas de pagamento
- Integração PIX
- Boletos com QR Code
- Conciliação automática

### 📄 Boletos
- Geração em PDF otimizada
- QR Codes PIX integrados
- Templates customizáveis
- Armazenamento seguro

## 🔄 Migração da v1

Se você está migrando da versão anterior, consulte nosso [Guia de Migração](docs/migration.md) para uma transição suave.

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

- 📧 Email: support@example.com
- 💬 Slack: #api-support
- 📖 Wiki: [Confluence](https://wiki.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/org/repo/issues)

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ pela equipe de Engenharia**