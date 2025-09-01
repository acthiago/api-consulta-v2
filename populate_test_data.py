#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste
"""
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from bson.decimal128 import Decimal128
from src.config.settings import get_settings
from src.infra.db.mongo import MongoProvider

async def populate_test_data():
    """Popula o banco com dados de teste"""
    # Usar configurações reais do ambiente
    settings = get_settings()
    mongo_provider = MongoProvider(settings)
    
    try:
        await mongo_provider.connect()
        db = mongo_provider.db
        
        print("🗑️  Limpando dados existentes...")
        await db.clientes.delete_many({})
        await db.dividas.delete_many({})
        await db.boletos.delete_many({})
        
        print("👤 Criando cliente de teste...")
        # Cliente de teste da requisição
        cliente_id = ObjectId()
        cliente_data = {
            "_id": cliente_id,
            "nome": "Larissa Brito",
            "cpf": "10799118397",
            "email": "larissa.brito@email.com",
            "telefone": "(11) 99999-8888",
            "data_nascimento": "1990-05-15",
            "endereco": {
                "logradouro": "Rua das Flores, 123",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01234-567"
            },
            "status": "ativo",
            "score_credito": 650,
            "limite_credito": 5000.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        await db.clientes.insert_one(cliente_data)
        print(f"✅ Cliente criado com ID: {cliente_id}")
        
        print("💰 Criando dívidas de teste...")
        dividas_test = [
            {
                "_id": ObjectId(),
                "cliente_id": cliente_id,
                "tipo": "cartao_credito",
                "descricao": "Cartão de Crédito - Fatura Vencida",
                "valor_original": Decimal128("1500.00"),
                "valor_atual": Decimal128("1650.00"),
                "data_vencimento": datetime.now() - timedelta(days=15),
                "dias_atraso": 15,
                "status": "vencido",
                "juros_mes": 2.5,
                "multa": 50.0,
                "created_at": datetime.now() - timedelta(days=30),
                "updated_at": datetime.now()
            },
            {
                "_id": ObjectId(),
                "cliente_id": cliente_id,
                "tipo": "emprestimo",
                "descricao": "Empréstimo Pessoal",
                "valor_original": Decimal128("3000.00"),
                "valor_atual": Decimal128("2800.00"),
                "data_vencimento": datetime.now() + timedelta(days=30),
                "dias_atraso": 0,
                "status": "ativo",
                "juros_mes": 1.8,
                "multa": 0.0,
                "created_at": datetime.now() - timedelta(days=60),
                "updated_at": datetime.now()
            },
            {
                "_id": ObjectId(),
                "cliente_id": cliente_id,
                "tipo": "financiamento",
                "descricao": "Financiamento Veículo",
                "valor_original": Decimal128("25000.00"),
                "valor_atual": Decimal128("28000.00"),
                "data_vencimento": datetime.now() - timedelta(days=45),
                "dias_atraso": 45,
                "status": "inadimplente",
                "juros_mes": 1.2,
                "multa": 500.0,
                "created_at": datetime.now() - timedelta(days=90),
                "updated_at": datetime.now()
            }
        ]
        
        for divida in dividas_test:
            await db.dividas.insert_one(divida)
            print(f"✅ Dívida criada: {divida['tipo']} - R$ {divida['valor_atual'].to_decimal()}")
        
        print("\n🎉 Dados de teste criados com sucesso!")
        print(f"Cliente: {cliente_data['nome']} (CPF: {cliente_data['cpf']})")
        print(f"Total de dívidas: {len(dividas_test)}")
        
        # Verifica os dados criados
        print("\n🔍 Verificando dados criados...")
        cliente_encontrado = await db.clientes.find_one({"cpf": "10799118397"})
        print(f"Cliente encontrado: {cliente_encontrado['nome'] if cliente_encontrado else 'Não encontrado'}")
        
        dividas_encontradas = await db.dividas.find({"cliente_id": cliente_id}).to_list(length=100)
        print(f"Dívidas encontradas: {len(dividas_encontradas)}")
        
        for divida in dividas_encontradas:
            print(f"  - {divida['tipo']}: R$ {divida['valor_atual'].to_decimal()} ({divida['status']})")
            
    except Exception as e:
        print(f"❌ Erro ao popular dados: {e}")
        
    finally:
        if mongo_provider:
            await mongo_provider.disconnect()

if __name__ == "__main__":
    asyncio.run(populate_test_data())
