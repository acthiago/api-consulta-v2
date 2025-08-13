"""
DTOs para Cliente - Data Transfer Objects
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ClienteDTO:
    """DTO para transferência de dados de Cliente"""
    
    id: str
    cpf: str
    nome: str
    email: str
    telefone: str
    endereco: str
    data_cadastro: datetime
    data_atualizacao: Optional[datetime]
    ativo: bool
    dividas_ids: List[str]
    historico_interacoes: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte DTO para dicionário"""
        return {
            "id": self.id,
            "cpf": self.cpf,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "endereco": self.endereco,
            "data_cadastro": self.data_cadastro.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            "ativo": self.ativo,
            "dividas_ids": self.dividas_ids,
            "historico_interacoes": self.historico_interacoes
        }


@dataclass
class CriarClienteDTO:
    """DTO para criação de Cliente"""
    
    cpf: str
    nome: str
    email: str
    telefone: str
    endereco: str


@dataclass
class AtualizarClienteDTO:
    """DTO para atualização de Cliente"""
    
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None


@dataclass
class BuscarClienteDTO:
    """DTO para busca de Cliente"""
    
    cpf: str
