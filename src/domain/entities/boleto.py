"""
Entidade: Boleto
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..value_objects.money import Money


@dataclass
class Boleto:
    """Entidade de domínio para Boleto"""

    cliente_id: str
    valor: Money
    descricao: str
    data_emissao: datetime
    data_vencimento: datetime
    linha_digitavel: str
    codigo_barras: str
    status: str
    id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))
    observacoes: Optional[str] = None
    data_pagamento: Optional[datetime] = None
    data_cancelamento: Optional[datetime] = None

    def __post_init__(self):
        """Validações pós-inicialização"""
        if not self.id:
            self.id = str(uuid.uuid4())

    def validar(self) -> None:
        """
        Valida a entidade Boleto

        Raises:
            ValueError: Se dados inválidos
        """
        if not self.cliente_id:
            raise ValueError("ID do cliente é obrigatório")

        if not isinstance(self.valor, Money):
            raise ValueError("Valor deve ser uma instância de Money")

        if self.valor.amount <= 0:
            raise ValueError("Valor deve ser positivo")

        if not self.descricao:
            raise ValueError("Descrição é obrigatória")

        if not self.data_emissao:
            raise ValueError("Data de emissão é obrigatória")

        if not self.data_vencimento:
            raise ValueError("Data de vencimento é obrigatória")

        if self.data_vencimento <= self.data_emissao:
            raise ValueError("Data de vencimento deve ser posterior à emissão")

        if not self.linha_digitavel:
            raise ValueError("Linha digitável é obrigatória")

        if not self.codigo_barras:
            raise ValueError("Código de barras é obrigatório")

        if not self.status:
            raise ValueError("Status é obrigatório")

        status_validos = ["ativo", "pago", "vencido", "cancelado"]
        if self.status not in status_validos:
            raise ValueError(f"Status inválido. Deve ser um de: {status_validos}")

    def esta_vencido(self) -> bool:
        """
        Verifica se o boleto está vencido

        Returns:
            True se vencido, False caso contrário
        """
        return datetime.utcnow() > self.data_vencimento and self.status == "ativo"

    def pagar(self) -> None:
        """Marca o boleto como pago"""
        if self.status == "cancelado":
            raise ValueError("Não é possível pagar boleto cancelado")

        self.status = "pago"
        self.data_pagamento = datetime.utcnow()

    def cancelar(self, motivo: str = None) -> None:
        """
        Cancela o boleto

        Args:
            motivo: Motivo do cancelamento
        """
        if self.status == "pago":
            raise ValueError("Não é possível cancelar boleto já pago")

        self.status = "cancelado"
        self.data_cancelamento = datetime.utcnow()
        if motivo:
            self.observacoes = f"{self.observacoes or ''}\nCancelado: {motivo}".strip()

    def marcar_como_vencido(self) -> None:
        """Marca o boleto como vencido"""
        if self.status == "ativo" and self.esta_vencido():
            self.status = "vencido"

    def __str__(self) -> str:
        return f"Boleto(id={self.id}, valor={self.valor}, status={self.status})"
