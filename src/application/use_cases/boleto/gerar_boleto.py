"""
Use Case: Gerar Boleto
"""

from datetime import datetime, timedelta

import structlog

from ...domain.entities.boleto import Boleto
from ...domain.value_objects.money import Money
from ..dtos.boleto_dto import GerarBoletoRequestDTO, GerarBoletoResponseDTO
from ..interfaces.repositories.boleto_repository import IBoletoRepository
from ..interfaces.repositories.cliente_repository import IClienteRepository
from ..interfaces.services.cache_service import ICacheService

logger = structlog.get_logger()


class GerarBoletoUseCase:
    """Use Case para geração de boleto"""

    def __init__(
        self,
        boleto_repository: IBoletoRepository,
        cliente_repository: IClienteRepository,
        cache_service: ICacheService,
    ):
        self.boleto_repository = boleto_repository
        self.cliente_repository = cliente_repository
        self.cache_service = cache_service

    async def execute(self, request: GerarBoletoRequestDTO) -> GerarBoletoResponseDTO:
        """
        Executa a geração de boleto

        Args:
            request: DTO com dados do boleto

        Returns:
            GerarBoletoResponseDTO com dados do boleto gerado

        Raises:
            ValueError: Se dados de entrada inválidos
            RuntimeError: Se erro na geração
        """
        try:
            logger.info(
                "Iniciando geração de boleto",
                valor=float(request.valor),
                cliente_id=request.cliente_id,
                use_case="GerarBoletoUseCase",
            )

            # Validar entrada
            if request.valor <= 0:
                raise ValueError("Valor do boleto deve ser positivo")

            if not request.cliente_id:
                raise ValueError("ID do cliente é obrigatório")

            if not request.descricao:
                raise ValueError("Descrição do boleto é obrigatória")

            # Verificar se cliente existe
            cliente = await self.cliente_repository.buscar_por_id(request.cliente_id)
            if not cliente:
                raise ValueError(f"Cliente {request.cliente_id} não encontrado")

            # Calcular data de vencimento (padrão: 30 dias)
            dias_vencimento = request.dias_vencimento or 30
            data_vencimento = datetime.utcnow() + timedelta(days=dias_vencimento)

            # Gerar linha digitável e código de barras
            linha_digitavel = self._gerar_linha_digitavel()
            codigo_barras = self._gerar_codigo_barras()

            # Criar entidade de boleto
            valor = Money(request.valor)
            boleto = Boleto(
                id=None,  # Será gerado pelo repositório
                cliente_id=request.cliente_id,
                valor=valor,
                descricao=request.descricao,
                data_emissao=datetime.utcnow(),
                data_vencimento=data_vencimento,
                linha_digitavel=linha_digitavel,
                codigo_barras=codigo_barras,
                status="ativo",
                observacoes=request.observacoes,
            )

            # Validar boleto
            try:
                boleto.validar()
            except ValueError as e:
                raise ValueError(f"Dados de boleto inválidos: {e}")

            # Salvar boleto
            boleto_salvo = await self.boleto_repository.salvar(boleto)

            # Invalidar cache do cliente
            cache_key = f"cliente:{request.cliente_id}"
            await self.cache_service.delete(cache_key)

            # Criar DTO de resposta
            response_dto = GerarBoletoResponseDTO(
                boleto_id=boleto_salvo.id,
                linha_digitavel=boleto_salvo.linha_digitavel,
                codigo_barras=boleto_salvo.codigo_barras,
                valor=float(valor),
                data_emissao=boleto_salvo.data_emissao,
                data_vencimento=boleto_salvo.data_vencimento,
                status=boleto_salvo.status,
                url_pdf=f"/api/v1/boletos/{boleto_salvo.id}/pdf",
            )

            logger.info(
                "Boleto gerado com sucesso",
                boleto_id=boleto_salvo.id,
                valor=float(valor),
                data_vencimento=data_vencimento.isoformat(),
            )

            return response_dto

        except ValueError as e:
            logger.error(
                "Erro de validação na geração de boleto",
                error=str(e),
                cliente_id=request.cliente_id,
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado na geração de boleto",
                error=str(e),
                cliente_id=request.cliente_id,
                exc_info=True,
            )
            raise RuntimeError(f"Erro na geração: {e}")

    def _gerar_linha_digitavel(self) -> str:
        """
        Gera linha digitável do boleto

        Returns:
            String com linha digitável
        """
        # Simulação - em produção seria integração com banco
        import random
        import string

        # Formato simplificado: 5 blocos de 5 dígitos
        blocos = []
        for _ in range(5):
            bloco = "".join(random.choices(string.digits, k=5))
            blocos.append(bloco)

        return " ".join(blocos)

    def _gerar_codigo_barras(self) -> str:
        """
        Gera código de barras do boleto

        Returns:
            String com código de barras
        """
        # Simulação - em produção seria integração com banco
        import random
        import string

        # Código de barras com 44 dígitos
        return "".join(random.choices(string.digits, k=44))
