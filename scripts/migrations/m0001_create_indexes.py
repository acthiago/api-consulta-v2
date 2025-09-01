"""
Idempotent script to create required indexes for performance and data integrity.
Run this as part of startup (optional) or manually.
"""

from pymongo import ASCENDING
from pymongo.mongo_client import MongoClient

from src.config.settings import Settings


def run() -> None:
    settings = Settings()
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]

    # Clientes: unique CPF and email (if present), and name for search
    db.clientes.create_index([("cpf", ASCENDING)], name="uniq_cpf", unique=True)
    db.clientes.create_index([("email", ASCENDING)], name="uniq_email", unique=True, sparse=True)
    db.clientes.create_index([("nome", ASCENDING)], name="idx_nome")

    # Dívidas: by cliente, status, and vencimento
    db.dividas.create_index([("cliente_id", ASCENDING)], name="idx_dividas_cliente")
    db.dividas.create_index([("status", ASCENDING)], name="idx_dividas_status")
    db.dividas.create_index([("data_vencimento", ASCENDING)], name="idx_dividas_vencimento")

    # Boletos: by cliente, status and vencimento
    db.boletos.create_index([("cliente_id", ASCENDING)], name="idx_boletos_cliente")
    db.boletos.create_index([("status", ASCENDING)], name="idx_boletos_status")
    db.boletos.create_index([("data_vencimento", ASCENDING)], name="idx_boletos_vencimento")


if __name__ == "__main__":
    run()
    print("Indexes created/ensured.")
