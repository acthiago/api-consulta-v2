"""
DTOs para Autenticação - Data Transfer Objects
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LoginDTO:
    """DTO para login de usuário"""
    
    username: str
    password: str


@dataclass
class TokenDTO:
    """DTO para token de autenticação"""
    
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: str
    username: str


@dataclass
class RefreshTokenDTO:
    """DTO para renovação de token"""
    
    refresh_token: str


@dataclass
class UserInfoDTO:
    """DTO para informações do usuário autenticado"""
    
    id: str
    username: str
    email: str
    ativo: bool
    data_ultimo_login: Optional[datetime]
    roles: list[str]
