"""
Use Case: Consultar Pagamento
"""

from typing import Optional

import structlog

from ..dtos.pagamento_dto import ConsultarPagamentoResponseDTO
from ..interfaces.repositories.pagamento_repository import IPagamentoRepository
from ..interfaces.services.cache_service import ICacheService

logger = structlog.get_logger()


class ConsultarPagamentoUseCase:
    """Use Case para consulta de pagamento"""

    def __init__(
        self, pagamento_repository: IPagamentoRepository, cache_service: ICacheService
    ):
        self.pagamento_repository = pagamento_repository
        self.cache_service = cache_service

    async def execute(
        self, pagamento_id: str
    ) -> Optional[ConsultarPagamentoResponseDTO]:
        """
        Executa a consulta de pagamento

        Args:
            pagamento_id: ID do pagamento

        Returns:
            ConsultarPagamentoResponseDTO se encontrado, None caso contrário

        Raises:
            ValueError: Se ID inválido
        """
        try:
            logger.info(
                "Iniciando consulta de pagamento",
                pagamento_id=pagamento_id,
                use_case="ConsultarPagamentoUseCase",
            )

            # Validar entrada
            if not pagamento_id:
                raise ValueError("ID do pagamento é obrigatório")

            # Verificar cache primeiro
            cache_key = f"pagamento:{pagamento_id}"
            cached_result = await self.cache_service.get(cache_key)

            if cached_result:
                logger.info("Pagamento encontrado no cache", pagamento_id=pagamento_id)
                return ConsultarPagamentoResponseDTO.from_dict(cached_result)

            # Buscar no repositório
            pagamento = await self.pagamento_repository.buscar_por_id(pagamento_id)

            if not pagamento:
                logger.info("Pagamento não encontrado", pagamento_id=pagamento_id)
                return None

            # Criar DTO de resposta
            response_dto = ConsultarPagamentoResponseDTO(
                pagamento_id=pagamento.id,
                cliente_id=pagamento.cliente_id,
                valor=float(pagamento.valor.amount),
                metodo=pagamento.metodo,
                status=pagamento.status,
                descricao=pagamento.descricao,
                data_pagamento=pagamento.data_pagamento,
                data_processamento=pagamento.data_processamento,
                codigo_transacao=pagamento.codigo_transacao,
            )

            # Salvar no cache por 30 minutos
            await self.cache_service.set(cache_key, response_dto.to_dict(), ttl=1800)

            logger.info(
                "Pagamento consultado com sucesso",
                pagamento_id=pagamento_id,
                status=pagamento.status,
            )

            return response_dto

        except ValueError as e:
            logger.error(
                "Erro de validação na consulta de pagamento",
                error=str(e),
                pagamento_id=pagamento_id,
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado na consulta de pagamento",
                error=str(e),
                pagamento_id=pagamento_id,
                exc_info=True,
            )
            raise
