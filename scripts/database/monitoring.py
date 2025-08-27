#!/usr/bin/env python3
"""
MongoDB Monitoring and Metrics
Monitora performance e métricas do banco MongoDB na cloud
"""

import os
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
from dataclasses import dataclass
from collections import defaultdict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseMetrics:
    """Métricas do banco de dados"""
    timestamp: datetime
    database_name: str
    total_size_mb: float
    total_documents: int
    total_collections: int
    index_count: int
    avg_query_time_ms: float
    connections_current: int
    operations_per_second: Dict[str, int]
    collection_stats: Dict[str, Dict]

@dataclass
class CollectionMetrics:
    """Métricas de uma coleção"""
    name: str
    document_count: int
    size_mb: float
    avg_document_size_bytes: int
    index_count: int
    index_size_mb: float
    queries_per_minute: int

class MongoMonitor:
    """Monitor do MongoDB"""
    
    def __init__(self, connection_string: str, database_name: str = "api_consulta_v2"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.admin_db = None
        
    def connect(self) -> bool:
        """Conecta ao MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.admin_db = self.client.admin
            logger.info(f"✅ Conectado ao MongoDB - Database: {self.database_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do MongoDB"""
        if self.client:
            self.client.close()
    
    def get_server_status(self) -> Dict[str, Any]:
        """Obtém status do servidor MongoDB"""
        try:
            return self.admin_db.command("serverStatus")
        except Exception as e:
            logger.error(f"❌ Erro ao obter server status: {e}")
            return {}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do banco de dados"""
        try:
            return self.db.command("dbStats")
        except Exception as e:
            logger.error(f"❌ Erro ao obter database stats: {e}")
            return {}
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Obtém estatísticas de uma coleção"""
        try:
            return self.db.command("collStats", collection_name)
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats da coleção {collection_name}: {e}")
            return {}
    
    def get_profiler_data(self, minutes: int = 5) -> List[Dict]:
        """Obtém dados do profiler (consultas lentas)"""
        try:
            # Ativa o profiler se não estiver ativo
            self.db.command("profile", 2, slowms=100)
            
            # Busca operações dos últimos minutos
            since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            profiler_data = list(self.db["system.profile"].find({
                "ts": {"$gte": since}
            }).sort("ts", -1).limit(100))
            
            return profiler_data
        except Exception as e:
            logger.error(f"❌ Erro ao obter dados do profiler: {e}")
            return []
    
    def analyze_slow_queries(self, minutes: int = 5) -> Dict[str, Any]:
        """Analisa consultas lentas"""
        try:
            profiler_data = self.get_profiler_data(minutes)
            
            if not profiler_data:
                return {"message": "Nenhuma operação registrada no profiler"}
            
            slow_queries = []
            operations_by_type = defaultdict(int)
            operations_by_collection = defaultdict(int)
            total_time = 0
            
            for op in profiler_data:
                duration_ms = op.get("millis", op.get("ts", {}).get("millis", 0))
                
                if duration_ms > 100:  # Consultas > 100ms
                    slow_queries.append({
                        "timestamp": op.get("ts"),
                        "duration_ms": duration_ms,
                        "operation": op.get("op", "unknown"),
                        "collection": op.get("ns", "").split(".")[-1] if "." in op.get("ns", "") else op.get("ns", ""),
                        "command": str(op.get("command", {}))[:200] + "..." if len(str(op.get("command", {}))) > 200 else str(op.get("command", {}))
                    })
                
                operations_by_type[op.get("op", "unknown")] += 1
                if "." in op.get("ns", ""):
                    collection = op.get("ns").split(".")[-1]
                    operations_by_collection[collection] += 1
                
                total_time += duration_ms
            
            return {
                "period_minutes": minutes,
                "total_operations": len(profiler_data),
                "slow_queries_count": len(slow_queries),
                "avg_duration_ms": round(total_time / len(profiler_data), 2) if profiler_data else 0,
                "operations_by_type": dict(operations_by_type),
                "operations_by_collection": dict(operations_by_collection),
                "slowest_queries": sorted(slow_queries, key=lambda x: x["duration_ms"], reverse=True)[:10]
            }
        except Exception as e:
            logger.error(f"❌ Erro ao analisar consultas lentas: {e}")
            return {}
    
    def get_index_usage(self) -> Dict[str, Any]:
        """Analisa uso de índices"""
        try:
            index_usage = {}
            
            for collection_name in self.db.list_collection_names():
                collection = self.db[collection_name]
                
                # Obtém estatísticas de uso dos índices
                try:
                    stats = collection.aggregate([{"$indexStats": {}}])
                    collection_indexes = []
                    
                    for index_stat in stats:
                        collection_indexes.append({
                            "name": index_stat.get("name"),
                            "usage_count": index_stat.get("accesses", {}).get("ops", 0),
                            "since": index_stat.get("accesses", {}).get("since")
                        })
                    
                    index_usage[collection_name] = collection_indexes
                except Exception as e:
                    # MongoDB Atlas pode não permitir $indexStats
                    logger.warning(f"⚠️  Não foi possível obter estatísticas de índice para {collection_name}: {e}")
                    
                    # Fallback: lista apenas os índices
                    indexes = list(collection.list_indexes())
                    index_usage[collection_name] = [
                        {"name": idx.get("name"), "keys": idx.get("key")} 
                        for idx in indexes
                    ]
            
            return index_usage
        except Exception as e:
            logger.error(f"❌ Erro ao analisar uso de índices: {e}")
            return {}
    
    def collect_metrics(self) -> DatabaseMetrics:
        """Coleta métricas completas do banco"""
        try:
            # Status do servidor
            server_status = self.get_server_status()
            
            # Estatísticas do banco
            db_stats = self.get_database_stats()
            
            # Estatísticas das coleções
            collection_stats = {}
            total_documents = 0
            
            for collection_name in self.db.list_collection_names():
                if collection_name.startswith("system."):
                    continue
                    
                coll_stats = self.get_collection_stats(collection_name)
                if coll_stats:
                    collection_stats[collection_name] = {
                        "count": coll_stats.get("count", 0),
                        "size_mb": round(coll_stats.get("size", 0) / (1024 * 1024), 2),
                        "avg_obj_size": coll_stats.get("avgObjSize", 0),
                        "index_count": coll_stats.get("nindexes", 0),
                        "index_size_mb": round(coll_stats.get("totalIndexSize", 0) / (1024 * 1024), 2)
                    }
                    total_documents += coll_stats.get("count", 0)
            
            # Operações por segundo
            operations = server_status.get("opcounters", {})
            ops_per_second = {
                "insert": operations.get("insert", 0),
                "query": operations.get("query", 0),
                "update": operations.get("update", 0),
                "delete": operations.get("delete", 0),
                "command": operations.get("command", 0)
            }
            
            # Conexões
            connections = server_status.get("connections", {})
            
            return DatabaseMetrics(
                timestamp=datetime.now(timezone.utc),
                database_name=self.database_name,
                total_size_mb=round(db_stats.get("dataSize", 0) / (1024 * 1024), 2),
                total_documents=total_documents,
                total_collections=len(collection_stats),
                index_count=sum(stats["index_count"] for stats in collection_stats.values()),
                avg_query_time_ms=0,  # Seria necessário calcular a partir do profiler
                connections_current=connections.get("current", 0),
                operations_per_second=ops_per_second,
                collection_stats=collection_stats
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas: {e}")
            return None
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        try:
            metrics = self.collect_metrics()
            if not metrics:
                return {"error": "Não foi possível coletar métricas"}
            
            slow_queries = self.analyze_slow_queries(30)  # Últimos 30 minutos
            index_usage = self.get_index_usage()
            
            # Análises e recomendações
            recommendations = []
            
            # Verifica coleções sem índices adequados
            for coll_name, stats in metrics.collection_stats.items():
                if stats["count"] > 1000 and stats["index_count"] <= 1:
                    recommendations.append(f"⚠️  Coleção '{coll_name}' tem {stats['count']} documentos mas apenas {stats['index_count']} índice(s)")
            
            # Verifica tamanho médio dos documentos
            for coll_name, stats in metrics.collection_stats.items():
                if stats["avg_obj_size"] > 1024 * 1024:  # > 1MB
                    recommendations.append(f"📏 Coleção '{coll_name}' tem documentos grandes (média: {round(stats['avg_obj_size'] / 1024, 2)}KB)")
            
            # Verifica consultas lentas
            if slow_queries.get("slow_queries_count", 0) > 10:
                recommendations.append(f"🐌 {slow_queries['slow_queries_count']} consultas lentas detectadas nos últimos 30 minutos")
            
            return {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "metrics": {
                    "database_name": metrics.database_name,
                    "total_size_mb": metrics.total_size_mb,
                    "total_documents": metrics.total_documents,
                    "total_collections": metrics.total_collections,
                    "connections_current": metrics.connections_current,
                    "operations_per_second": metrics.operations_per_second
                },
                "collection_details": metrics.collection_stats,
                "slow_queries_analysis": slow_queries,
                "index_usage": index_usage,
                "recommendations": recommendations,
                "health_score": self._calculate_health_score(metrics, slow_queries)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {"error": str(e)}
    
    def _calculate_health_score(self, metrics: DatabaseMetrics, slow_queries: Dict) -> int:
        """Calcula um score de saúde do banco (0-100)"""
        try:
            score = 100
            
            # Penaliza por consultas lentas
            slow_count = slow_queries.get("slow_queries_count", 0)
            if slow_count > 50:
                score -= 30
            elif slow_count > 20:
                score -= 20
            elif slow_count > 10:
                score -= 10
            
            # Penaliza por coleções sem índices adequados
            for coll_name, stats in metrics.collection_stats.items():
                if stats["count"] > 1000 and stats["index_count"] <= 1:
                    score -= 5
            
            # Penaliza por documentos muito grandes
            for coll_name, stats in metrics.collection_stats.items():
                if stats["avg_obj_size"] > 1024 * 1024:  # > 1MB
                    score -= 10
            
            # Bonifica por uso adequado de índices
            if metrics.index_count > metrics.total_collections * 2:
                score += 5
            
            return max(0, min(100, score))
            
        except Exception:
            return 50  # Score neutro em caso de erro
    
    def monitor_real_time(self, interval_seconds: int = 30, duration_minutes: int = 10):
        """Monitora métricas em tempo real"""
        try:
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            print(f"🔄 Monitoramento em tempo real por {duration_minutes} minutos")
            print(f"📊 Coletando métricas a cada {interval_seconds} segundos")
            print("=" * 80)
            
            while datetime.now() < end_time:
                metrics = self.collect_metrics()
                if metrics:
                    print(f"\n⏰ {metrics.timestamp.strftime('%H:%M:%S')}")
                    print(f"📊 Documentos: {metrics.total_documents:,}")
                    print(f"💾 Tamanho: {metrics.total_size_mb:.2f} MB")
                    print(f"🔗 Conexões: {metrics.connections_current}")
                    print(f"📈 Ops/seg: Q:{metrics.operations_per_second.get('query', 0)} "
                          f"I:{metrics.operations_per_second.get('insert', 0)} "
                          f"U:{metrics.operations_per_second.get('update', 0)} "
                          f"D:{metrics.operations_per_second.get('delete', 0)}")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoramento interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")

def main():
    """Função principal"""
    print("📊 MongoDB Monitoring and Metrics")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Uso: python monitoring.py <comando> [argumentos]")
        print("\nComandos disponíveis:")
        print("  status                    - Status atual do banco")
        print("  metrics                   - Métricas detalhadas")
        print("  slow-queries [minutes]    - Analisa consultas lentas")
        print("  index-usage              - Uso de índices")
        print("  report                   - Relatório completo de performance")
        print("  monitor [interval] [duration] - Monitoramento em tempo real")
        return
    
    # Carrega variáveis de ambiente do arquivo .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Obtém a string de conexão
    connection_string = os.getenv('MONGO_URI')
    if not connection_string:
        connection_string = input("Digite a string de conexão MongoDB: ")
    
    if '<db_password>' in connection_string:
        password = input("Digite a senha do banco: ")
        connection_string = connection_string.replace('<db_password>', password)
    
    # Inicializa o monitor
    monitor = MongoMonitor(connection_string)
    
    if not monitor.connect():
        print("❌ Não foi possível conectar ao banco")
        return
    
    try:
        command = sys.argv[1]
        
        if command == "status":
            metrics = monitor.collect_metrics()
            if metrics:
                print(f"\n📊 Status do Banco: {metrics.database_name}")
                print(f"🕐 Timestamp: {metrics.timestamp}")
                print(f"📄 Documentos: {metrics.total_documents:,}")
                print(f"📁 Coleções: {metrics.total_collections}")
                print(f"💾 Tamanho: {metrics.total_size_mb:.2f} MB")
                print(f"📇 Índices: {metrics.index_count}")
                print(f"🔗 Conexões: {metrics.connections_current}")
        
        elif command == "metrics":
            metrics = monitor.collect_metrics()
            if metrics:
                print(json.dumps(metrics.__dict__, indent=2, default=str))
        
        elif command == "slow-queries":
            minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            slow_queries = monitor.analyze_slow_queries(minutes)
            print(json.dumps(slow_queries, indent=2, default=str))
        
        elif command == "index-usage":
            index_usage = monitor.get_index_usage()
            print(json.dumps(index_usage, indent=2, default=str))
        
        elif command == "report":
            report = monitor.generate_performance_report()
            print(json.dumps(report, indent=2, default=str))
        
        elif command == "monitor":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            monitor.monitor_real_time(interval, duration)
        
        else:
            print(f"❌ Comando '{command}' não reconhecido")
    
    finally:
        monitor.disconnect()

if __name__ == "__main__":
    main()
