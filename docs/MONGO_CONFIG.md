# Configuração de String de Conexão MongoDB - API Consulta V2

Este documento lista todos os arquivos onde a string de conexão MongoDB deve ser configurada.

## 🔧 Arquivos de Configuração Principal

### 1. `.env` (Local/Desenvolvimento)
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/.env`
**Uso**: Ambiente de desenvolvimento local
```bash
MONGO_URI=mongodb+srv://thiago:SUA_SENHA@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGO_DB_NAME=api_consulta_v2
```

### 2. `.env.example` (Template)
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/.env.example`
**Uso**: Template para outros ambientes
```bash
MONGO_URI=mongodb+srv://seu_usuario:sua_senha@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

## 🐳 Configurações Docker

### 3. `docker-compose.yml` (Produção)
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/docker-compose.yml`
**Uso**: Container de produção
```yaml
environment:
  - MONGO_URI=${MONGO_URI:-mongodb://mongo:27017}
```

### 4. `docker-compose.prod.yml`
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/docker-compose.prod.yml`
**Uso**: Produção otimizada
```yaml
environment:
  - MONGO_URI=${MONGO_URI:-mongodb://mongo:27017}
```

### 5. `docker-compose.dev.yml`
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/docker-compose.dev.yml`
**Uso**: Desenvolvimento com containers
```yaml
environment:
  - MONGO_URI=mongodb://mongo-dev:27017
```

## ☸️ Configurações Kubernetes

### 6. `k8s/deployment.yaml`
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/k8s/deployment.yaml`
**Uso**: Deploy em Kubernetes
```yaml
env:
- name: MONGO_URI
  valueFrom:
    secretKeyRef:
      name: api-secrets
      key: mongo_uri
```

## 🛠️ Scripts de Database

### 7. `scripts/database/.env`
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/scripts/database/.env`
**Uso**: Scripts de gerenciamento do banco
```bash
MONGO_URI=mongodb+srv://seu_usuario:sua_senha@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=api_consulta_v2
```

### 8. `scripts/database/.env.example`
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/scripts/database/.env.example`
**Uso**: Template para scripts
```bash
MONGO_URI=mongodb+srv://seu_usuario:sua_senha@cluster0.wjwnv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

## 🏗️ Código da Aplicação

### 9. `src/config/settings.py`
**Localização**: `/home/thiago/api-consulta-v2/api-consulta-v2/src/config/settings.py`
**Uso**: Configuração padrão da aplicação
```python
MONGO_URI: str = Field(default="mongodb://localhost:27017")
```

## 📋 Prioridade de Configuração

1. **Para desenvolvimento local**: Configure `.env` na raiz do projeto
2. **Para containers Docker**: Use variáveis de ambiente no docker-compose
3. **Para Kubernetes**: Configure secrets no cluster
4. **Para scripts de banco**: Configure `scripts/database/.env`

## 🔐 Segurança

- ❌ **NUNCA** commite strings de conexão reais no Git
- ✅ Use `.env` files locais (no .gitignore)
- ✅ Use secrets do Kubernetes em produção
- ✅ Use variáveis de ambiente no Docker

## 🚀 Como Configurar

### Desenvolvimento Local:
```bash
# 1. Copie o template
cp .env.example .env

# 2. Edite com suas credenciais
nano .env

# 3. Configure os scripts
cp scripts/database/.env.example scripts/database/.env
nano scripts/database/.env
```

### Produção Docker:
```bash
# Configure variável de ambiente
export MONGO_URI="mongodb+srv://..."

# Execute o container
docker-compose -f docker-compose.prod.yml up
```

### Kubernetes:
```bash
# Crie o secret
kubectl create secret generic api-secrets \
  --from-literal=mongo_uri="mongodb+srv://..."

# Deploy a aplicação
kubectl apply -f k8s/
```
