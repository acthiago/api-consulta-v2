"""
Interface para Serviço de Cache
"""

from abc import ABC, abstractmethod
from typing import Optional, Any


class ICacheService(ABC):
    """Interface para serviço de cache"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Obtém valor do cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """Define valor no cache com TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache"""
        pass
    
    @abstractmethod
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalida chaves que correspondem ao padrão"""
        pass
    
    @abstractmethod
    async def get_json(self, key: str) -> Optional[Any]:
        """Obtém e deserializa JSON do cache"""
        pass
    
    @abstractmethod
    async def set_json(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Serializa e armazena JSON no cache"""
        pass
