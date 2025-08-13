"""
Interface do Repositório de Cliente
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ...domain.entities.cliente import Cliente
from ...domain.value_objects.cpf import CPF


class IClienteRepository(ABC):
    """Interface para repositório de Cliente"""
    
    @abstractmethod
    async def buscar_por_cpf(self, cpf: CPF) -> Optional[Cliente]:
        """Busca cliente por CPF"""
        pass
    
    @abstractmethod
    async def buscar_por_id(self, cliente_id: str) -> Optional[Cliente]:
        """Busca cliente por ID"""
        pass
    
    @abstractmethod
    async def buscar_por_email(self, email: str) -> Optional[Cliente]:
        """Busca cliente por email"""
        pass
    
    @abstractmethod
    async def criar(self, cliente: Cliente) -> Cliente:
        """Cria um novo cliente"""
        pass
    
    @abstractmethod
    async def atualizar(self, cliente: Cliente) -> Cliente:
        """Atualiza um cliente existente"""
        pass
    
    @abstractmethod
    async def excluir(self, cliente_id: str) -> bool:
        """Exclui um cliente"""
        pass
    
    @abstractmethod
    async def listar(
        self, 
        filtros: dict = None, 
        offset: int = 0, 
        limit: int = 20
    ) -> List[Cliente]:
        """Lista clientes com filtros e paginação"""
        pass
    
    @abstractmethod
    async def contar(self, filtros: dict = None) -> int:
        """Conta total de clientes com filtros"""
        pass
    
    @abstractmethod
    async def existe_cpf(self, cpf: CPF) -> bool:
        """Verifica se CPF já existe"""
        pass
    
    @abstractmethod
    async def existe_email(self, email: str) -> bool:
        """Verifica se email já existe"""
        pass
