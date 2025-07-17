"""
Entidade Cliente - Representa um cliente no sistema
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from ..value_objects.cpf import CPF
from ..value_objects.email import Email


@dataclass
class Cliente:
    """Entidade Cliente com regras de negócio"""
    
    # Identidade
    id: str = field(default_factory=lambda: str(uuid4()))
    
    # Dados pessoais
    cpf: CPF
    nome: str
    email: Email
    telefone: str
    endereco: str
    
    # Metadados
    data_cadastro: datetime = field(default_factory=datetime.utcnow)
    data_atualizacao: Optional[datetime] = None
    ativo: bool = True
    
    # Relacionamentos
    dividas_ids: List[str] = field(default_factory=list)
    
    # Histórico
    historico_interacoes: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validações após criação do objeto"""
        self._validar_dados()
    
    def _validar_dados(self) -> None:
        """Valida os dados do cliente"""
        if not self.nome or len(self.nome.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        if not self.telefone or len(self.telefone.strip()) < 10:
            raise ValueError("Telefone deve ter pelo menos 10 caracteres")
        
        if not self.endereco or len(self.endereco.strip()) < 10:
            raise ValueError("Endereço deve ter pelo menos 10 caracteres")
    
    def adicionar_divida(self, divida_id: str) -> None:
        """Adiciona uma dívida ao cliente"""
        if not divida_id:
            raise ValueError("ID da dívida não pode ser vazio")
        
        if divida_id not in self.dividas_ids:
            self.dividas_ids.append(divida_id)
            self._registrar_interacao("divida_adicionada", {"divida_id": divida_id})
            self._marcar_como_atualizado()
    
    def remover_divida(self, divida_id: str) -> None:
        """Remove uma dívida do cliente"""
        if divida_id in self.dividas_ids:
            self.dividas_ids.remove(divida_id)
            self._registrar_interacao("divida_removida", {"divida_id": divida_id})
            self._marcar_como_atualizado()
    
    def atualizar_dados_pessoais(
        self, 
        nome: Optional[str] = None,
        email: Optional[Email] = None,
        telefone: Optional[str] = None,
        endereco: Optional[str] = None
    ) -> None:
        """Atualiza dados pessoais do cliente"""
        dados_anteriores = {
            "nome": self.nome,
            "email": self.email.valor,
            "telefone": self.telefone,
            "endereco": self.endereco
        }
        
        if nome is not None:
            if len(nome.strip()) < 2:
                raise ValueError("Nome deve ter pelo menos 2 caracteres")
            self.nome = nome.strip()
        
        if email is not None:
            self.email = email
        
        if telefone is not None:
            if len(telefone.strip()) < 10:
                raise ValueError("Telefone deve ter pelo menos 10 caracteres")
            self.telefone = telefone.strip()
        
        if endereco is not None:
            if len(endereco.strip()) < 10:
                raise ValueError("Endereço deve ter pelo menos 10 caracteres")
            self.endereco = endereco.strip()
        
        self._registrar_interacao("dados_atualizados", {
            "dados_anteriores": dados_anteriores,
            "dados_novos": {
                "nome": self.nome,
                "email": self.email.valor,
                "telefone": self.telefone,
                "endereco": self.endereco
            }
        })
        self._marcar_como_atualizado()
    
    def desativar(self, motivo: str = "") -> None:
        """Desativa o cliente"""
        if not self.ativo:
            raise ValueError("Cliente já está desativado")
        
        self.ativo = False
        self._registrar_interacao("cliente_desativado", {"motivo": motivo})
        self._marcar_como_atualizado()
    
    def reativar(self, motivo: str = "") -> None:
        """Reativa o cliente"""
        if self.ativo:
            raise ValueError("Cliente já está ativo")
        
        self.ativo = True
        self._registrar_interacao("cliente_reativado", {"motivo": motivo})
        self._marcar_como_atualizado()
    
    def tem_dividas(self) -> bool:
        """Verifica se o cliente possui dívidas"""
        return len(self.dividas_ids) > 0
    
    def quantidade_dividas(self) -> int:
        """Retorna a quantidade de dívidas do cliente"""
        return len(self.dividas_ids)
    
    def _registrar_interacao(self, acao: str, dados: Dict[str, Any]) -> None:
        """Registra uma interação no histórico"""
        interacao = {
            "acao": acao,
            "timestamp": datetime.utcnow().isoformat(),
            "dados": dados
        }
        self.historico_interacoes.append(interacao)
    
    def _marcar_como_atualizado(self) -> None:
        """Marca o cliente como atualizado"""
        self.data_atualizacao = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "cpf": self.cpf.limpo(),
            "nome": self.nome,
            "email": self.email.valor,
            "telefone": self.telefone,
            "endereco": self.endereco,
            "data_cadastro": self.data_cadastro.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            "ativo": self.ativo,
            "dividas_ids": self.dividas_ids,
            "historico_interacoes": self.historico_interacoes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cliente":
        """Cria uma entidade a partir de dicionário"""
        return cls(
            id=data["id"],
            cpf=CPF(data["cpf"]),
            nome=data["nome"],
            email=Email(data["email"]),
            telefone=data["telefone"],
            endereco=data["endereco"],
            data_cadastro=datetime.fromisoformat(data["data_cadastro"]),
            data_atualizacao=datetime.fromisoformat(data["data_atualizacao"]) if data.get("data_atualizacao") else None,
            ativo=data.get("ativo", True),
            dividas_ids=data.get("dividas_ids", []),
            historico_interacoes=data.get("historico_interacoes", [])
        )
    
    def __str__(self) -> str:
        return f"Cliente({self.nome} - {self.cpf.mascarado()})"
    
    def __repr__(self) -> str:
        return f"Cliente(id='{self.id}', nome='{self.nome}', cpf='{self.cpf.mascarado()}')"