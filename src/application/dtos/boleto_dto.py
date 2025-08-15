"""
DTOs para Boleto - Data Transfer Objects
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


@dataclass
class BoletoDTO:
    """DTO para transferência de dados de Boleto"""

    id: str
    divida_id: str
    numero_boleto: str
    codigo_barras: str
    linha_digitavel: str
    valor: Decimal
    data_vencimento: date
    data_criacao: datetime
    status: str
    url_pdf: Optional[str]
    qr_code_pix: Optional[str]


@dataclass
class GerarBoletoDTO:
    """DTO para geração de boleto"""

    divida_id: str
    data_vencimento: date
    instrucoes: Optional[str] = None


@dataclass
class BaixarBoletoDTO:
    """DTO para download de boleto"""

    boleto_id: str
    formato: str = "pdf"
