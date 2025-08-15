"""
Interfaces de repositório para boletos
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...domain.entities.boleto import Boleto


class IBoletoRepository(ABC):
    """Interface para repositório de boletos"""

    @abstractmethod
    async def salvar(self, boleto: Boleto) -> Boleto:
        """
        Salva ou atualiza um boleto

        Args:
            boleto: Entidade de boleto

        Returns:
            Boleto salvo com ID gerado
        """
        pass

    @abstractmethod
    async def buscar_por_id(self, boleto_id: str) -> Optional[Boleto]:
        """
        Busca boleto por ID

        Args:
            boleto_id: ID do boleto

        Returns:
            Boleto se encontrado, None caso contrário
        """
        pass

    @abstractmethod
    async def buscar_por_linha_digitavel(
        self, linha_digitavel: str
    ) -> Optional[Boleto]:
        """
        Busca boleto por linha digitável

        Args:
            linha_digitavel: Linha digitável do boleto

        Returns:
            Boleto se encontrado, None caso contrário
        """
        pass

    @abstractmethod
    async def buscar_por_cliente(self, cliente_id: str) -> List[Boleto]:
        """
        Busca boletos por cliente

        Args:
            cliente_id: ID do cliente

        Returns:
            Lista de boletos do cliente
        """
        pass

    @abstractmethod
    async def buscar_por_status(self, status: str) -> List[Boleto]:
        """
        Busca boletos por status

        Args:
            status: Status do boleto

        Returns:
            Lista de boletos com o status especificado
        """
        pass

    @abstractmethod
    async def listar_todos(self, skip: int = 0, limit: int = 100) -> List[Boleto]:
        """
        Lista todos os boletos com paginação

        Args:
            skip: Número de registros para pular
            limit: Limite de registros

        Returns:
            Lista de boletos
        """
        pass

    @abstractmethod
    async def deletar(self, boleto_id: str) -> bool:
        """
        Deleta um boleto

        Args:
            boleto_id: ID do boleto

        Returns:
            True se deletado, False se não encontrado
        """
        pass
