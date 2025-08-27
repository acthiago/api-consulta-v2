#!/usr/bin/env python3
"""
MongoDB Migration Manager
Gerencia migrações e versionamento do schema do banco
"""

import os
import sys
from typing import Dict, List, Optional, Callable
from datetime import datetime, timezone
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Migration:
    """Classe base para migrações"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.created_at = datetime.now(timezone.utc)
    
    def up(self, db):
        """Aplica a migração"""
        raise NotImplementedError("Método up deve ser implementado")
    
    def down(self, db):
        """Reverte a migração"""
        raise NotImplementedError("Método down deve ser implementado")

class MigrationManager:
    """Gerenciador de migrações"""
    
    def __init__(self, connection_string: str, database_name: str = "api_consulta_v2"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.migrations = []
        self._register_migrations()
    
    def connect(self) -> bool:
        """Conecta ao MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            # Cria coleção de controle de migrações
            if "migrations" not in self.db.list_collection_names():
                self.db.create_collection("migrations")
                logger.info("📝 Coleção de migrações criada")
            
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do MongoDB"""
        if self.client:
            self.client.close()
    
    def _register_migrations(self):
        """Registra todas as migrações disponíveis"""
        
        # Migration 001: Estrutura inicial
        class InitialStructure(Migration):
            def __init__(self):
                super().__init__(
                    version="001",
                    description="Criação da estrutura inicial de coleções"
                )
            
            def up(self, db):
                logger.info("🏗️  Criando estrutura inicial...")
                
                # Cria coleção de clientes com validação
                if "clientes" not in db.list_collection_names():
                    db.create_collection("clientes", validator={
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["cpf", "nome", "email", "status", "created_at"],
                            "properties": {
                                "cpf": {"bsonType": "string", "pattern": "^[0-9]{11}$"},
                                "nome": {"bsonType": "string", "minLength": 2},
                                "email": {"bsonType": "string"},
                                "status": {"bsonType": "string", "enum": ["ativo", "inativo"]},
                                "created_at": {"bsonType": "date"}
                            }
                        }
                    })
                    db.clientes.create_index("cpf", unique=True)
                    db.clientes.create_index("email", unique=True)
            
            def down(self, db):
                logger.info("🗑️  Removendo estrutura inicial...")
                db.drop_collection("clientes")
        
        # Migration 002: Adiciona coleção de pagamentos
        class AddPayments(Migration):
            def __init__(self):
                super().__init__(
                    version="002", 
                    description="Adiciona coleção de pagamentos"
                )
            
            def up(self, db):
                logger.info("💰 Criando coleção de pagamentos...")
                
                if "pagamentos" not in db.list_collection_names():
                    db.create_collection("pagamentos", validator={
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["cliente_id", "valor", "status", "created_at"],
                            "properties": {
                                "cliente_id": {"bsonType": "objectId"},
                                "valor": {"bsonType": "decimal"},
                                "status": {"bsonType": "string", "enum": ["pendente", "pago", "cancelado"]},
                                "created_at": {"bsonType": "date"}
                            }
                        }
                    })
                    db.pagamentos.create_index("cliente_id")
                    db.pagamentos.create_index("status")
                    db.pagamentos.create_index("created_at")
            
            def down(self, db):
                logger.info("🗑️  Removendo coleção de pagamentos...")
                db.drop_collection("pagamentos")
        
        # Migration 003: Adiciona campo status bloqueado
        class AddBlockedStatus(Migration):
            def __init__(self):
                super().__init__(
                    version="003",
                    description="Adiciona status 'bloqueado' para clientes"
                )
            
            def up(self, db):
                logger.info("🔒 Adicionando status 'bloqueado'...")
                
                # Atualiza o validator da coleção clientes
                db.command({
                    "collMod": "clientes",
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["cpf", "nome", "email", "status", "created_at"],
                            "properties": {
                                "cpf": {"bsonType": "string", "pattern": "^[0-9]{11}$"},
                                "nome": {"bsonType": "string", "minLength": 2},
                                "email": {"bsonType": "string"},
                                "status": {"bsonType": "string", "enum": ["ativo", "inativo", "bloqueado"]},
                                "created_at": {"bsonType": "date"}
                            }
                        }
                    }
                })
            
            def down(self, db):
                logger.info("🔓 Removendo status 'bloqueado'...")
                
                # Remove clientes com status bloqueado
                db.clientes.update_many(
                    {"status": "bloqueado"}, 
                    {"$set": {"status": "inativo"}}
                )
                
                # Volta o validator original
                db.command({
                    "collMod": "clientes",
                    "validator": {
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["cpf", "nome", "email", "status", "created_at"],
                            "properties": {
                                "cpf": {"bsonType": "string", "pattern": "^[0-9]{11}$"},
                                "nome": {"bsonType": "string", "minLength": 2},
                                "email": {"bsonType": "string"},
                                "status": {"bsonType": "string", "enum": ["ativo", "inativo"]},
                                "created_at": {"bsonType": "date"}
                            }
                        }
                    }
                })
        
        # Migration 004: Adiciona coleção de boletos
        class AddBoletos(Migration):
            def __init__(self):
                super().__init__(
                    version="004",
                    description="Adiciona coleção de boletos"
                )
            
            def up(self, db):
                logger.info("🧾 Criando coleção de boletos...")
                
                if "boletos" not in db.list_collection_names():
                    db.create_collection("boletos", validator={
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["numero_boleto", "cliente_id", "valor", "status", "created_at"],
                            "properties": {
                                "numero_boleto": {"bsonType": "string"},
                                "cliente_id": {"bsonType": "objectId"},
                                "pagamento_id": {"bsonType": "objectId"},
                                "valor": {"bsonType": "decimal"},
                                "data_vencimento": {"bsonType": "date"},
                                "status": {"bsonType": "string", "enum": ["ativo", "pago", "cancelado", "vencido"]},
                                "created_at": {"bsonType": "date"}
                            }
                        }
                    })
                    db.boletos.create_index("numero_boleto", unique=True)
                    db.boletos.create_index("cliente_id")
                    db.boletos.create_index("status")
            
            def down(self, db):
                logger.info("🗑️  Removendo coleção de boletos...")
                db.drop_collection("boletos")
        
        # Migration 005: Adiciona auditoria e usuários
        class AddAuditAndUsers(Migration):
            def __init__(self):
                super().__init__(
                    version="005",
                    description="Adiciona auditoria e usuários"
                )
            
            def up(self, db):
                logger.info("👥 Criando coleções de usuários e auditoria...")
                
                # Coleção de usuários
                if "usuarios" not in db.list_collection_names():
                    db.create_collection("usuarios", validator={
                        "$jsonSchema": {
                            "bsonType": "object",
                            "required": ["username", "email", "password_hash", "role", "status", "created_at"],
                            "properties": {
                                "username": {"bsonType": "string", "minLength": 3},
                                "email": {"bsonType": "string"},
                                "password_hash": {"bsonType": "string"},
                                "role": {"bsonType": "string", "enum": ["admin", "user", "readonly"]},
                                "status": {"bsonType": "string", "enum": ["ativo", "inativo", "bloqueado"]},
                                "created_at": {"bsonType": "date"}
                            }
                        }
                    })
                    db.usuarios.create_index("username", unique=True)
                    db.usuarios.create_index("email", unique=True)
                
                # Coleção de auditoria
                if "auditoria" not in db.list_collection_names():
                    db.create_collection("auditoria")
                    db.auditoria.create_index("acao")
                    db.auditoria.create_index("created_at")
                    db.auditoria.create_index("usuario_id")
            
            def down(self, db):
                logger.info("🗑️  Removendo usuários e auditoria...")
                db.drop_collection("usuarios")
                db.drop_collection("auditoria")
        
        # Registra todas as migrações
        self.migrations = [
            InitialStructure(),
            AddPayments(),
            AddBlockedStatus(),
            AddBoletos(),
            AddAuditAndUsers()
        ]
    
    def get_applied_migrations(self) -> List[str]:
        """Retorna lista de migrações já aplicadas"""
        applied = list(self.db.migrations.find({}, {"version": 1}).sort("applied_at", 1))
        return [m["version"] for m in applied]
    
    def get_pending_migrations(self) -> List[Migration]:
        """Retorna migrações pendentes"""
        applied = self.get_applied_migrations()
        return [m for m in self.migrations if m.version not in applied]
    
    def apply_migration(self, migration: Migration) -> bool:
        """Aplica uma migração específica"""
        try:
            logger.info(f"🚀 Aplicando migração {migration.version}: {migration.description}")
            
            # Aplica a migração
            migration.up(self.db)
            
            # Registra a migração como aplicada
            self.db.migrations.insert_one({
                "version": migration.version,
                "description": migration.description,
                "applied_at": datetime.now(timezone.utc)
            })
            
            logger.info(f"✅ Migração {migration.version} aplicada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar migração {migration.version}: {e}")
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """Reverte uma migração específica"""
        try:
            # Encontra a migração
            migration = next((m for m in self.migrations if m.version == version), None)
            if not migration:
                logger.error(f"❌ Migração {version} não encontrada")
                return False
            
            logger.info(f"⏪ Revertendo migração {version}: {migration.description}")
            
            # Reverte a migração
            migration.down(self.db)
            
            # Remove o registro da migração
            self.db.migrations.delete_one({"version": version})
            
            logger.info(f"✅ Migração {version} revertida com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao reverter migração {version}: {e}")
            return False
    
    def migrate_up(self, target_version: Optional[str] = None) -> bool:
        """Aplica todas as migrações pendentes até a versão alvo"""
        pending = self.get_pending_migrations()
        
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
        
        if not pending:
            logger.info("✅ Nenhuma migração pendente")
            return True
        
        logger.info(f"📋 {len(pending)} migrações pendentes")
        
        for migration in pending:
            if not self.apply_migration(migration):
                logger.error(f"❌ Falha na migração {migration.version}")
                return False
        
        logger.info("🎉 Todas as migrações aplicadas com sucesso!")
        return True
    
    def migrate_down(self, target_version: str) -> bool:
        """Reverte migrações até a versão alvo"""
        applied = self.get_applied_migrations()
        applied.reverse()  # Reverte na ordem inversa
        
        to_rollback = [v for v in applied if v > target_version]
        
        if not to_rollback:
            logger.info("✅ Nenhuma migração para reverter")
            return True
        
        logger.info(f"📋 Revertendo {len(to_rollback)} migrações")
        
        for version in to_rollback:
            if not self.rollback_migration(version):
                logger.error(f"❌ Falha ao reverter migração {version}")
                return False
        
        logger.info("🎉 Reversão concluída com sucesso!")
        return True
    
    def status(self):
        """Mostra status das migrações"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        print("\n📊 Status das Migrações:")
        print("=" * 50)
        
        print("\n✅ Migrações Aplicadas:")
        if applied:
            for version in applied:
                migration = next((m for m in self.migrations if m.version == version), None)
                desc = migration.description if migration else "Descrição não encontrada"
                print(f"  {version}: {desc}")
        else:
            print("  Nenhuma migração aplicada")
        
        print("\n⏳ Migrações Pendentes:")
        if pending:
            for migration in pending:
                print(f"  {migration.version}: {migration.description}")
        else:
            print("  Nenhuma migração pendente")

