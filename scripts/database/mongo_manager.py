#!/usr/bin/env python3
"""
MongoDB Cloud Database Manager
Gerencia a conexão, estrutura e organização do banco MongoDB na cloud
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MongoCloudManager:
    """Gerenciador do MongoDB na cloud"""
    
    def __init__(self, connection_string: str, database_name: str = "api_consulta_v2"):
        """
        Inicializa o gerenciador do MongoDB
        
        Args:
            connection_string: String de conexão MongoDB Atlas
            database_name: Nome do banco de dados
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        
    def connect(self) -> bool:
        """
        Estabelece conexão com o MongoDB
        
        Returns:
            bool: True se conectado com sucesso
        """
        try:
            self.client = MongoClient(self.connection_string)
            # Testa a conexão
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"✅ Conectado ao MongoDB Atlas - Database: {self.database_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False
    
    def disconnect(self):
        """Fecha a conexão com o MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Conexão fechada")
    
    def get_database_info(self) -> Dict:
        """
        Obtém informações sobre o banco de dados
        
        Returns:
            Dict: Informações do banco
        """
        try:
            # Estatísticas do banco
            stats = self.db.command("dbStats")
            
            # Lista de coleções
            collections = self.db.list_collection_names()
            
            # Informações detalhadas das coleções
            collection_info = {}
            total_documents = 0
            total_indexes = 0
            
            for collection_name in collections:
                if collection_name.startswith("system."):
                    continue
                    
                collection = self.db[collection_name]
                count = collection.count_documents({})
                indexes = list(collection.list_indexes())
                
                collection_info[collection_name] = {
                    "count": count,
                    "indexes": len(indexes),
                    "index_names": [idx.get("name", "unknown") for idx in indexes]
                }
                
                total_documents += count
                total_indexes += len(indexes)
            
            return {
                "database_name": self.database_name,
                "collections": collections,
                "collection_details": collection_info,
                "total_size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2),
                "total_documents": total_documents,
                "indexes_count": total_indexes,
                "server_info": self.client.server_info()["version"]
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações: {e}")
            return {}
    
    def create_collections_structure(self):
        """Cria a estrutura de coleções recomendada"""
        
        collections_schema = {
            "clientes": {
                "description": "Dados dos clientes",
                "indexes": [
                    {"fields": [("cpf", ASCENDING)], "unique": True},
                    {"fields": [("email", ASCENDING)], "unique": True},
                    {"fields": [("created_at", DESCENDING)]},
                    {"fields": [("status", ASCENDING)]},
                    {"fields": [("cpf", "text"), ("nome", "text"), ("email", "text")]}
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["cpf", "nome", "email", "status", "created_at"],
                        "properties": {
                            "cpf": {"bsonType": "string", "pattern": "^[0-9]{11}$"},
                            "nome": {"bsonType": "string", "minLength": 2},
                            "email": {"bsonType": "string", "pattern": "^[^@]+@[^@]+\\.[^@]+$"},
                            "telefone": {"bsonType": "string"},
                            "endereco": {"bsonType": "object"},
                            "status": {"bsonType": "string", "enum": ["ativo", "inativo", "bloqueado"]},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            },
            
            "pagamentos": {
                "description": "Histórico de pagamentos",
                "indexes": [
                    {"fields": [("cliente_id", ASCENDING)]},
                    {"fields": [("status", ASCENDING)]},
                    {"fields": [("data_vencimento", ASCENDING)]},
                    {"fields": [("created_at", DESCENDING)]},
                    {"fields": [("valor", DESCENDING)]},
                    {"fields": [("tipo_pagamento", ASCENDING)]}
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["cliente_id", "valor", "status", "tipo_pagamento", "created_at"],
                        "properties": {
                            "cliente_id": {"bsonType": "objectId"},
                            "valor": {"bsonType": "decimal"},
                            "descricao": {"bsonType": "string"},
                            "status": {"bsonType": "string", "enum": ["pendente", "pago", "cancelado", "vencido"]},
                            "tipo_pagamento": {"bsonType": "string", "enum": ["boleto", "pix", "cartao"]},
                            "data_vencimento": {"bsonType": "date"},
                            "data_pagamento": {"bsonType": "date"},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            },
            
            "boletos": {
                "description": "Boletos gerados",
                "indexes": [
                    {"fields": [("numero_boleto", ASCENDING)], "unique": True},
                    {"fields": [("cliente_id", ASCENDING)]},
                    {"fields": [("pagamento_id", ASCENDING)]},
                    {"fields": [("status", ASCENDING)]},
                    {"fields": [("data_vencimento", ASCENDING)]},
                    {"fields": [("created_at", DESCENDING)]}
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["numero_boleto", "cliente_id", "valor", "status", "created_at"],
                        "properties": {
                            "numero_boleto": {"bsonType": "string"},
                            "cliente_id": {"bsonType": "objectId"},
                            "pagamento_id": {"bsonType": "objectId"},
                            "valor": {"bsonType": "decimal"},
                            "data_vencimento": {"bsonType": "date"},
                            "linha_digitavel": {"bsonType": "string"},
                            "codigo_barras": {"bsonType": "string"},
                            "status": {"bsonType": "string", "enum": ["ativo", "pago", "cancelado", "vencido"]},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            },
            
            "auditoria": {
                "description": "Log de auditoria do sistema",
                "indexes": [
                    {"fields": [("usuario_id", ASCENDING)]},
                    {"fields": [("acao", ASCENDING)]},
                    {"fields": [("created_at", DESCENDING)]},
                    {"fields": [("ip_address", ASCENDING)]},
                    {"fields": [("recurso", ASCENDING)]}
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["acao", "recurso", "created_at"],
                        "properties": {
                            "usuario_id": {"bsonType": "objectId"},
                            "acao": {"bsonType": "string"},
                            "recurso": {"bsonType": "string"},
                            "detalhes": {"bsonType": "object"},
                            "ip_address": {"bsonType": "string"},
                            "user_agent": {"bsonType": "string"},
                            "created_at": {"bsonType": "date"}
                        }
                    }
                }
            },
            
            "usuarios": {
                "description": "Usuários do sistema",
                "indexes": [
                    {"fields": [("email", ASCENDING)], "unique": True},
                    {"fields": [("username", ASCENDING)], "unique": True},
                    {"fields": [("status", ASCENDING)]},
                    {"fields": [("role", ASCENDING)]},
                    {"fields": [("created_at", DESCENDING)]}
                ],
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["username", "email", "password_hash", "role", "status", "created_at"],
                        "properties": {
                            "username": {"bsonType": "string", "minLength": 3},
                            "email": {"bsonType": "string", "pattern": "^[^@]+@[^@]+\\.[^@]+$"},
                            "password_hash": {"bsonType": "string"},
                            "nome": {"bsonType": "string"},
                            "role": {"bsonType": "string", "enum": ["admin", "user", "readonly"]},
                            "status": {"bsonType": "string", "enum": ["ativo", "inativo", "bloqueado"]},
                            "last_login": {"bsonType": "date"},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            }
        }
        
        for collection_name, schema in collections_schema.items():
            try:
                # Cria a coleção se não existir
                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(
                        collection_name,
                        validator=schema.get("validator")
                    )
                    logger.info(f"✅ Coleção '{collection_name}' criada")
                
                # Cria os índices
                collection = self.db[collection_name]
                for index_spec in schema["indexes"]:
                    try:
                        if "unique" in index_spec:
                            collection.create_index(
                                index_spec["fields"],
                                unique=index_spec["unique"]
                            )
                        else:
                            collection.create_index(index_spec["fields"])
                        logger.info(f"📊 Índice criado em '{collection_name}': {index_spec['fields']}")
                    except OperationFailure as e:
                        if "already exists" not in str(e):
                            logger.warning(f"⚠️  Erro ao criar índice: {e}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar coleção '{collection_name}': {e}")
    
    def optimize_database(self):
        """Otimiza o banco de dados"""
        try:
            # Reindexação
            for collection_name in self.db.list_collection_names():
                self.db[collection_name].reindex()
                logger.info(f"🔄 Coleção '{collection_name}' reindexada")
            
            # Compactação (apenas para self-hosted MongoDB)
            # Para MongoDB Atlas, isso é gerenciado automaticamente
            logger.info("✅ Otimização concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro na otimização: {e}")
    
    def backup_data(self, output_file: str = None):
        """
        Faz backup dos dados em formato JSON
        
        Args:
            output_file: Arquivo de saída (opcional)
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"backup_mongodb_{timestamp}.json"
        
        try:
            backup_data = {}
            
            for collection_name in self.db.list_collection_names():
                collection = self.db[collection_name]
                documents = list(collection.find())
                
                # Converte ObjectId para string
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    # Converte datas para string
                    for key, value in doc.items():
                        if isinstance(value, datetime):
                            doc[key] = value.isoformat()
                
                backup_data[collection_name] = documents
                logger.info(f"📦 Backup da coleção '{collection_name}': {len(documents)} documentos")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Backup salvo em: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Erro no backup: {e}")
            return None
    
    def cleanup_data(self):
        """Limpeza e organização dos dados"""
        try:
            # Remove documentos duplicados baseado em CPF (clientes)
            if "clientes" in self.db.list_collection_names():
                pipeline = [
                    {"$group": {
                        "_id": "$cpf",
                        "count": {"$sum": 1},
                        "docs": {"$push": "$_id"}
                    }},
                    {"$match": {"count": {"$gt": 1}}}
                ]
                
                duplicates = list(self.db.clientes.aggregate(pipeline))
                for dup in duplicates:
                    # Mantém apenas o primeiro documento
                    docs_to_remove = dup["docs"][1:]
                    self.db.clientes.delete_many({"_id": {"$in": docs_to_remove}})
                    logger.info(f"🧹 Removidos {len(docs_to_remove)} duplicados para CPF: {dup['_id']}")
            
            # Remove documentos órfãos
            self._remove_orphaned_documents()
            
            logger.info("✅ Limpeza concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")
    
    def _remove_orphaned_documents(self):
        """Remove documentos órfãos"""
        try:
            # Remove pagamentos sem cliente
            if all(coll in self.db.list_collection_names() for coll in ["clientes", "pagamentos"]):
                client_ids = set(doc["_id"] for doc in self.db.clientes.find({}, {"_id": 1}))
                orphaned_payments = self.db.pagamentos.find({"cliente_id": {"$nin": list(client_ids)}})
                orphaned_count = self.db.pagamentos.delete_many({"cliente_id": {"$nin": list(client_ids)}}).deleted_count
                if orphaned_count > 0:
                    logger.info(f"🧹 Removidos {orphaned_count} pagamentos órfãos")
            
            # Remove boletos sem pagamento
            if all(coll in self.db.list_collection_names() for coll in ["pagamentos", "boletos"]):
                payment_ids = set(doc["_id"] for doc in self.db.pagamentos.find({}, {"_id": 1}))
                orphaned_boletos = self.db.boletos.delete_many({"pagamento_id": {"$nin": list(payment_ids)}}).deleted_count
                if orphaned_boletos > 0:
                    logger.info(f"🧹 Removidos {orphaned_boletos} boletos órfãos")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao remover órfãos: {e}")

