"""
Use Case: Consultar Boleto
"""

import structlog
from typing import Optional

from ..interfaces.repositories.boleto_repository import IBoletoRepository
from ..interfaces.services.cache_service import ICacheService
from ..dtos.boleto_dto import ConsultarBoletoResponseDTO


logger = structlog.get_logger()


class ConsultarBoletoUseCase:
    """Use Case para consulta de boleto"""
    
    def __init__(
        self,
        boleto_repository: IBoletoRepository,
        cache_service: ICacheService
    ):
        self.boleto_repository = boleto_repository
        self.cache_service = cache_service
    
    async def execute(self, boleto_id: str) -> Optional[ConsultarBoletoResponseDTO]:
        """
        Executa a consulta de boleto
        
        Args:
            boleto_id: ID do boleto
            
        Returns:
            ConsultarBoletoResponseDTO se encontrado, None caso contrário
            
        Raises:
            ValueError: Se ID inválido
        """
        try:
            logger.info(
                "Iniciando consulta de boleto",
                boleto_id=boleto_id,
                use_case="ConsultarBoletoUseCase"
            )
            
            # Validar entrada
            if not boleto_id:
                raise ValueError("ID do boleto é obrigatório")
            
            # Verificar cache primeiro
            cache_key = f"boleto:{boleto_id}"
            cached_result = await self.cache_service.get(cache_key)
            
            if cached_result:
                logger.info(
                    "Boleto encontrado no cache",
                    boleto_id=boleto_id
                )
                return ConsultarBoletoResponseDTO.from_dict(cached_result)
            
            # Buscar no repositório
            boleto = await self.boleto_repository.buscar_por_id(boleto_id)
            
            if not boleto:
                logger.info(
                    "Boleto não encontrado",
                    boleto_id=boleto_id
                )
                return None
            
            # Criar DTO de resposta
            response_dto = ConsultarBoletoResponseDTO(
                boleto_id=boleto.id,
                cliente_id=boleto.cliente_id,
                valor=float(boleto.valor.amount),
                descricao=boleto.descricao,
                data_emissao=boleto.data_emissao,
                data_vencimento=boleto.data_vencimento,
                linha_digitavel=boleto.linha_digitavel,
                codigo_barras=boleto.codigo_barras,
                status=boleto.status,
                observacoes=boleto.observacoes,
                url_pdf=f"/api/v1/boletos/{boleto.id}/pdf"
            )
            
            # Salvar no cache por 1 hora
            await self.cache_service.set(
                cache_key,
                response_dto.to_dict(),
                ttl=3600
            )
            
            logger.info(
                "Boleto consultado com sucesso",
                boleto_id=boleto_id,
                status=boleto.status
            )
            
            return response_dto
            
        except ValueError as e:
            logger.error(
                "Erro de validação na consulta de boleto",
                error=str(e),
                boleto_id=boleto_id
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado na consulta de boleto",
                error=str(e),
                boleto_id=boleto_id,
                exc_info=True
            )
            raise
