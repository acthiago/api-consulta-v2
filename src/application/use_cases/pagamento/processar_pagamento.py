"""
Use Case: Processar Pagamento
"""

from datetime import datetime

import structlog

from ...domain.entities.pagamento import Pagamento
from ...domain.value_objects.money import Money
from ..dtos.pagamento_dto import (
    ProcessarPagamentoRequestDTO,
    ProcessarPagamentoResponseDTO,
)
from ..interfaces.repositories.cliente_repository import IClienteRepository
from ..interfaces.repositories.pagamento_repository import IPagamentoRepository
from ..interfaces.services.cache_service import ICacheService

logger = structlog.get_logger()


class ProcessarPagamentoUseCase:
    """Use Case para processamento de pagamento"""

    def __init__(
        self,
        pagamento_repository: IPagamentoRepository,
        cliente_repository: IClienteRepository,
        cache_service: ICacheService,
    ):
        self.pagamento_repository = pagamento_repository
        self.cliente_repository = cliente_repository
        self.cache_service = cache_service

    async def execute(
        self, request: ProcessarPagamentoRequestDTO
    ) -> ProcessarPagamentoResponseDTO:
        """
        Executa o processamento de pagamento

        Args:
            request: DTO com dados do pagamento

        Returns:
            ProcessarPagamentoResponseDTO com resultado do processamento

        Raises:
            ValueError: Se dados de entrada inválidos
            RuntimeError: Se erro no processamento
        """
        try:
            logger.info(
                "Iniciando processamento de pagamento",
                valor=float(request.valor),
                cliente_id=request.cliente_id,
                use_case="ProcessarPagamentoUseCase",
            )

            # Validar entrada
            if request.valor <= 0:
                raise ValueError("Valor do pagamento deve ser positivo")

            if not request.cliente_id:
                raise ValueError("ID do cliente é obrigatório")

            # Verificar se cliente existe
            cliente = await self.cliente_repository.buscar_por_id(request.cliente_id)
            if not cliente:
                raise ValueError(f"Cliente {request.cliente_id} não encontrado")

            # Criar entidade de pagamento
            valor = Money(request.valor)
            pagamento = Pagamento(
                id=None,  # Será gerado pelo repositório
                cliente_id=request.cliente_id,
                valor=valor,
                metodo=request.metodo,
                descricao=request.descricao,
                data_pagamento=datetime.utcnow(),
                status="processando",
            )

            # Validar pagamento
            try:
                pagamento.validar()
            except ValueError as e:
                raise ValueError(f"Dados de pagamento inválidos: {e}")

            # Processar pagamento (lógica de negócio)
            sucesso = await self._processar_pagamento_interno(pagamento)

            if sucesso:
                pagamento.status = "aprovado"
                pagamento.data_processamento = datetime.utcnow()

                # Salvar pagamento
                pagamento_salvo = await self.pagamento_repository.salvar(pagamento)

                # Invalidar cache do cliente
                cache_key = f"cliente:{request.cliente_id}"
                await self.cache_service.delete(cache_key)

                logger.info(
                    "Pagamento processado com sucesso",
                    pagamento_id=pagamento_salvo.id,
                    valor=float(valor),
                    status="aprovado",
                )

                return ProcessarPagamentoResponseDTO(
                    pagamento_id=pagamento_salvo.id,
                    status="aprovado",
                    valor=float(valor),
                    data_processamento=pagamento_salvo.data_processamento,
                    codigo_transacao=pagamento_salvo.codigo_transacao,
                    mensagem="Pagamento processado com sucesso",
                )
            else:
                pagamento.status = "rejeitado"
                pagamento.data_processamento = datetime.utcnow()

                # Salvar mesmo pagamento rejeitado para auditoria
                pagamento_salvo = await self.pagamento_repository.salvar(pagamento)

                logger.warning(
                    "Pagamento rejeitado",
                    pagamento_id=pagamento_salvo.id,
                    valor=float(valor),
                    status="rejeitado",
                )

                return ProcessarPagamentoResponseDTO(
                    pagamento_id=pagamento_salvo.id,
                    status="rejeitado",
                    valor=float(valor),
                    data_processamento=pagamento_salvo.data_processamento,
                    codigo_transacao=None,
                    mensagem="Pagamento rejeitado",
                )

        except ValueError as e:
            logger.error(
                "Erro de validação no processamento de pagamento",
                error=str(e),
                cliente_id=request.cliente_id,
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado no processamento de pagamento",
                error=str(e),
                cliente_id=request.cliente_id,
                exc_info=True,
            )
            raise RuntimeError(f"Erro no processamento: {e}")

    async def _processar_pagamento_interno(self, pagamento: Pagamento) -> bool:
        """
        Lógica interna de processamento de pagamento

        Args:
            pagamento: Entidade de pagamento

        Returns:
            True se aprovado, False se rejeitado
        """
        # Simular processamento (em produção seria integração com gateway)
        # Regras de negócio para aprovação/rejeição

        # Exemplo: rejeitar valores muito altos sem validação adicional
        if pagamento.valor.amount > 10000:
            return False

        # Exemplo: aprovar automaticamente valores baixos
        if pagamento.valor.amount < 100:
            return True

        # Para valores intermediários, simular 90% de aprovação
        import random

        return random.random() > 0.1
