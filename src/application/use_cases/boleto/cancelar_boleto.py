"""
Use Case: Cancelar Boleto
"""

from datetime import datetime
from typing import Optional

import structlog

from ..dtos.boleto_dto import CancelarBoletoResponseDTO
from ..interfaces.repositories.boleto_repository import IBoletoRepository
from ..interfaces.services.cache_service import ICacheService

logger = structlog.get_logger()


class CancelarBoletoUseCase:
    """Use Case para cancelamento de boleto"""

    def __init__(
        self, boleto_repository: IBoletoRepository, cache_service: ICacheService
    ):
        self.boleto_repository = boleto_repository
        self.cache_service = cache_service

    async def execute(
        self, boleto_id: str, motivo: str = None
    ) -> Optional[CancelarBoletoResponseDTO]:
        """
        Executa o cancelamento de boleto

        Args:
            boleto_id: ID do boleto
            motivo: Motivo do cancelamento (opcional)

        Returns:
            CancelarBoletoResponseDTO se cancelado, None se não encontrado

        Raises:
            ValueError: Se ID inválido ou boleto já cancelado/pago
        """
        try:
            logger.info(
                "Iniciando cancelamento de boleto",
                boleto_id=boleto_id,
                use_case="CancelarBoletoUseCase",
            )

            # Validar entrada
            if not boleto_id:
                raise ValueError("ID do boleto é obrigatório")

            # Buscar boleto
            boleto = await self.boleto_repository.buscar_por_id(boleto_id)

            if not boleto:
                logger.info("Boleto não encontrado", boleto_id=boleto_id)
                return None

            # Verificar se pode ser cancelado
            if boleto.status == "cancelado":
                raise ValueError("Boleto já está cancelado")

            if boleto.status == "pago":
                raise ValueError("Não é possível cancelar boleto já pago")

            # Verificar se está vencido
            if boleto.data_vencimento < datetime.utcnow():
                logger.warning(
                    "Tentativa de cancelar boleto vencido",
                    boleto_id=boleto_id,
                    data_vencimento=boleto.data_vencimento.isoformat(),
                )

            # Atualizar status do boleto
            boleto.status = "cancelado"
            boleto.data_cancelamento = datetime.utcnow()
            if motivo:
                boleto.observacoes = (
                    f"{boleto.observacoes or ''}\nCancelado: {motivo}".strip()
                )

            # Salvar alterações
            boleto_atualizado = await self.boleto_repository.salvar(boleto)

            # Invalidar cache
            cache_key = f"boleto:{boleto_id}"
            await self.cache_service.delete(cache_key)

            # Também invalidar cache do cliente
            cliente_cache_key = f"cliente:{boleto.cliente_id}"
            await self.cache_service.delete(cliente_cache_key)

            # Criar DTO de resposta
            response_dto = CancelarBoletoResponseDTO(
                boleto_id=boleto_atualizado.id,
                status=boleto_atualizado.status,
                data_cancelamento=boleto_atualizado.data_cancelamento,
                motivo=motivo,
                mensagem="Boleto cancelado com sucesso",
            )

            logger.info(
                "Boleto cancelado com sucesso",
                boleto_id=boleto_id,
                data_cancelamento=boleto_atualizado.data_cancelamento.isoformat(),
            )

            return response_dto

        except ValueError as e:
            logger.error(
                "Erro de validação no cancelamento de boleto",
                error=str(e),
                boleto_id=boleto_id,
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado no cancelamento de boleto",
                error=str(e),
                boleto_id=boleto_id,
                exc_info=True,
            )
            raise
