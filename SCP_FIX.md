# 🔧 Correção dos Erros de Deploy SCP

## ❌ Problema Identificado
```
scp: stat local "monitoring/grafana/dashboards/api-monitoring.json": No such file or directory
Error: Process completed with exit code 255.
```

**Causa**: Scripts de deploy ainda referenciavam arquivos antigos que foram removidos/reorganizados.

## ✅ Correções Aplicadas

### 1. **GitHub Actions (.github/workflows/python-app.yml)**
**Antes:**
```yaml
scp monitoring/grafana/dashboards/api-monitoring.json root@69.62.103.163:/opt/api-consulta-v2/monitoring/grafana/dashboards/
```

**Depois:**
```yaml
# Create directories on VPS first
ssh root@69.62.103.163 << 'DIRS_EOF'
  mkdir -p /opt/api-consulta-v2/monitoring/grafana/provisioning/datasources
  mkdir -p /opt/api-consulta-v2/monitoring/grafana/provisioning/dashboards
  mkdir -p /opt/api-consulta-v2/monitoring/grafana/dashboards-json
DIRS_EOF

scp monitoring/prometheus.prod.yml root@69.62.103.163:/opt/api-consulta-v2/monitoring/prometheus.yml
scp -r monitoring/grafana/provisioning/* root@69.62.103.163:/opt/api-consulta-v2/monitoring/grafana/provisioning/
scp -r monitoring/grafana/dashboards-json/* root@69.62.103.163:/opt/api-consulta-v2/monitoring/grafana/dashboards-json/
```

### 2. **Deploy VPS Script (deploy-vps.sh)**
**Antes:**
```bash
if [ -f "monitoring/grafana/dashboards/api-monitoring.json" ]; then
    copy_to_vps "monitoring/grafana/dashboards/api-monitoring.json" "$PROJECT_DIR/monitoring/grafana/dashboards/"
fi
```

**Depois:**
```bash
# Criar estrutura de diretórios no VPS
run_on_vps "mkdir -p $PROJECT_DIR/monitoring/grafana/provisioning/datasources"
run_on_vps "mkdir -p $PROJECT_DIR/monitoring/grafana/provisioning/dashboards"
run_on_vps "mkdir -p $PROJECT_DIR/monitoring/grafana/dashboards-json"

# Copiar arquivos de provisionamento
copy_to_vps "monitoring/grafana/provisioning/" "$PROJECT_DIR/monitoring/grafana/"

# Copiar dashboards corrigidos
for dashboard in monitoring/grafana/dashboards-json/*.json; do
    if [ -f "$dashboard" ]; then
        echo "  📋 Copiando $(basename "$dashboard")"
        copy_to_vps "$dashboard" "$PROJECT_DIR/monitoring/grafana/dashboards-json/"
    fi
done
```

### 3. **Docker Compose VPS (docker-compose.vps.yml)**
**Antes:**
```yaml
volumes:
  - grafana_data:/var/lib/grafana
  - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
  - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
```

**Depois:**
```yaml
volumes:
  - grafana_data:/var/lib/grafana
  - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
  - ./monitoring/grafana/dashboards-json:/etc/grafana/provisioning/dashboards-json:ro
```

### 4. **Dashboard Deploy Script (scripts/deploy_dashboards.sh)**
**Atualizado para:**
- Criar diretórios corretos no VPS
- Copiar arquivos de provisionamento separadamente
- Aplicar correções de estrutura JSON automaticamente
- Usar nova estrutura de volumes

## 📁 Nova Estrutura de Arquivos
```
monitoring/grafana/
├── provisioning/
│   ├── datasources/
│   │   └── prometheus.yml          # Configuração do datasource
│   └── dashboards/
│       └── dashboards.yml          # Configuração de provisionamento
└── dashboards-json/                # Dashboards com estrutura JSON correta
    ├── api-performance.json
    ├── mongodb-performance.json
    ├── redis-performance.json
    └── system-overview.json
```

## 🚀 Scripts Atualizados

### ✅ **GitHub Actions**
- Cria diretórios antes de copiar
- Usa nova estrutura de arquivos
- Remove referências a arquivos antigos

### ✅ **Deploy VPS**
- Loop para copiar dashboards dinamicamente
- Criação automática de diretórios
- Suporte à nova estrutura

### ✅ **Deploy Dashboards**
- Correção automática de JSON
- Estrutura de volumes atualizada
- Validação de arquivos

## 🎯 Resultado

**Problema resolvido**: Não há mais referências a `api-monitoring.json`  
**Estrutura atualizada**: Todos os scripts usam a nova organização  
**Deploy funcionando**: SCP agora encontra todos os arquivos corretamente  

**Status**: ✅ Todos os erros de SCP corrigidos!
