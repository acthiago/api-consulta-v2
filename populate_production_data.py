#!/usr/bin/env python3
"""
Script para popular o banco de dados de PRODUÇÃO com dados de teste
USAR COM CUIDADO - APENAS EM PRODUÇÃO CONTROLADA
"""
import asyncio
import os
from datetime import datetime, timedelta
from bson import ObjectId
from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorClient

async def populate_production_data():
    """Popula o banco de produção com dados de teste"""
    
    # String de conexão do MongoDB (Atlas ou servidor de produção)
    # Em produção, essa string deve vir de variável de ambiente
    mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/?authSource=admin")
    db_name = os.getenv("MONGO_DB_NAME", "api_consulta_v2")
    
    print(f"🔗 Conectando ao MongoDB: {mongo_uri.replace(mongo_uri.split('@')[0].split('//')[1], '***')}@{mongo_uri.split('@')[1] if '@' in mongo_uri else mongo_uri}")
    
    try:
        # Conecta ao MongoDB
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        
        # Testa a conexão
        await client.admin.command('ping')
        print("✅ Conexão com MongoDB estabelecida")
        
        # Limpa dados existentes do cliente de teste
        print("🗑️  Limpando dados existentes...")
        await db.clientes.delete_many({"cpf": "10799118397"})
        
        # Remove dívidas órfãs (sem cliente associado)
        clientes_existentes = await db.clientes.find({}, {"_id": 1}).to_list(length=None)
        clientes_ids = [c["_id"] for c in clientes_existentes]
        
        if clientes_ids:
            await db.dividas.delete_many({"cliente_id": {"$nin": clientes_ids}})
        else:
            await db.dividas.delete_many({})  # Remove todas se não há clientes
            
        print("👤 Criando cliente de teste...")
        
        # Cria cliente de teste
        cliente_data = {
            "_id": ObjectId(),
            "nome": "Larissa Brito",
            "cpf": "10799118397",
            "email": "uda-mota@example.net",
            "telefone": "+55 (071) 4352-4082",
            "data_nascimento": "1951-11-03",
            "endereco": {
                "rua": "Avenida Novaes, 82",
                "cidade": "Albuquerque",
                "estado": "RJ",
                "cep": "77752-047",
                "numero": "4346",
                "complemento": None
            },
            "status": "ativo",
            "score_credito": None,
            "limite_credito": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        resultado_cliente = await db.clientes.insert_one(cliente_data)
        cliente_id = resultado_cliente.inserted_id
        print(f"✅ Cliente criado com ID: {cliente_id}")
        
        print("💰 Criando dívidas de teste...")
        
        # Cria dívidas de teste
        dividas_data = [
            {
                "_id": ObjectId(),
                "cliente_id": cliente_id,
                "tipo": "cartao_credito",
                "descricao": "Cartão de Crédito - Nubank",
                "valor_original": Decimal128("1500.00"),
                "valor_atual": Decimal128("1650.00"),
                "status": "vencido",
                "data_vencimento": datetime.now() - timedelta(days=15),
                "dias_atraso": 15,
                "juros_mes": Decimal128("2.5"),
                "multa": Decimal128("150.00"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "_id": ObjectId(),
                "cliente_id": cliente_id,
                "tipo": "emprestimo",
                "descricao": "Empréstimo Pessoal - Banco Inter",
                "valor_original": Decimal128("2800.00"),
                "valor_atual": Decimal128("2800.00"),
                "status": "ativo",
                "data_vencimento": datetime.now() + timedelta(days=30),
                "dias_atraso": 0,
                "juros_mes": Decimal128("1.8"),
                "multa": Decimal128("0.00"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "_id": ObjectId(),
                "cliente_id": cliente_id,
                "tipo": "financiamento",
                "descricao": "Financiamento Veículo - Santander",
                "valor_original": Decimal128("25000.00"),
                "valor_atual": Decimal128("28000.00"),
                "status": "inadimplente",
                "data_vencimento": datetime.now() - timedelta(days=45),
                "dias_atraso": 45,
                "juros_mes": Decimal128("3.2"),
                "multa": Decimal128("3000.00"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        await db.dividas.insert_many(dividas_data)
        
        for i, divida in enumerate(dividas_data):
            valor = float(divida["valor_atual"].to_decimal())
            print(f"✅ Dívida criada: {divida['tipo']} - R$ {valor:.2f}")
        
        print("\n🎉 Dados de teste criados com sucesso!")
        print("Cliente: Larissa Brito (CPF: 10799118397)")
        print("Total de dívidas: 3")
        
        # Verifica dados criados
        print("\n🔍 Verificando dados criados...")
        cliente_verificacao = await db.clientes.find_one({"cpf": "10799118397"})
        if cliente_verificacao:
            print(f"Cliente encontrado: {cliente_verificacao['nome']}")
            
            dividas_verificacao = await db.dividas.find({"cliente_id": cliente_id}).to_list(length=10)
            print(f"Dívidas encontradas: {len(dividas_verificacao)}")
            
            for divida in dividas_verificacao:
                valor = float(divida["valor_atual"].to_decimal())
                print(f"  - {divida['tipo']}: R$ {valor:.2f} ({divida['status']})")
        else:
            print("❌ Erro: Cliente não encontrado após criação!")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        raise
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    asyncio.run(populate_production_data())
