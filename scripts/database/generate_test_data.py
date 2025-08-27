#!/usr/bin/env python3
"""
Gerador de Massa de Dados para Testes
Cria dados realistas para testar a API e o banco MongoDB
"""

import os
import sys
import random
from typing import Dict, List
from datetime import datetime, timezone, timedelta
import logging
from faker import Faker
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId, Decimal128
import json
from bson import Decimal128
import uuid

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataGenerator:
    """Gerador de dados de teste"""
    
    def __init__(self, connection_string: str, database_name: str = "api_consulta_v2"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        
        # Configurar Faker para dados brasileiros
        self.fake = Faker('pt_BR')
        Faker.seed(42)  # Para dados consistentes
        random.seed(42)
        
        # Dados para geração
        self.status_cliente = ["ativo", "inativo", "bloqueado"]
        self.status_pagamento = ["pendente", "pago", "cancelado"]
        self.tipo_pagamento = ["boleto", "pix", "cartao"]
        self.status_boleto = ["ativo", "pago", "cancelado"]
        self.roles_usuario = ["admin", "user", "readonly"]
        self.acoes_auditoria = [
            "login", "logout", "create_cliente", "update_cliente", "delete_cliente",
            "create_pagamento", "update_pagamento", "delete_pagamento",
            "create_boleto", "update_boleto", "delete_boleto",
            "view_dashboard", "export_data", "backup_database"
        ]
        
    def connect(self) -> bool:
        """Conecta ao MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"✅ Conectado ao MongoDB - Database: {self.database_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do MongoDB"""
        if self.client:
            self.client.close()
    
    def gerar_cpf(self) -> str:
        """Gera um CPF válido"""
        # Gera os 9 primeiros dígitos
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calcula o primeiro dígito verificador
        soma = sum(cpf[i] * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        if digito1 == 10:
            digito1 = 0
        cpf.append(digito1)
        
        # Calcula o segundo dígito verificador
        soma = sum(cpf[i] * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        if digito2 == 10:
            digito2 = 0
        cpf.append(digito2)
        
        return ''.join(map(str, cpf))
    
    def gerar_valor_monetario(self, min_val: float = 10.0, max_val: float = 5000.0) -> Decimal128:
        """Gera um valor monetário realista"""
        valor = round(random.uniform(min_val, max_val), 2)
        return Decimal128(str(valor))
    
    def gerar_data_aleatoria(self, dias_atras: int = 365) -> datetime:
        """Gera uma data aleatória no passado"""
        agora = datetime.now(timezone.utc)
        delta = timedelta(days=random.randint(1, dias_atras))
        return agora - delta
    
    def gerar_clientes(self, quantidade: int = 50) -> List[Dict]:
        """Gera dados de clientes"""
        clientes = []
        cpfs_gerados = set()
        emails_gerados = set()
        
        logger.info(f"🏗️  Gerando {quantidade} clientes...")
        
        for i in range(quantidade):
            # Gera CPF único
            while True:
                cpf = self.gerar_cpf()
                if cpf not in cpfs_gerados:
                    cpfs_gerados.add(cpf)
                    break
            
            # Gera email único
            while True:
                email = self.fake.email()
                if email not in emails_gerados:
                    emails_gerados.add(email)
                    break
            
            created_at = self.gerar_data_aleatoria(180)  # Últimos 6 meses
            
            cliente = {
                "cpf": cpf,
                "nome": self.fake.name(),
                "email": email,
                "telefone": self.fake.phone_number(),
                "endereco": {
                    "rua": self.fake.street_address(),
                    "cidade": self.fake.city(),
                    "estado": self.fake.state_abbr(),
                    "cep": self.fake.postcode(),
                    "numero": str(random.randint(1, 9999)),
                    "complemento": random.choice([None, "Apto " + str(random.randint(1, 200)), "Casa", "Sala " + str(random.randint(1, 50))])
                },
                "data_nascimento": self.fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
                "status": random.choice(self.status_cliente),
                "created_at": created_at,
                "updated_at": created_at + timedelta(days=random.randint(0, 30))
            }
            
            clientes.append(cliente)
            
            if (i + 1) % 10 == 0:
                logger.info(f"📝 Gerados {i + 1}/{quantidade} clientes...")
        
        return clientes
    
    def gerar_usuarios(self, quantidade: int = 5) -> List[Dict]:
        """Gera dados de usuários do sistema"""
        usuarios = []
        usernames_gerados = set()
        emails_gerados = set()
        
        logger.info(f"👥 Gerando {quantidade} usuários...")
        
        # Usuário admin padrão
        admin_user = {
            "username": "admin",
            "email": "admin@apiconsulta.com",
            "password_hash": "$2b$12$LQv3c1yqBwWcD8KK0XdG.e8r8/OJ7.ZN.Y9Z9Z9Z9Z9Z9Z9Z9Z9Z9",  # password: admin123
            "nome": "Administrador do Sistema",
            "role": "admin",
            "status": "ativo",
            "last_login": datetime.now(timezone.utc) - timedelta(hours=2),
            "created_at": datetime.now(timezone.utc) - timedelta(days=30),
            "updated_at": datetime.now(timezone.utc) - timedelta(hours=2)
        }
        usuarios.append(admin_user)
        usernames_gerados.add("admin")
        emails_gerados.add("admin@apiconsulta.com")
        
        for i in range(quantidade - 1):
            # Gera username único
            while True:
                username = self.fake.user_name()
                if username not in usernames_gerados and len(username) >= 3:
                    usernames_gerados.add(username)
                    break
            
            # Gera email único
            while True:
                email = self.fake.email()
                if email not in emails_gerados:
                    emails_gerados.add(email)
                    break
            
            created_at = self.gerar_data_aleatoria(60)  # Últimos 2 meses
            last_login = created_at + timedelta(days=random.randint(1, 30))
            
            usuario = {
                "username": username,
                "email": email,
                "password_hash": "$2b$12$LQv3c1yqBwWcD8KK0XdG.e8r8/OJ7.ZN.Y9Z9Z9Z9Z9Z9Z9Z9Z9Z9",  # password: user123
                "nome": self.fake.name(),
                "role": random.choice(self.roles_usuario),
                "status": random.choice(["ativo", "inativo"]),
                "last_login": last_login,
                "created_at": created_at,
                "updated_at": last_login
            }
            
            usuarios.append(usuario)
        
        return usuarios
    
    def gerar_pagamentos(self, clientes_ids: List, quantidade: int = 200) -> List[Dict]:
        """Gera dados de pagamentos"""
        pagamentos = []
        
        logger.info(f"💰 Gerando {quantidade} pagamentos...")
        
        for i in range(quantidade):
            cliente_id = random.choice(clientes_ids)
            created_at = self.gerar_data_aleatoria(120)  # Últimos 4 meses
            
            # Data de vencimento (entre hoje e 60 dias no futuro)
            data_vencimento = datetime.now(timezone.utc) + timedelta(days=random.randint(-30, 60))
            
            # Data de pagamento (apenas se status = pago)
            status = random.choice(self.status_pagamento)
            data_pagamento = None
            if status == "pago":
                # Pagamento entre created_at e data_vencimento
                max_pay_date = min(data_vencimento, datetime.now(timezone.utc))
                dias_para_pagamento = (max_pay_date - created_at).days
                if dias_para_pagamento > 0:
                    data_pagamento = created_at + timedelta(days=random.randint(1, dias_para_pagamento))
                else:
                    data_pagamento = created_at + timedelta(hours=random.randint(1, 24))
            
            pagamento = {
                "cliente_id": cliente_id,
                "valor": self.gerar_valor_monetario(50.0, 2000.0),
                "descricao": random.choice([
                    "Mensalidade do serviço",
                    "Taxa de manutenção",
                    "Pagamento de consulta",
                    "Renovação anual",
                    "Taxa de adesão",
                    "Serviço premium",
                    "Consulta especializada",
                    "Pacote de serviços"
                ]),
                "status": status,
                "tipo_pagamento": random.choice(self.tipo_pagamento),
                "data_vencimento": data_vencimento,
                "data_pagamento": data_pagamento,
                "codigo_transacao": str(uuid.uuid4()),
                "created_at": created_at,
                "updated_at": data_pagamento if data_pagamento else created_at + timedelta(days=random.randint(0, 5))
            }
            
            pagamentos.append(pagamento)
            
            if (i + 1) % 50 == 0:
                logger.info(f"💳 Gerados {i + 1}/{quantidade} pagamentos...")
        
        return pagamentos
    
    def gerar_boletos(self, clientes_ids: List, pagamentos_ids: List, quantidade: int = 150) -> List[Dict]:
        """Gera dados de boletos"""
        boletos = []
        numeros_gerados = set()
        
        logger.info(f"🧾 Gerando {quantidade} boletos...")
        
        for i in range(quantidade):
            # Gera número do boleto único
            while True:
                numero_boleto = f"{random.randint(10000, 99999)}.{random.randint(10000, 99999)} {random.randint(10000, 99999)}.{random.randint(100000, 999999)} {random.randint(10000, 99999)}.{random.randint(100000, 999999)} {random.randint(1, 9)} {random.randint(10000000000000, 99999999999999)}"
                if numero_boleto not in numeros_gerados:
                    numeros_gerados.add(numero_boleto)
                    break
            
            cliente_id = random.choice(clientes_ids)
            pagamento_id = random.choice(pagamentos_ids)  # Sempre associa um pagamento
            
            created_at = self.gerar_data_aleatoria(90)  # Últimos 3 meses
            data_vencimento = created_at + timedelta(days=random.randint(15, 45))
            
            # Código de barras simulado
            codigo_barras = ''.join([str(random.randint(0, 9)) for _ in range(44)])
            
            # Linha digitável
            linha_digitavel = f"{random.randint(10000, 99999)}.{random.randint(10000, 99999)} {random.randint(10000, 99999)}.{random.randint(100000, 999999)} {random.randint(10000, 99999)}.{random.randint(100000, 999999)} {random.randint(1, 9)} {random.randint(10000000000000, 99999999999999)}"
            
            boleto = {
                "numero_boleto": numero_boleto,
                "cliente_id": cliente_id,
                "pagamento_id": pagamento_id,
                "valor": self.gerar_valor_monetario(30.0, 1500.0),
                "data_vencimento": data_vencimento,
                "linha_digitavel": linha_digitavel,
                "codigo_barras": codigo_barras,
                "banco": random.choice(["001", "033", "104", "237", "341", "399"]),  # Códigos de bancos
                "agencia": f"{random.randint(1000, 9999)}",
                "conta": f"{random.randint(10000, 99999)}-{random.randint(0, 9)}",
                "status": random.choice(self.status_boleto),
                "created_at": created_at,
                "updated_at": created_at + timedelta(days=random.randint(0, 10))
            }
            
            boletos.append(boleto)
            
            if (i + 1) % 30 == 0:
                logger.info(f"📄 Gerados {i + 1}/{quantidade} boletos...")
        
        return boletos
    
    def gerar_auditoria(self, usuarios_ids: List, quantidade: int = 500) -> List[Dict]:
        """Gera dados de auditoria"""
        auditorias = []
        
        logger.info(f"📝 Gerando {quantidade} registros de auditoria...")
        
        for i in range(quantidade):
            usuario_id = random.choice(usuarios_ids)
            created_at = self.gerar_data_aleatoria(30)  # Último mês
            acao = random.choice(self.acoes_auditoria)
            
            # Gera detalhes baseados na ação
            detalhes = {}
            if "create" in acao:
                detalhes = {"action": "create", "new_record_id": str(uuid.uuid4())}
            elif "update" in acao:
                detalhes = {"action": "update", "record_id": str(uuid.uuid4()), "fields_changed": random.choice([["status"], ["nome", "email"], ["valor"]])}
            elif "delete" in acao:
                detalhes = {"action": "delete", "record_id": str(uuid.uuid4()), "reason": "User request"}
            elif acao == "login":
                detalhes = {"action": "login", "success": True, "method": "email"}
            elif acao == "logout":
                detalhes = {"action": "logout", "session_duration": random.randint(5, 180)}
            else:
                detalhes = {"action": acao, "timestamp": created_at.isoformat()}
            
            auditoria = {
                "usuario_id": usuario_id,
                "acao": acao,
                "recurso": random.choice(["clientes", "pagamentos", "boletos", "usuarios", "sistema"]),
                "detalhes": detalhes,
                "ip_address": self.fake.ipv4(),
                "user_agent": random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                ]),
                "created_at": created_at
            }
            
            auditorias.append(auditoria)
            
            if (i + 1) % 100 == 0:
                logger.info(f"🔍 Gerados {i + 1}/{quantidade} registros de auditoria...")
        
        return auditorias
    
    def inserir_dados(self, colecao: str, dados: List[Dict]) -> bool:
        """Insere dados em uma coleção"""
        try:
            if not dados:
                logger.warning(f"⚠️  Nenhum dado para inserir em {colecao}")
                return True
            
            resultado = self.db[colecao].insert_many(dados)
            logger.info(f"✅ Inseridos {len(resultado.inserted_ids)} documentos em {colecao}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inserir dados em {colecao}: {e}")
            return False
    
    def limpar_dados_teste(self):
        """Remove todos os dados de teste (exceto migrações)"""
        logger.info("🧹 Limpando dados de teste existentes...")
        
        colecoes = ["auditoria", "boletos", "pagamentos", "clientes", "usuarios"]
        
        for colecao in colecoes:
            # Não remove dados se a coleção tem poucos documentos (pode ser produção)
            count = self.db[colecao].count_documents({})
            if count > 0:
                self.db[colecao].delete_many({})
                logger.info(f"🗑️  Removidos {count} documentos de {colecao}")
    
    def gerar_massa_completa(self, 
                           clientes: int = 50, 
                           usuarios: int = 5, 
                           pagamentos: int = 200, 
                           boletos: int = 150, 
                           auditoria: int = 500,
                           limpar_antes: bool = True):
        """Gera massa de dados completa"""
        
        logger.info("🚀 Iniciando geração de massa de dados...")
        
        if limpar_antes:
            self.limpar_dados_teste()
        
        # 1. Gera e insere usuários
        usuarios_dados = self.gerar_usuarios(usuarios)
        if not self.inserir_dados("usuarios", usuarios_dados):
            return False
        usuarios_ids = [str(doc["_id"]) for doc in self.db.usuarios.find({}, {"_id": 1})]
        
        # 2. Gera e insere clientes
        clientes_dados = self.gerar_clientes(clientes)
        if not self.inserir_dados("clientes", clientes_dados):
            return False
        clientes_ids = [doc["_id"] for doc in self.db.clientes.find({}, {"_id": 1})]
        
        # 3. Gera e insere pagamentos
        pagamentos_dados = self.gerar_pagamentos(clientes_ids, pagamentos)
        if not self.inserir_dados("pagamentos", pagamentos_dados):
            return False
        pagamentos_ids = [doc["_id"] for doc in self.db.pagamentos.find({}, {"_id": 1})]
        
        # 4. Gera e insere boletos
        boletos_dados = self.gerar_boletos(clientes_ids, pagamentos_ids, boletos)
        if not self.inserir_dados("boletos", boletos_dados):
            return False
        
        # 5. Gera e insere auditoria
        auditoria_dados = self.gerar_auditoria(usuarios_ids, auditoria)
        if not self.inserir_dados("auditoria", auditoria_dados):
            return False
        
        logger.info("✅ Massa de dados gerada com sucesso!")
        return True
    
    def estatisticas_dados(self):
        """Mostra estatísticas dos dados gerados"""
        logger.info("📊 Estatísticas dos dados gerados:")
        
        for colecao in ["clientes", "usuarios", "pagamentos", "boletos", "auditoria"]:
            count = self.db[colecao].count_documents({})
            logger.info(f"📁 {colecao}: {count:,} documentos")
            
            if colecao == "clientes":
                status_stats = list(self.db[colecao].aggregate([
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ]))
                logger.info(f"   Status: {dict((item['_id'], item['count']) for item in status_stats)}")
                
            elif colecao == "pagamentos":
                status_stats = list(self.db[colecao].aggregate([
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ]))
                logger.info(f"   Status: {dict((item['_id'], item['count']) for item in status_stats)}")
                
                valor_total = list(self.db[colecao].aggregate([
                    {"$group": {"_id": None, "total": {"$sum": "$valor"}}}
                ]))
                if valor_total:
                    total_value = float(str(valor_total[0]['total']))
                    logger.info(f"   Valor total: R$ {total_value:,.2f}")
                    
            elif colecao == "usuarios":
                role_stats = list(self.db[colecao].aggregate([
                    {"$group": {"_id": "$role", "count": {"$sum": 1}}}
                ]))
                logger.info(f"   Roles: {dict((item['_id'], item['count']) for item in role_stats)}")

def main():
    """Função principal"""
    print("🎲 Gerador de Massa de Dados para Testes")
    print("=" * 50)
    
    # Carrega variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Obtém string de conexão
    connection_string = os.getenv('MONGO_URI')
    if not connection_string:
        connection_string = input("Digite a string de conexão MongoDB: ")
    
    if '<db_password>' in connection_string:
        password = input("Digite a senha do banco: ")
        connection_string = connection_string.replace('<db_password>', password)
    
    # Configurações
    print("\n⚙️  Configurações de geração:")
    print("1. Configuração padrão (50 clientes, 200 pagamentos, 150 boletos)")
    print("2. Configuração pequena (20 clientes, 50 pagamentos, 30 boletos)")
    print("3. Configuração grande (100 clientes, 500 pagamentos, 300 boletos)")
    print("4. Configuração personalizada")
    
    opcao = input("\nEscolha uma opção (1-4): ").strip()
    
    if opcao == "1":
        config = {"clientes": 50, "usuarios": 5, "pagamentos": 200, "boletos": 150, "auditoria": 500}
    elif opcao == "2":
        config = {"clientes": 20, "usuarios": 3, "pagamentos": 50, "boletos": 30, "auditoria": 100}
    elif opcao == "3":
        config = {"clientes": 100, "usuarios": 8, "pagamentos": 500, "boletos": 300, "auditoria": 1000}
    elif opcao == "4":
        config = {
            "clientes": int(input("Quantidade de clientes: ")),
            "usuarios": int(input("Quantidade de usuários: ")),
            "pagamentos": int(input("Quantidade de pagamentos: ")),
            "boletos": int(input("Quantidade de boletos: ")),
            "auditoria": int(input("Quantidade de registros de auditoria: "))
        }
    else:
        print("❌ Opção inválida, usando configuração padrão")
        config = {"clientes": 50, "usuarios": 5, "pagamentos": 200, "boletos": 150, "auditoria": 500}
    
    # Confirmação
    print(f"\n📋 Será gerado:")
    for chave, valor in config.items():
        print(f"   • {valor:,} {chave}")
    
    limpar = input("\n🧹 Limpar dados existentes antes? (s/N): ").strip().lower()
    limpar_antes = limpar in ['s', 'sim', 'y', 'yes']
    
    confirmar = input("\n✅ Confirma a geração? (s/N): ").strip().lower()
    if confirmar not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return
    
    # Gera dados
    generator = DataGenerator(connection_string)
    
    if not generator.connect():
        print("❌ Não foi possível conectar ao banco")
        return
    
    try:
        # Verifica se faker está disponível
        try:
            from faker import Faker
        except ImportError:
            print("❌ Biblioteca 'faker' não encontrada. Instale com: pip install faker")
            return
        
        sucesso = generator.gerar_massa_completa(
            clientes=config["clientes"],
            usuarios=config["usuarios"],
            pagamentos=config["pagamentos"],
            boletos=config["boletos"],
            auditoria=config["auditoria"],
            limpar_antes=limpar_antes
        )
        
        if sucesso:
            print("\n🎉 Massa de dados gerada com sucesso!")
            generator.estatisticas_dados()
            
            print("\n💡 Dados de acesso gerados:")
            print("   • Usuário admin: admin@apiconsulta.com")
            print("   • Senha padrão: admin123")
            print("\n🧪 Agora você pode testar a API com dados realistas!")
        else:
            print("❌ Erro na geração da massa de dados")
    
    finally:
        generator.disconnect()

if __name__ == "__main__":
    main()
