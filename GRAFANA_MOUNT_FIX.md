# 🔧 Correção do Erro de Mount do Grafana - RESOLVIDO

## ❌ Problema Identificado
```
failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/opt/api-consulta-v2/monitoring/grafana/dashboards-json" to rootfs at "/etc/grafana/provisioning/dashboards-json": create mountpoint for /etc/grafana/provisioning/dashboards-json mount: mkdirat /var/lib/docker/overlay2/.../merged/etc/grafana/provisioning/dashboards-json: read-only file system: unknown
```

**Causa**: Tentativa de montar volume em diretório que não existe no sistema de arquivos read-only do container.

## ✅ Solução Aplicada

### **Problema Técnico**
O Docker não conseguia criar o diretório `/etc/grafana/provisioning/dashboards-json` porque:
1. O sistema de arquivos do container é read-only
2. O diretório não existe na imagem base do Grafana
3. O Docker precisa criar o mountpoint antes de montar o volume

### **Estratégia de Correção**
Mudança do ponto de mount para um diretório que já existe e é writable.

### **Antes (❌ Falhou)**
```yaml
volumes:
  - ./monitoring/grafana/dashboards-json:/etc/grafana/provisioning/dashboards-json:ro
```
```yaml
# dashboards.yml
options:
  path: /etc/grafana/provisioning/dashboards-json
```

### **Depois (✅ Funcionando)**
```yaml
volumes:
  - ./monitoring/grafana/dashboards-json:/opt/dashboards:ro
```
```yaml
# dashboards.yml
options:
  path: /opt/dashboards
```

## 📁 Arquivos Corrigidos

### 1. **docker-compose.yml** (Local)
```yaml
grafana:
  image: grafana/grafana:latest
  volumes:
    - grafana_data:/var/lib/grafana
    - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    - ./monitoring/grafana/dashboards-json:/opt/dashboards  # ✅ Novo local
```

### 2. **docker-compose.vps.yml** (Produção)
```yaml
grafana:
  image: grafana/grafana:latest
  volumes:
    - grafana_data:/var/lib/grafana
    - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    - ./monitoring/grafana/dashboards-json:/opt/dashboards:ro  # ✅ Novo local
```

### 3. **monitoring/grafana/provisioning/dashboards/dashboards.yml**
```yaml
apiVersion: 1
providers:
  - name: 'API Consulta Dashboards'
    orgId: 1
    folder: ''
    type: file
    options:
      path: /opt/dashboards  # ✅ Novo caminho
```

## 🔍 Validação da Correção

### ✅ **Testes Realizados**
1. **Container Inicia**: Sem erros de mount
2. **Dashboards Montados**: `/opt/dashboards/` contém 4 arquivos JSON
3. **Provisionamento Funciona**: Logs mostram "finished to provision dashboards"
4. **Sem Erros**: Não há mais "Dashboard title cannot be empty"

### ✅ **Verificações**
```bash
# Container inicia normalmente
docker compose up -d grafana ✅

# Dashboards estão montados
docker compose exec grafana ls -la /opt/dashboards/ ✅
# Resultado: 4 arquivos JSON presentes

# Logs confirmam sucesso
docker compose logs grafana | grep dashboard ✅
# Resultado: "finished to provision dashboards"
```

## 🚀 Impacto da Correção

### **Local (Desenvolvimento)**
- ✅ Grafana inicia sem erros
- ✅ Dashboards carregam automaticamente
- ✅ Configuração consistente

### **Produção (VPS)**
- ✅ Deploy funcionará sem erros de mount
- ✅ Dashboards serão provisionados corretamente
- ✅ Monitoramento completo disponível

## 📊 Status Final

**Problema**: ❌ Mount error - read-only filesystem  
**Solução**: ✅ Mount em `/opt/dashboards` (diretório writable)  
**Resultado**: ✅ Grafana + Dashboards funcionando perfeitamente  

**Deploy pronto para produção!** 🎯
