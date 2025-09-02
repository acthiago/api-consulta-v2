# 🚀 API de Consulta e Cobranças v2.0

> **Sistema completo de gestão financeira com negociação de dívidas e cancelamento de boletos**

## 📊 Status do Projeto

![API Endpoints](https://img.shields.io/badge/API%20Endpoints-100%25%20✅-brightgreen)
![Authentication](https://img.shields.io/badge/Authentication-OAuth2%20✅-brightgreen)
![Database](https://img.shields.io/badge/Database-MongoDB%20✅-brightgreen)
![Business Logic](https://img.shields.io/badge/Business%20Logic-100%25%20✅-brightgreen)

![Financial Operations](https://img.shields.io/badge/Financial%20Operations-100%25%20✅-brightgreen)
![Documentation](https://img.shields.io/badge/Documentation-Swagger%20✅-brightgreen)
![Production Ready](https://img.shields.io/badge/Production%20Ready-✅-blue)

## 📋 Visão Geral

Esta é uma API RESTful completa para gestão de cobranças e consultas de clientes, com foco em:

- 🛡️ **Segurança robusta** (OAuth2, Rate Limiting, Validações)
- 💰 **Operações financeiras completas** (Dívidas, Boletos, Cancelamentos)
- 🔄 **Regras de negócio avançadas** (Parcelamento, Negociação, Histórico)
- 📊 **Auditoria completa** (Logs estruturados, Rastreabilidade)
- 🔍 **Observabilidade** (Métricas Prometheus, Health Checks)
- 📚 **Documentação interativa** (Swagger UI)

## 💼 Funcionalidades Implementadas

### � Autenticação e Segurança
- **OAuth2 Password Flow** com JWT tokens
- **Rate Limiting** personalizado por endpoint
- **Validação de CPF** com algoritmo oficial
- **Logs estruturados** para auditoria

### 👥 Gestão de Clientes
- **Consulta por CPF** com validação completa
- **Dados completos** (nome, telefone, endereço, score)
- **Histórico de relacionamento** com a empresa

### 💳 Gestão de Dívidas
- **Consulta de dívidas** por cliente
- **Tipos diversos**: Crediário, Cartão, Empréstimo, Financiamento
- **Status inteligente**: Ativo, Vencido, Inadimplente, Negociado, Pago
- **Cálculo automático** de juros e multas

### 🧾 Sistema de Boletos
- **Geração de boletos** com múltiplas dívidas
- **Parcelamento** até 5x com valor mínimo R$ 50,00
- **Cancelamento** com restauração de dívidas
- **Códigos bancários** reais (linha digitável, código de barras)
- **Validações de negócio** robustas

### 📊 Auditoria e Histórico
- **Preservação completa** do histórico de negociações
- **Rastreamento de usuários** responsáveis pelas operações
- **Log de todas as transações** financeiras
- **Métricas de performance** e uso

## 🏛️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (FastAPI)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Controllers │ │ Middleware  │ │     API Schemas         ││
│  │  (OAuth2)   │ │(Rate Limit) │ │    (Pydantic)          ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  BUSINESS LOGIC                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Financial  │ │ Validation  │ │     Domain Rules        ││
│  │ Operations  │ │   Engine    │ │   • Parcelamento        ││
│  │• Boletos    │ │• CPF Check  │ │   • Status Logic        ││
│  │• Dívidas    │ │• Business   │ │   • Audit Trail         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                 DATABASE LAYER                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  MongoDB    │ │ Collections │ │    ACID Transactions    ││
│  │  Atlas      │ │• clientes   │ │                         ││
│  │  Cloud      │ │• dividas    │ │                         ││
│  │             │ │• boletos    │ │                         ││
│  │             │ │• auditoria  │ │                         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- MongoDB Atlas (ou local)

### Instalação e Execução

```bash
# Clone o repositório
git clone <repository-url>
cd api-consulta-v2

# Execute com Docker Compose
docker-compose up -d

# Acesse a documentação
http://localhost:8000/docs
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Acesso Rápido

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
```

### 🔗 Autenticação Necessária
```bash
# Obter token de acesso
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## 🌟 Endpoints Implementados

### 🔐 Autenticação
```bash
# Login OAuth2
POST /auth/token
```

### 👥 Gestão de Clientes
```bash
# Consultar cliente por CPF
GET /api/v1/cliente/{cpf}

# Listar dívidas do cliente
GET /api/v1/cliente/{cpf}/dividas

# Listar boletos do cliente
GET /api/v1/cliente/{cpf}/boletos
```

### 💳 Sistema de Dívidas e Boletos
```bash
# Gerar boleto com múltiplas dívidas
POST /api/v1/boleto/gerar
{
  "cliente_cpf": "123.456.789-00",
  "dividas_ids": ["id1", "id2"],
  "parcelas": 3
}

# Cancelar boleto e restaurar dívidas
POST /api/v1/boleto/{boleto_id}/cancelar
```

### 📊 Monitoramento
```bash
# Health check
GET /health

# Métricas Prometheus
GET /metrics
```

## 📖 Documentação

- [📋 API Reference](docs/API_REFERENCE.md) - Documentação completa dos endpoints
- [🛣️ Roadmap de Desenvolvimento](docs/ROADMAP.md) - Status e próximos passos
- [🏛️ Arquitetura](docs/ARCHITECTURE.md) - Detalhes da arquitetura
- [🚀 Guia de Setup](docs/SETUP_GUIDE.md) - Configuração completa
- [📝 Changelog](CHANGELOG.md) - Histórico de mudanças v2.0
- [🔧 MongoDB Config](docs/MONGO_CONFIG.md) - Configuração do banco de dados

## 🛡️ Segurança

- ✅ **Autenticação OAuth2** com JWT tokens
- ✅ **Rate Limiting** personalizado por endpoint
- ✅ **Validação rigorosa** de CPF e dados
- ✅ **CORS configurado** adequadamente
- ✅ **Logs de auditoria** completos com structured logging
- ✅ **Headers de segurança** implementados

## 📊 Performance

- ⚡ **MongoDB Atlas** com índices otimizados
- ⚡ **Connection Pooling** configurado
- ⚡ **Validações eficientes** com Pydantic
- ⚡ **Compressão GZip** habilitada
- ⚡ **Rate limiting** inteligente

## 🔍 Observabilidade

- 📊 **Métricas Prometheus** para monitoramento
- 📝 **Logs estruturados** em JSON com contexto
- 🏥 **Health Checks** detalhados
- 📈 **Request/Response tracking** completo
- 🔍 **Error tracking** com stack traces

## 💼 Regras de Negócio Implementadas

### 💰 Sistema Financeiro
- ✅ **Parcelamento**: Máximo 5 parcelas por boleto
- ✅ **Valor mínimo**: R$ 50,00 por parcela
- ✅ **Status de dívidas**: Ativo → Vencido → Inadimplente
- ✅ **Juros e multas**: Cálculo automático baseado no tempo
- ✅ **Negociação**: Boleto bloqueia re-negociação das dívidas

### 🔄 Ciclo de Vida do Boleto
- ✅ **Geração**: Múltiplas dívidas em um boleto
- ✅ **Validação**: Verifica se dívidas podem ser negociadas
- ✅ **Cancelamento**: Restaura dívidas ao estado original
- ✅ **Auditoria**: Preserva histórico completo de operações

## 🌟 Principais Funcionalidades

### 🔐 Autenticação ✅
- ✅ Login OAuth2 Password Flow implementado
- ✅ JWT tokens com expiração configurável
- ✅ Validação de credenciais segura
- ✅ Rate limiting por usuário

### 👥 Gestão de Clientes ✅
- ✅ Consulta por CPF com validação algorítmica
- ✅ Dados completos (nome, telefone, endereço, score)
- ✅ Histórico de relacionamento
- ✅ Integração com MongoDB Atlas

### 💳 Sistema de Dívidas ✅
- ✅ Múltiplos tipos: Crediário, Cartão, Empréstimo, Financiamento
- ✅ Status inteligente baseado em vencimento
- ✅ Cálculo automático de juros (2% a.m.) e multa (2%)
- ✅ Agrupamento por cliente

### 📄 Sistema de Boletos ✅
- ✅ Geração com múltiplas dívidas
- ✅ Parcelamento com validação de regras
- ✅ Códigos bancários reais (linha digitável, código de barras)
- ✅ Cancelamento com restauração de dívidas
- ✅ Histórico preservado para auditoria
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

## �️ Informações de Acesso

### Log de execução

O gerador fornece:
- ✅ **Status em tempo real** da geração
- 📊 **Estatísticas detalhadas** dos dados criados
- 💡 **Informações de acesso** para testes
- 🧹 **Limpeza automática** de dados anteriores

### Exemplo de saída
```
🎉 Massa de dados gerada com sucesso!
📊 Estatísticas dos dados gerados:
📁 clientes: 100 documentos
   Status: {'ativo': 35, 'bloqueado': 34, 'inativo': 31}
📁 pagamentos: 500 documentos
   Status: {'pago': 137, 'cancelado': 200, 'pendente': 163}
   Valor total: R$ 494,988.84
📁 boletos: 300 documentos
📁 usuários: 8 documentos
📁 auditoria: 1,000 documentos

💡 Dados de acesso gerados:
   • Usuário admin: admin@apiconsulta.com
   • Senha padrão: admin123
```

---

**Desenvolvido com ❤️ pela equipe de Engenharia**