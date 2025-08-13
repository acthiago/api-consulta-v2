"""
DTOs para Pagamento - Data Transfer Objects
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal


@dataclass
class PagamentoDTO:
    """DTO para transferência de dados de Pagamento"""
    
    id: str
    divida_id: str
    valor: Decimal
    forma_pagamento: str
    status: str
    data_criacao: datetime
    data_processamento: Optional[datetime]
    transacao_id: Optional[str]
    comprovante_url: Optional[str]


@dataclass
class ProcessarPagamentoDTO:
    """DTO para processamento de pagamento"""
    
    divida_id: str
    valor: Decimal
    forma_pagamento: str
    dados_pagamento: dict


@dataclass
class ConsultarStatusPagamentoDTO:
    """DTO para consulta de status de pagamento"""
    
    pagamento_id: str


@dataclass
class StatusPagamentoDTO:
    """DTO para resposta de status de pagamento"""
    
    id: str
    status: str
    data_processamento: Optional[datetime]
    mensagem: Optional[str]
