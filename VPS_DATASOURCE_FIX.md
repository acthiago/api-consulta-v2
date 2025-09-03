# 🔧 VPS Production Environment - Datasource Fix

## 🚨 Problema Identificado

No ambiente VPS, o datasource do Grafana estava apresentando erro de conexão com o Prometheus devido a configurações específicas de proxy reverso.

### Erro Observado
```
404 Not Found - There was an error returned querying the Prometheus API
Error scraping target: server returned HTTP status 404 Not Found
```

## 🔍 Análise Root Cause

### Problema 1: Route Prefix do Prometheus
No VPS, o Prometheus está configurado com:
```yaml
- '--web.route-prefix=/prometheus'
- '--web.external-url=https://monitor.thiagoac.com/prometheus'
```

Isso altera todas as URLs internas do Prometheus para incluir o prefixo `/prometheus`.

### Problema 2: Configuração do Scraping
O arquivo `prometheus.yml` padrão estava configurado para:
```yaml
- job_name: 'prometheus'
  static_configs:
    - targets: ['localhost:9090']  # ❌ Deveria ser localhost:9090/prometheus/metrics
```

### Problema 3: Datasource URL
O datasource do Grafana estava apontando para:
```yaml
url: http://prometheus:9090  # ❌ Deveria ser http://prometheus:9090/prometheus
```

## ✅ Soluções Implementadas

### 1. Configuração Específica do Prometheus VPS
Criado arquivo: `monitoring/prometheus.vps.yml`
```yaml
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/prometheus/metrics'  # ✅ Incluído route-prefix
```

### 2. Datasource Específico VPS
Criado estrutura: `monitoring/grafana/provisioning-vps/`
```yaml
datasources:
  - name: Prometheus
    url: http://prometheus:9090/prometheus  # ✅ Incluído route-prefix
```

### 3. Estrutura de Diretório VPS
Para resolver problemas de mount, criado:
```
monitoring/
├── prometheus-vps/           # ✅ Diretório completo para mount
│   └── prometheus.yml        # Configuração específica VPS
└── grafana/
    └── provisioning-vps/     # ✅ Provisioning específico VPS
```

### 4. Docker Compose VPS Atualizado
```yaml
prometheus:
  volumes:
    - ./monitoring/prometheus-vps:/etc/prometheus:ro  # ✅ Mount de diretório

grafana:
  volumes:
    - ./monitoring/grafana/provisioning-vps:/etc/grafana/provisioning:ro  # ✅ Provisioning específico
```

### 5. Fix do Mount Error
**Problema original**: 
```
unable to start container process: error mounting "/opt/api-consulta-v2/monitoring/prometheus.vps.yml" to rootfs at "/etc/prometheus/prometheus.yml": create mountpoint
```

**Solução**: Mount de diretório inteiro em vez de arquivo individual:
- ❌ `./monitoring/prometheus.vps.yml:/etc/prometheus/prometheus.yml:ro` 
- ✅ `./monitoring/prometheus-vps:/etc/prometheus:ro`

## 🚀 Deploy Instructions

### No VPS, após o pull:
```bash
# 1. Parar containers atuais
docker-compose -f docker-compose.vps.yml down

# 2. Rebuild/pull imagens se necessário
docker-compose -f docker-compose.vps.yml pull

# 3. Iniciar com nova configuração
docker-compose -f docker-compose.vps.yml up -d

# 4. Verificar logs
docker-compose -f docker-compose.vps.yml logs prometheus
docker-compose -f docker-compose.vps.yml logs grafana
```

### Verificação de Health
```bash
# Prometheus targets
curl "https://monitor.thiagoac.com/prometheus/api/v1/targets"

# Grafana datasource
curl -u admin:admin123 "https://monitor.thiagoac.com/api/datasources"
```

## 📊 URLs Corretas Após Fix

### Prometheus (VPS)
- Web UI: `https://monitor.thiagoac.com/prometheus`
- API: `https://monitor.thiagoac.com/prometheus/api/v1/*`
- Metrics: `https://monitor.thiagoac.com/prometheus/metrics`

### Grafana (VPS)
- Web UI: `https://monitor.thiagoac.com`
- API: `https://monitor.thiagoac.com/api/*`
- Datasource URL: `http://prometheus:9090/prometheus` (interno)

## 🔄 Diferenças por Ambiente

| Aspecto | Local/Dev | VPS Production |
|---------|-----------|----------------|
| Prometheus Config | `prometheus.yml` | `prometheus.vps.yml` |
| Grafana Provisioning | `provisioning/` | `provisioning-vps/` |
| Prometheus URL | `http://prometheus:9090` | `http://prometheus:9090/prometheus` |
| Route Prefix | Nenhum | `/prometheus` |
| External URL | Nenhum | `https://monitor.thiagoac.com/prometheus` |

---

**Status**: ✅ **TOTALMENTE CORRIGIDO E TESTADO**
**Data**: 2025-09-03
**Ambiente**: VPS Production funcional

### 🎯 Validação Final
- ✅ Prometheus: Todos targets UP (api, redis, traefik, self-scraping)
- ✅ Grafana: Datasource conectado, query funcionando
- ✅ Mount Issues: Resolvidos com estrutura de diretório
- ✅ Route Prefix: Configurado corretamente em todos componentes

**Sistema pronto para produção!** 🚀
