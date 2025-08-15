"""
Value Object para valores monetários com precisão decimal
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Union


@dataclass(frozen=True)
class Money:
    """Value Object para valores monetários"""

    valor: Decimal
    moeda: str = "BRL"

    def __post_init__(self):
        """Valida o valor monetário na criação"""
        if not isinstance(self.valor, Decimal):
            object.__setattr__(self, "valor", Decimal(str(self.valor)))

        if self.valor < 0:
            raise ValueError("Valor monetário não pode ser negativo")

        # Arredonda para 2 casas decimais
        valor_arredondado = self.valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "valor", valor_arredondado)

    def somar(self, outro: "Money") -> "Money":
        """Soma dois valores monetários"""
        if self.moeda != outro.moeda:
            raise ValueError("Não é possível somar moedas diferentes")
        return Money(self.valor + outro.valor, self.moeda)

    def subtrair(self, outro: "Money") -> "Money":
        """Subtrai dois valores monetários"""
        if self.moeda != outro.moeda:
            raise ValueError("Não é possível subtrair moedas diferentes")
        resultado = self.valor - outro.valor
        if resultado < 0:
            raise ValueError("Resultado da subtração não pode ser negativo")
        return Money(resultado, self.moeda)

    def multiplicar(self, fator: Union[int, float, Decimal]) -> "Money":
        """Multiplica o valor por um fator"""
        if not isinstance(fator, Decimal):
            fator = Decimal(str(fator))
        return Money(self.valor * fator, self.moeda)

    def dividir(self, divisor: Union[int, float, Decimal]) -> "Money":
        """Divide o valor por um divisor"""
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        if divisor == 0:
            raise ValueError("Não é possível dividir por zero")
        return Money(self.valor / divisor, self.moeda)

    def porcentagem(self, percentual: Union[int, float, Decimal]) -> "Money":
        """Calcula uma porcentagem do valor"""
        if not isinstance(percentual, Decimal):
            percentual = Decimal(str(percentual))
        return self.multiplicar(percentual / 100)

    def formatado(self) -> str:
        """Retorna valor formatado: R$ 1.234,56"""
        if self.moeda == "BRL":
            valor_str = (
                f"{self.valor:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )
            return f"R$ {valor_str}"
        else:
            return f"{self.moeda} {self.valor:,.2f}"

    def centavos(self) -> int:
        """Retorna o valor em centavos (para APIs de pagamento)"""
        return int(self.valor * 100)

    @classmethod
    def from_centavos(cls, centavos: int, moeda: str = "BRL") -> "Money":
        """Cria Money a partir de centavos"""
        valor = Decimal(centavos) / 100
        return cls(valor, moeda)

    @classmethod
    def from_string(cls, valor_str: str, moeda: str = "BRL") -> "Money":
        """Cria Money a partir de string"""
        # Remove símbolos de moeda e espaços
        valor_limpo = valor_str.replace("R$", "").replace(",", ".").strip()
        return cls(Decimal(valor_limpo), moeda)

    @classmethod
    def zero(cls, moeda: str = "BRL") -> "Money":
        """Cria um valor zero"""
        return cls(Decimal("0"), moeda)

    def eh_zero(self) -> bool:
        """Verifica se o valor é zero"""
        return self.valor == 0

    def eh_positivo(self) -> bool:
        """Verifica se o valor é positivo"""
        return self.valor > 0

    def __str__(self) -> str:
        return self.formatado()

    def __repr__(self) -> str:
        return f"Money({self.valor}, '{self.moeda}')"

    def __float__(self) -> float:
        return float(self.valor)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Money):
            return False
        return self.valor == other.valor and self.moeda == other.moeda

    def __lt__(self, other: "Money") -> bool:
        if self.moeda != other.moeda:
            raise ValueError("Não é possível comparar moedas diferentes")
        return self.valor < other.valor

    def __le__(self, other: "Money") -> bool:
        if self.moeda != other.moeda:
            raise ValueError("Não é possível comparar moedas diferentes")
        return self.valor <= other.valor

    def __gt__(self, other: "Money") -> bool:
        if self.moeda != other.moeda:
            raise ValueError("Não é possível comparar moedas diferentes")
        return self.valor > other.valor

    def __ge__(self, other: "Money") -> bool:
        if self.moeda != other.moeda:
            raise ValueError("Não é possível comparar moedas diferentes")
        return self.valor >= other.valor
