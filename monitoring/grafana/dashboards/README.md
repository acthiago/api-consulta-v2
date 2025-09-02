# 📊 Dashboards de Monitoramento

Este diretório contém os dashboards do Grafana para monitoramento completo da API de Consulta V2.

## 📁 Estrutura dos Dashboards

### 🏠 System Overview (`system-overview.json`)
**Dashboard principal com visão geral de todo o sistema**

**Painéis incluídos:**
- 🏥 **System Health Status**: Status de saúde de todos os serviços (API, Redis, Prometheus)
- ⚡ **System Performance**: Performance geral (RPS da API, Ops/s do Redis, Queries/s do MongoDB)
- 🔥 **Error Rates**: Taxa de erro da API e MongoDB
- 💾 **Resource Usage**: Uso de memória do Redis, clientes conectados, documentos no MongoDB
- 📊 **API Request Rate & Response Time**: Taxa de requisições e tempo de resposta
- 🎯 **Cache Hit Rate & Database Performance**: Taxa de acerto do cache e performance do banco
- 🌐 **HTTP Status Distribution**: Distribuição dos códigos de status HTTP
- 🔄 **Top API Endpoints**: Endpoints mais utilizados
- 💡 **System Alerts & Issues**: Alertas ativos do sistema

---

### 🚀 API Performance (`api-performance.json`)
**Dashboard específico para monitoramento da API FastAPI**

**Painéis incluídos:**
- 🏥 **API Health Status**: Status de saúde da API
- 📊 **Request Rate (RPS)**: Taxa de requisições por segundo
- ⏱️ **Response Time**: Tempo médio de resposta
- ❌ **Error Rate**: Taxa de erro das requisições
- 👥 **Active Connections**: Conexões ativas
- 📈 **Request Volume Over Time**: Volume de requisições ao longo do tempo
- 🎯 **Response Time Percentiles**: Percentis de tempo de resposta (P50, P95, P99)
- 🌐 **HTTP Status Codes**: Distribuição de códigos de status HTTP
- 🔄 **Top Endpoints**: Endpoints mais utilizados
- 📊 **Request Method Distribution**: Distribuição por método HTTP

---

### 🔴 Redis Performance (`redis-performance.json`)
**Dashboard específico para monitoramento do Redis**

**Painéis incluídos:**
- 🏥 **Redis Status**: Status de conexão do Redis
- 💾 **Memory Usage**: Uso de memória (percentual)
- 👥 **Connected Clients**: Clientes conectados
- ⚡ **Operations/sec**: Operações por segundo
- 🎯 **Hit Rate**: Taxa de acerto do cache
- 💾 **Memory Usage Over Time**: Uso de memória ao longo do tempo
- 📊 **Command Statistics**: Estatísticas de comandos executados
- 🔄 **Network I/O**: I/O de rede (input/output)
- 🗃️ **Keys by Database**: Contagem de chaves por banco
- ⏱️ **Command Latency**: Latência dos comandos

---

### 🍃 MongoDB Performance (`mongodb-performance.json`)
**Dashboard específico para monitoramento do MongoDB**

**Painéis incluídos:**
- 🏥 **MongoDB Connection Status**: Status de conexão com MongoDB
- 👥 **Total Clients**: Total de clientes cadastrados
- 🔍 **Queries/min**: Consultas por minuto
- ⚡ **Avg Response Time**: Tempo médio de resposta
- ❌ **Error Rate**: Taxa de erro das consultas
- 📊 **Query Performance Over Time**: Performance das consultas ao longo do tempo
- 🎯 **Query Operations by Type**: Operações por tipo (find, insert, update, delete)
- ⏱️ **Query Duration Percentiles**: Percentis de duração das consultas
- 📈 **Collection Statistics**: Estatísticas das coleções
- 🔄 **Connection Pool Status**: Status do pool de conexões
- 🚨 **Recent Errors**: Logs de erros recentes

## 🚀 Deploy dos Dashboards

Para deployar os dashboards no VPS, execute:

```bash
./scripts/deploy_dashboards.sh
```

Este script irá:
1. Copiar todos os dashboards para o VPS
2. Reiniciar o Grafana com as novas configurações
3. Verificar se todos os serviços estão funcionando

## 🔗 Acesso aos Dashboards

Após o deploy, acesse:

- **Grafana**: http://69.62.103.163:3000
- **Login padrão**: admin/admin (altere na primeira vez)

## 📋 Métricas Disponíveis

### API (FastAPI)
- `http_requests_total`: Total de requisições HTTP
- `http_request_duration_seconds`: Duração das requisições
- `http_requests_in_progress`: Requisições em andamento

### Redis
- `redis_up`: Status do Redis
- `redis_memory_used_bytes`: Memória utilizada
- `redis_connected_clients`: Clientes conectados
- `redis_commands_processed_total`: Comandos processados
- `redis_keyspace_hits_total`: Acertos no cache
- `redis_keyspace_misses_total`: Falhas no cache

### MongoDB (Simuladas/Customizadas)
- `api_mongodb_queries_total`: Total de consultas
- `api_mongodb_query_duration_seconds`: Duração das consultas
- `api_mongodb_errors_total`: Erros nas consultas
- `api_mongodb_total_clients`: Total de clientes
- `api_mongodb_connections_active`: Conexões ativas

## 🔧 Personalização

Para personalizar os dashboards:

1. Edite os arquivos JSON correspondentes
2. Execute o script de deploy novamente
3. Os dashboards serão atualizados automaticamente

## 📊 Alertas Recomendados

Configure alertas para:
- Taxa de erro > 5%
- Tempo de resposta P95 > 500ms
- Uso de memória Redis > 90%
- Conexões MongoDB > 80% do limite
- API fora do ar por mais de 1 minuto

## 🎯 Próximos Passos

1. Configurar alertas automáticos
2. Adicionar métricas de negócio (consultas por CPF, etc.)
3. Implementar logs estruturados
4. Adicionar métricas de infraestrutura (CPU, disco, rede)
