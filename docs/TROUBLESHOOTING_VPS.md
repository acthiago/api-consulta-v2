# Troubleshooting VPS - API Consulta V2

## Problemas Identificados e Soluções

### 1. Datasource não aparece no Grafana

**Problema:** Grafana não consegue carregar os datasources do Prometheus.

**Possíveis causas:**
- Route-prefix mal configurado
- Prometheus não está respondendo
- Configuração de provisioning incorreta

**Soluções implementadas:**

#### A. Configuração Robusta (Recomendada)
```bash
# Use o docker-compose principal com configuração robusta
docker-compose -f docker-compose.vps.yml up -d

# Debug com script personalizado
./scripts/debug-vps.sh full
```

#### B. Configuração Simplificada (Fallback)
```bash
# Use a versão simplificada sem route-prefix
docker-compose -f docker-compose.vps-simple.yml up -d

# Acesse diretamente:
# Prometheus: http://seu-vps:9090
# Grafana: http://seu-vps:3000
```

### 2. Prometheus reiniciando continuamente

**Problema:** Container do Prometheus não consegue inicializar.

**Verificações:**
```bash
# Verificar logs do Prometheus
docker-compose -f docker-compose.vps.yml logs prometheus

# Verificar configuração
docker exec api-consulta-v2-prometheus promtool check config /etc/prometheus/prometheus-robust.yml
```

**Arquivos de configuração disponíveis:**
- `prometheus-robust.yml` - Configuração completa com route-prefix
- `prometheus-simple.yml` - Configuração simplificada sem route-prefix

### 3. Datasources disponíveis

O sistema foi configurado com múltiplos datasources para máxima compatibilidade:

1. **Prometheus-Direct** (Padrão) - Conexão direta sem route-prefix
2. **Prometheus-RoutePrefix** - Com route-prefix para Traefik
3. **Prometheus-Fallback** - Configuração de emergência

### 4. Scripts de Debug

Execute o script de debug para diagnóstico completo:

```bash
# Status dos containers
./scripts/debug-vps.sh status

# Logs recentes
./scripts/debug-vps.sh logs

# Teste de conectividade
./scripts/debug-vps.sh connectivity

# Verificação de configurações
./scripts/debug-vps.sh config

# Restart completo
./scripts/debug-vps.sh restart

# Diagnóstico completo
./scripts/debug-vps.sh full
```

### 5. Portas expostas para debug

Na configuração atual, as seguintes portas estão expostas para facilitar o debug:

- **8000** - API Principal
- **3000** - Grafana
- **6379** - Redis
- **9090** - Prometheus
- **9121** - Redis Exporter

### 6. Verificação manual dos serviços

```bash
# Testar API
curl http://localhost:8000/health

# Testar Prometheus
curl http://localhost:9090/-/healthy

# Testar Grafana
curl http://localhost:3000/api/health

# Testar Redis
redis-cli ping

# Testar Redis Exporter
curl http://localhost:9121/metrics
```

### 7. Limpeza completa (se necessário)

```bash
# Parar todos os containers
docker-compose -f docker-compose.vps.yml down

# Remover volumes (CUIDADO: perde dados!)
docker-compose -f docker-compose.vps.yml down -v

# Remover imagens órfãs
docker system prune -f

# Restart completo
docker-compose -f docker-compose.vps.yml up -d
```

### 8. Monitoramento contínuo

```bash
# Acompanhar logs em tempo real
docker-compose -f docker-compose.vps.yml logs -f

# Verificar uso de recursos
docker stats

# Verificar healthchecks
docker-compose -f docker-compose.vps.yml ps
```

## Estratégia de Deploy

1. **Primeiro:** Teste local com `docker-compose.vps-simple.yml`
2. **Segundo:** Se funcionar, migre para `docker-compose.vps.yml` com Traefik
3. **Terceiro:** Configure DNS e SSL apenas após confirmar que o monitoramento funciona

## Contacts

Em caso de problemas persistentes, verifique:
1. Logs detalhados com `./scripts/debug-vps.sh logs`
2. Conectividade entre containers
3. Configurações de firewall do VPS
4. Recursos disponíveis (RAM, CPU, Disk)
