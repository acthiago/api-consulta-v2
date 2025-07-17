"""
Value Object para Email com validação
"""

import re
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Email:
    """Value Object para Email com validação"""
    
    valor: str
    
    def __post_init__(self):
        """Valida o email na criação do objeto"""
        if not self._validar():
            raise ValueError("Email inválido")
    
    def _validar(self) -> bool:
        """Validação do email usando regex"""
        if not self.valor:
            return False
        
        # Regex para validação básica de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.valor))
    
    def dominio(self) -> str:
        """Retorna o domínio do email"""
        return self.valor.split('@')[1] if '@' in self.valor else ''
    
    def usuario(self) -> str:
        """Retorna a parte do usuário do email"""
        return self.valor.split('@')[0] if '@' in self.valor else ''
    
    def mascarado(self) -> str:
        """Retorna email mascarado para logs: u***@domain.com"""
        if '@' not in self.valor:
            return self.valor
        
        usuario, dominio = self.valor.split('@')
        if len(usuario) <= 2:
            return f"{usuario[0]}***@{dominio}"
        return f"{usuario[0]}***{usuario[-1]}@{dominio}"
    
    @classmethod
    def from_string(cls, valor: Union[str, None]) -> "Email":
        """Cria Email a partir de string, com validação"""
        if not valor:
            raise ValueError("Email não pode ser vazio")
        return cls(valor.lower().strip())
    
    def __str__(self) -> str:
        return self.valor
    
    def __repr__(self) -> str:
        return f"Email('{self.mascarado()}')"