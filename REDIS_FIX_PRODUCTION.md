# 🔧 Correção Redis Exporter - Produção

## 📋 Problema Identificado
- Redis Exporter com erro "server misbehaving" 
- Node Exporter tentando conectar em `host.docker.internal:9100` (não disponível no VPS)
- Configuração incompleta de monitoramento em produção

## ✅ Soluções Implementadas

### 1. **Redis Exporter Configurado**
- ✅ Adicionado ao `docker-compose.vps.yml`
- ✅ Healthcheck configurado com wget
- ✅ Conectado às redes `api_network` e `monitoring_network`

### 2. **Prometheus Otimizado**
- ✅ Criado `monitoring/prometheus.prod.yml` específico para produção
- ✅ Removido node-exporter problemático
- ✅ Mantidos targets essenciais: API, Redis, Traefik

### 3. **Stack Completa de Produção**
- ✅ `docker-compose.prod.yml` atualizado com monitoring completo
- ✅ Limits de recursos configurados
- ✅ Restart policies definidas

## 🚀 Para Aplicar em Produção

### Opção 1: Deploy Automático
```bash
./deploy-vps.sh latest
```

### Opção 2: Manual no VPS
```bash
# No VPS (69.62.103.163):
cd /opt/api-consulta-v2
docker compose down
docker compose pull
docker compose up -d --remove-orphans
```

## 📊 Verificação Pós-Deploy

### 1. **Verificar Serviços**
```bash
docker compose ps
```

### 2. **Testar Redis Exporter**
```bash
curl http://localhost:9121/metrics | grep redis_up
# Deve retornar: redis_up 1
```

### 3. **Verificar Prometheus Targets**
- Acessar: https://monitor.thiagoac.com/prometheus/targets
- Todos devem estar **UP**: prometheus, api-consulta-v2, redis, traefik

### 4. **Logs para Debug**
```bash
# Redis Exporter
docker compose logs redis-exporter

# Prometheus  
docker compose logs prometheus

# Redis
docker compose logs redis
```

## 🎯 Resultado Esperado
- ✅ Redis: **UP** (verde)
- ✅ API: **UP** (verde)  
- ✅ Prometheus: **UP** (verde)
- ✅ Traefik: **UP** (verde)

## 📝 Arquivos Alterados
- `docker-compose.vps.yml` - Adicionado redis-exporter
- `docker-compose.prod.yml` - Stack completa
- `monitoring/prometheus.prod.yml` - Config produção
- `monitoring/prometheus.yml` - Node-exporter removido

---
**Commit:** `a61ff5a` - 🔧 Fix: Configuração Redis Exporter para produção
