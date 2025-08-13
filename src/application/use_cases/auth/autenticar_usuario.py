"""
Use Case: Autenticar Usuário
"""

import structlog
from datetime import datetime, timedelta
from typing import Optional

from ..interfaces.services.auth_service import IAuthService, IJWTService
from ..dtos.auth_dto import LoginDTO, TokenDTO


logger = structlog.get_logger()


class AutenticarUsuarioUseCase:
    """Use Case para autenticação de usuário"""
    
    def __init__(
        self, 
        auth_service: IAuthService,
        jwt_service: IJWTService
    ):
        self.auth_service = auth_service
        self.jwt_service = jwt_service
    
    async def execute(self, request: LoginDTO) -> Optional[TokenDTO]:
        """
        Executa a autenticação do usuário
        
        Args:
            request: DTO com credenciais de login
            
        Returns:
            TokenDTO se autenticação bem-sucedida, None caso contrário
            
        Raises:
            ValueError: Se credenciais forem inválidas
        """
        try:
            logger.info(
                "Iniciando autenticação de usuário",
                username=request.username,
                use_case="AutenticarUsuarioUseCase"
            )
            
            # Validar entrada
            if not request.username or not request.password:
                raise ValueError("Username e password são obrigatórios")
            
            if len(request.username.strip()) < 3:
                raise ValueError("Username deve ter pelo menos 3 caracteres")
            
            if len(request.password) < 6:
                raise ValueError("Password deve ter pelo menos 6 caracteres")
            
            # Autenticar usuário
            user_data = await self.auth_service.authenticate_user(
                request.username.strip(),
                request.password
            )
            
            if not user_data:
                logger.warning(
                    "Tentativa de login inválida",
                    username=request.username
                )
                raise ValueError("Credenciais inválidas")
            
            # Gerar tokens
            access_token_data = {
                "sub": user_data["id"],
                "username": user_data["username"],
                "type": "access"
            }
            
            refresh_token_data = {
                "sub": user_data["id"],
                "username": user_data["username"],
                "type": "refresh"
            }
            
            access_token = self.jwt_service.create_access_token(
                access_token_data,
                expires_delta=timedelta(minutes=30)
            )
            
            refresh_token = self.jwt_service.create_refresh_token(
                refresh_token_data,
                expires_delta=timedelta(days=7)
            )
            
            # Criar DTO de resposta
            token_dto = TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=1800,  # 30 minutos
                user_id=user_data["id"],
                username=user_data["username"]
            )
            
            logger.info(
                "Usuário autenticado com sucesso",
                username=request.username,
                user_id=user_data["id"]
            )
            
            return token_dto
            
        except ValueError as e:
            logger.error(
                "Erro de validação na autenticação",
                username=request.username,
                error=str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado na autenticação",
                username=request.username,
                error=str(e),
                exc_info=True
            )
            raise
