"""
Value Object para CPF com validação rigorosa
"""

import re
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class CPF:
    """Value Object para CPF com validação completa"""

    valor: str

    def __post_init__(self):
        """Valida o CPF na criação do objeto"""
        if not self._validar():
            raise ValueError("CPF inválido")

    def _validar(self) -> bool:
        """Validação completa do CPF usando algoritmo oficial"""
        # Remove caracteres não numéricos
        cpf = re.sub(r"[^0-9]", "", self.valor)

        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False

        # Verifica se não são todos iguais (ex: 111.111.111-11)
        if cpf == cpf[0] * 11:
            return False

        # Algoritmo de validação do CPF
        # Calcula o primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto

        # Verifica o primeiro dígito
        if int(cpf[9]) != digito1:
            return False

        # Calcula o segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto

        # Verifica o segundo dígito
        return int(cpf[10]) == digito2

    def formatado(self) -> str:
        """Retorna CPF formatado: 000.000.000-00"""
        cpf = re.sub(r"[^0-9]", "", self.valor)
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    def mascarado(self) -> str:
        """Retorna CPF mascarado para logs: 000.***.***.00"""
        cpf = re.sub(r"[^0-9]", "", self.valor)
        return f"{cpf[:3]}.***.***.{cpf[-2:]}"

    def limpo(self) -> str:
        """Retorna apenas os números do CPF"""
        return re.sub(r"[^0-9]", "", self.valor)

    @classmethod
    def from_string(cls, valor: Union[str, None]) -> "CPF":
        """Cria CPF a partir de string, com validação"""
        if not valor:
            raise ValueError("CPF não pode ser vazio")
        return cls(valor)

    def __str__(self) -> str:
        return self.formatado()

    def __repr__(self) -> str:
        return f"CPF('{self.mascarado()}')"


def validate_cpf(cpf: str) -> bool:
    """
    Valida um CPF usando o algoritmo oficial brasileiro
    
    Args:
        cpf: CPF para validar (com ou sem formatação)
        
    Returns:
        bool: True se válido, False caso contrário
    """
    try:
        cpf_obj = CPF.criar(cpf)
        return True
    except ValueError:
        return False
