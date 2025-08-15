"""
Interfaces de repositório para pagamentos
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...domain.entities.pagamento import Pagamento


class IPagamentoRepository(ABC):
    """Interface para repositório de pagamentos"""

    @abstractmethod
    async def salvar(self, pagamento: Pagamento) -> Pagamento:
        """
        Salva ou atualiza um pagamento

        Args:
            pagamento: Entidade de pagamento

        Returns:
            Pagamento salvo com ID gerado
        """
        pass

    @abstractmethod
    async def buscar_por_id(self, pagamento_id: str) -> Optional[Pagamento]:
        """
        Busca pagamento por ID

        Args:
            pagamento_id: ID do pagamento

        Returns:
            Pagamento se encontrado, None caso contrário
        """
        pass

    @abstractmethod
    async def buscar_por_cliente(self, cliente_id: str) -> List[Pagamento]:
        """
        Busca pagamentos por cliente

        Args:
            cliente_id: ID do cliente

        Returns:
            Lista de pagamentos do cliente
        """
        pass

    @abstractmethod
    async def buscar_por_status(self, status: str) -> List[Pagamento]:
        """
        Busca pagamentos por status

        Args:
            status: Status do pagamento

        Returns:
            Lista de pagamentos com o status especificado
        """
        pass

    @abstractmethod
    async def listar_todos(self, skip: int = 0, limit: int = 100) -> List[Pagamento]:
        """
        Lista todos os pagamentos com paginação

        Args:
            skip: Número de registros para pular
            limit: Limite de registros

        Returns:
            Lista de pagamentos
        """
        pass

    @abstractmethod
    async def deletar(self, pagamento_id: str) -> bool:
        """
        Deleta um pagamento

        Args:
            pagamento_id: ID do pagamento

        Returns:
            True se deletado, False se não encontrado
        """
        pass