def main():
    """Função principal"""
    print("🔄 MongoDB Migration Manager")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Uso: python migrations.py <comando> [argumentos]")
        print("\nComandos disponíveis:")
        print("  status                 - Mostra status das migrações")
        print("  up [version]          - Aplica migrações (até versão específica)")
        print("  down <version>        - Reverte até versão específica")
        print("  rollback <version>    - Reverte migração específica")
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
    
    # Inicializa o gerenciador
    manager = MigrationManager(connection_string)
    
    if not manager.connect():
        print("❌ Não foi possível conectar ao banco")
        return
    
    try:
        command = sys.argv[1]
        
        if command == "status":
            manager.status()
            
        elif command == "up":
            target_version = sys.argv[2] if len(sys.argv) > 2 else None
            manager.migrate_up(target_version)
            
        elif command == "down":
            if len(sys.argv) < 3:
                print("❌ Versão alvo necessária para 'down'")
                return
            target_version = sys.argv[2]
            manager.migrate_down(target_version)
            
        elif command == "rollback":
            if len(sys.argv) < 3:
                print("❌ Versão necessária para 'rollback'")
                return
            version = sys.argv[2]
            manager.rollback_migration(version)
            
        else:
            print(f"❌ Comando '{command}' não reconhecido")
    
    finally:
        manager.disconnect()

if __name__ == "__main__":
    main()
