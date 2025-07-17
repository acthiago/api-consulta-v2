"""
Testes unitários para Value Objects
"""

import pytest
from decimal import Decimal

from src.domain.value_objects.cpf import CPF
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money


class TestCPF:
    """Testes para o Value Object CPF"""
    
    def test_cpf_valido(self):
        """Testa criação de CPF válido"""
        cpf = CPF("12345678909")
        assert cpf.valor == "12345678909"
        assert cpf.formatado() == "123.456.789-09"
    
    def test_cpf_invalido(self):
        """Testa CPF inválido"""
        with pytest.raises(ValueError, match="CPF inválido"):
            CPF("12345678901")
    
    def test_cpf_todos_iguais(self):
        """Testa CPF com todos os dígitos iguais"""
        with pytest.raises(ValueError, match="CPF inválido"):
            CPF("11111111111")
    
    def test_cpf_tamanho_incorreto(self):
        """Testa CPF com tamanho incorreto"""
        with pytest.raises(ValueError, match="CPF inválido"):
            CPF("123456789")
    
    def test_cpf_mascarado(self):
        """Testa CPF mascarado para logs"""
        cpf = CPF("12345678909")
        assert cpf.mascarado() == "123.***.***.09"
    
    def test_cpf_limpo(self):
        """Testa CPF limpo (apenas números)"""
        cpf = CPF("123.456.789-09")
        assert cpf.limpo() == "12345678909"


class TestEmail:
    """Testes para o Value Object Email"""
    
    def test_email_valido(self):
        """Testa criação de email válido"""
        email = Email("test@example.com")
        assert email.valor == "test@example.com"
    
    def test_email_invalido(self):
        """Testa email inválido"""
        with pytest.raises(ValueError, match="Email inválido"):
            Email("email_invalido")
    
    def test_email_vazio(self):
        """Testa email vazio"""
        with pytest.raises(ValueError, match="Email inválido"):
            Email("")
    
    def test_email_dominio(self):
        """Testa extração do domínio"""
        email = Email("user@example.com")
        assert email.dominio() == "example.com"
    
    def test_email_usuario(self):
        """Testa extração do usuário"""
        email = Email("user@example.com")
        assert email.usuario() == "user"
    
    def test_email_mascarado(self):
        """Testa email mascarado para logs"""
        email = Email("usuario@example.com")
        assert email.mascarado() == "u***o@example.com"


class TestMoney:
    """Testes para o Value Object Money"""
    
    def test_money_criacao(self):
        """Testa criação de valor monetário"""
        money = Money(Decimal("100.50"))
        assert money.valor == Decimal("100.50")
        assert money.moeda == "BRL"
    
    def test_money_formatado(self):
        """Testa formatação de valor monetário"""
        money = Money(Decimal("1234.56"))
        assert money.formatado() == "R$ 1.234,56"
    
    def test_money_soma(self):
        """Testa soma de valores monetários"""
        money1 = Money(Decimal("100.00"))
        money2 = Money(Decimal("50.00"))
        resultado = money1.somar(money2)
        assert resultado.valor == Decimal("150.00")
    
    def test_money_subtracao(self):
        """Testa subtração de valores monetários"""
        money1 = Money(Decimal("100.00"))
        money2 = Money(Decimal("30.00"))
        resultado = money1.subtrair(money2)
        assert resultado.valor == Decimal("70.00")
    
    def test_money_subtracao_negativa(self):
        """Testa subtração que resultaria em valor negativo"""
        money1 = Money(Decimal("50.00"))
        money2 = Money(Decimal("100.00"))
        with pytest.raises(ValueError, match="Resultado da subtração não pode ser negativo"):
            money1.subtrair(money2)
    
    def test_money_multiplicacao(self):
        """Testa multiplicação de valor monetário"""
        money = Money(Decimal("100.00"))
        resultado = money.multiplicar(2)
        assert resultado.valor == Decimal("200.00")
    
    def test_money_porcentagem(self):
        """Testa cálculo de porcentagem"""
        money = Money(Decimal("100.00"))
        resultado = money.porcentagem(10)  # 10%
        assert resultado.valor == Decimal("10.00")
    
    def test_money_centavos(self):
        """Testa conversão para centavos"""
        money = Money(Decimal("123.45"))
        assert money.centavos() == 12345
    
    def test_money_from_centavos(self):
        """Testa criação a partir de centavos"""
        money = Money.from_centavos(12345)
        assert money.valor == Decimal("123.45")
    
    def test_money_zero(self):
        """Testa valor zero"""
        money = Money.zero()
        assert money.eh_zero()
        assert not money.eh_positivo()
    
    def test_money_valor_negativo(self):
        """Testa que não aceita valor negativo"""
        with pytest.raises(ValueError, match="Valor monetário não pode ser negativo"):
            Money(Decimal("-10.00"))
    
    def test_money_comparacao(self):
        """Testa comparação entre valores"""
        money1 = Money(Decimal("100.00"))
        money2 = Money(Decimal("50.00"))
        money3 = Money(Decimal("100.00"))
        
        assert money1 > money2
        assert money2 < money1
        assert money1 == money3
        assert money1 >= money3
        assert money2 <= money1