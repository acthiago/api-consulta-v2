"""
Use Case: Renovar Token
"""

import structlog
from datetime import timedelta
from typing import Optional

from ..interfaces.services.auth_service import IJWTService
from ..dtos.auth_dto import RefreshTokenDTO, TokenDTO


logger = structlog.get_logger()


class RenovarTokenUseCase:
    """Use Case para renovação de token"""
    
    def __init__(self, jwt_service: IJWTService):
        self.jwt_service = jwt_service
    
    async def execute(self, request: RefreshTokenDTO) -> Optional[TokenDTO]:
        """
        Executa a renovação de token
        
        Args:
            request: DTO com refresh token
            
        Returns:
            TokenDTO com novos tokens se válido, None caso contrário
            
        Raises:
            ValueError: Se refresh token for inválido
        """
        try:
            logger.info(
                "Iniciando renovação de token",
                use_case="RenovarTokenUseCase"
            )
            
            # Validar entrada
            if not request.refresh_token:
                raise ValueError("Refresh token é obrigatório")
            
            # Verificar e decodificar refresh token
            token_data = self.jwt_service.verify_token(request.refresh_token)
            
            if not token_data:
                raise ValueError("Refresh token inválido")
            
            # Verificar se é realmente um refresh token
            if token_data.get("type") != "refresh":
                raise ValueError("Token fornecido não é um refresh token")
            
            # Gerar novos tokens
            access_token_data = {
                "sub": token_data["sub"],
                "username": token_data["username"],
                "type": "access"
            }
            
            new_refresh_token_data = {
                "sub": token_data["sub"],
                "username": token_data["username"],
                "type": "refresh"
            }
            
            new_access_token = self.jwt_service.create_access_token(
                access_token_data,
                expires_delta=timedelta(minutes=30)
            )
            
            new_refresh_token = self.jwt_service.create_refresh_token(
                new_refresh_token_data,
                expires_delta=timedelta(days=7)
            )
            
            # Criar DTO de resposta
            token_dto = TokenDTO(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=1800,  # 30 minutos
                user_id=token_data["sub"],
                username=token_data["username"]
            )
            
            logger.info(
                "Token renovado com sucesso",
                user_id=token_data["sub"],
                username=token_data["username"]
            )
            
            return token_dto
            
        except ValueError as e:
            logger.error(
                "Erro de validação na renovação de token",
                error=str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado na renovação de token",
                error=str(e),
                exc_info=True
            )
            raise
