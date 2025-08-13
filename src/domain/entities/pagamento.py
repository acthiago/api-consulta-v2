"""
Entidade: Pagamento
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

from ..value_objects.money import Money


@dataclass
class Pagamento:
    """Entidade de domínio para Pagamento"""
    
    cliente_id: str
    valor: Money
    metodo: str
    descricao: str
    data_pagamento: datetime
    status: str
    id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))
    data_processamento: Optional[datetime] = None
    codigo_transacao: Optional[str] = None
    observacoes: Optional[str] = None
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def validar(self) -> None:
        """
        Valida a entidade Pagamento
        
        Raises:
            ValueError: Se dados inválidos
        """
        if not self.cliente_id:
            raise ValueError("ID do cliente é obrigatório")
        
        if not isinstance(self.valor, Money):
            raise ValueError("Valor deve ser uma instância de Money")
        
        if self.valor.amount <= 0:
            raise ValueError("Valor deve ser positivo")
        
        if not self.metodo:
            raise ValueError("Método de pagamento é obrigatório")
        
        metodos_validos = [
            "cartao_credito", "cartao_debito", "pix", "boleto", 
            "transferencia", "dinheiro"
        ]
        if self.metodo not in metodos_validos:
            raise ValueError(f"Método inválido. Deve ser um de: {metodos_validos}")
        
        if not self.descricao:
            raise ValueError("Descrição é obrigatória")
        
        if not self.data_pagamento:
            raise ValueError("Data de pagamento é obrigatória")
        
        if not self.status:
            raise ValueError("Status é obrigatório")
        
        status_validos = ["pendente", "processando", "aprovado", "rejeitado", "cancelado"]
        if self.status not in status_validos:
            raise ValueError(f"Status inválido. Deve ser um de: {status_validos}")
    
    def aprovar(self, codigo_transacao: str) -> None:
        """
        Aprova o pagamento
        
        Args:
            codigo_transacao: Código da transação
        """
        self.status = "aprovado"
        self.codigo_transacao = codigo_transacao
        self.data_processamento = datetime.utcnow()
    
    def rejeitar(self, motivo: str = None) -> None:
        """
        Rejeita o pagamento
        
        Args:
            motivo: Motivo da rejeição
        """
        self.status = "rejeitado"
        self.data_processamento = datetime.utcnow()
        if motivo:
            self.observacoes = f"{self.observacoes or ''}\nRejeitado: {motivo}".strip()
    
    def cancelar(self, motivo: str = None) -> None:
        """
        Cancela o pagamento
        
        Args:
            motivo: Motivo do cancelamento
        """
        if self.status == "aprovado":
            raise ValueError("Não é possível cancelar pagamento já aprovado")
        
        self.status = "cancelado"
        if motivo:
            self.observacoes = f"{self.observacoes or ''}\nCancelado: {motivo}".strip()
    
    def __str__(self) -> str:
        return f"Pagamento(id={self.id}, valor={self.valor}, status={self.status})"