def main():
    """Função principal"""
    print("🚀 MongoDB Cloud Database Manager")
    print("=" * 50)
    
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
    
    # Inicializa o gerenciador
    manager = MongoCloudManager(connection_string)
    
    if not manager.connect():
        print("❌ Não foi possível conectar ao banco")
        return
    
    try:
        while True:
            print("\n📋 Opções disponíveis:")
            print("1. Ver informações do banco")
            print("2. Criar/Atualizar estrutura de coleções")
            print("3. Otimizar banco de dados")
            print("4. Fazer backup dos dados")
            print("5. Limpar e organizar dados")
            print("6. Sair")
            
            choice = input("\nEscolha uma opção (1-6): ").strip()
            
            if choice == "1":
                print("\n📊 Informações do Banco de Dados:")
                info = manager.get_database_info()
                print(json.dumps(info, indent=2, default=str))
                
            elif choice == "2":
                print("\n🏗️  Criando estrutura de coleções...")
                manager.create_collections_structure()
                print("✅ Estrutura atualizada!")
                
            elif choice == "3":
                print("\n⚡ Otimizando banco de dados...")
                manager.optimize_database()
                
            elif choice == "4":
                print("\n💾 Fazendo backup...")
                backup_file = manager.backup_data()
                if backup_file:
                    print(f"✅ Backup concluído: {backup_file}")
                    
            elif choice == "5":
                print("\n🧹 Limpando e organizando dados...")
                manager.cleanup_data()
                
            elif choice == "6":
                break
                
            else:
                print("❌ Opção inválida")
    
    finally:
        manager.disconnect()

if __name__ == "__main__":
    main()
