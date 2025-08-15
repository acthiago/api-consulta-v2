"""
Interfaces para Serviços de Autenticação
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from ..repositories.cliente_repository import IClienteRepository


class IPasswordService(ABC):
    """Interface para serviço de senhas"""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Gera hash da senha"""
        pass

    @abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica se senha está correta"""
        pass


class IJWTService(ABC):
    """Interface para serviço JWT"""

    @abstractmethod
    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Cria token de acesso"""
        pass

    @abstractmethod
    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Cria token de refresh"""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[dict]:
        """Verifica e decodifica token"""
        pass

    @abstractmethod
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Obtém data de expiração do token"""
        pass


class IAuthService(ABC):
    """Interface para serviço de autenticação"""

    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Autentica usuário com username e senha"""
        pass

    @abstractmethod
    async def get_current_user(self, token: str) -> Optional[dict]:
        """Obtém usuário atual do token"""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[dict]:
        """Renova token usando refresh token"""
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """Revoga token"""
        pass
