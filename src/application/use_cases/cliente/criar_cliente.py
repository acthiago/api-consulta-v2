"""
Use Case: Criar Cliente
"""

from datetime import datetime

import structlog

from ...domain.entities.cliente import Cliente
from ...domain.value_objects.cpf import CPF
from ...domain.value_objects.email import Email
from ..dtos.cliente_dto import ClienteDTO, CriarClienteDTO
from ..interfaces.repositories.cliente_repository import IClienteRepository
from ..interfaces.services.cache_service import ICacheService

logger = structlog.get_logger()


class CriarClienteUseCase:
    """Use Case para criar novo cliente"""

    def __init__(
        self, cliente_repository: IClienteRepository, cache_service: ICacheService
    ):
        self.cliente_repository = cliente_repository
        self.cache_service = cache_service

    async def execute(self, request: CriarClienteDTO) -> ClienteDTO:
        """
        Executa a criação de um novo cliente

        Args:
            request: DTO com dados do cliente a ser criado

        Returns:
            ClienteDTO do cliente criado

        Raises:
            ValueError: Se dados forem inválidos
            Exception: Se CPF ou email já existirem
        """
        try:
            logger.info(
                "Iniciando criação de cliente",
                cpf_mascarado=CPF(request.cpf).mascarado(),
                email=request.email,
                use_case="CriarClienteUseCase",
            )

            # Criar value objects e validar
            cpf = CPF(request.cpf)
            email = Email(request.email)

            # Verificar se CPF já existe
            if await self.cliente_repository.existe_cpf(cpf):
                raise ValueError(f"CPF {cpf.mascarado()} já está cadastrado")

            # Verificar se email já existe
            if await self.cliente_repository.existe_email(email.valor):
                raise ValueError(f"Email {email.mascarado()} já está cadastrado")

            # Criar entidade Cliente
            cliente = Cliente(
                cpf=cpf,
                nome=request.nome.strip(),
                email=email,
                telefone=request.telefone.strip(),
                endereco=request.endereco.strip(),
            )

            # Persistir no repositório
            cliente_criado = await self.cliente_repository.criar(cliente)

            # Converter para DTO
            cliente_dto = self._entidade_para_dto(cliente_criado)

            # Invalidar cache relacionado
            await self._invalidar_cache(cpf)

            logger.info(
                "Cliente criado com sucesso",
                cliente_id=cliente_criado.id,
                cpf=cpf.mascarado(),
                email=email.mascarado(),
            )

            return cliente_dto

        except ValueError as e:
            logger.error(
                "Erro de validação ao criar cliente",
                cpf=request.cpf,
                email=request.email,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado ao criar cliente",
                cpf=request.cpf,
                email=request.email,
                error=str(e),
                exc_info=True,
            )
            raise

    async def _invalidar_cache(self, cpf: CPF):
        """Invalida cache relacionado ao cliente"""
        cache_key = f"cliente:cpf:{cpf.limpo()}"
        await self.cache_service.delete(cache_key)

        # Invalidar listagens
        await self.cache_service.invalidate_pattern("clientes:lista:*")

    def _entidade_para_dto(self, cliente: Cliente) -> ClienteDTO:
        """Converte entidade Cliente para DTO"""
        return ClienteDTO(
            id=cliente.id,
            cpf=cliente.cpf.formatado(),
            nome=cliente.nome,
            email=cliente.email.valor,
            telefone=cliente.telefone,
            endereco=cliente.endereco,
            data_cadastro=cliente.data_cadastro,
            data_atualizacao=cliente.data_atualizacao,
            ativo=cliente.ativo,
            dividas_ids=cliente.dividas_ids,
            historico_interacoes=cliente.historico_interacoes,
        )
