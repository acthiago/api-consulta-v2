"""
Use Case: Atualizar Cliente
"""

import structlog
from typing import Optional

from ...domain.entities.cliente import Cliente
from ...domain.value_objects.cpf import CPF
from ...domain.value_objects.email import Email
from ..interfaces.repositories.cliente_repository import IClienteRepository
from ..interfaces.services.cache_service import ICacheService
from ..dtos.cliente_dto import ClienteDTO, AtualizarClienteDTO


logger = structlog.get_logger()


class AtualizarClienteUseCase:
    """Use Case para atualizar dados do cliente"""
    
    def __init__(
        self, 
        cliente_repository: IClienteRepository,
        cache_service: ICacheService
    ):
        self.cliente_repository = cliente_repository
        self.cache_service = cache_service
    
    async def execute(self, cliente_id: str, request: AtualizarClienteDTO) -> ClienteDTO:
        """
        Executa a atualização de dados do cliente
        
        Args:
            cliente_id: ID do cliente a ser atualizado
            request: DTO com dados a serem atualizados
            
        Returns:
            ClienteDTO do cliente atualizado
            
        Raises:
            ValueError: Se dados forem inválidos
            Exception: Se cliente não for encontrado
        """
        try:
            logger.info(
                "Iniciando atualização de cliente",
                cliente_id=cliente_id,
                use_case="AtualizarClienteUseCase"
            )
            
            # Buscar cliente existente
            cliente = await self.cliente_repository.buscar_por_id(cliente_id)
            if not cliente:
                raise ValueError(f"Cliente com ID {cliente_id} não encontrado")
            
            # Preparar dados para atualização
            nome = request.nome.strip() if request.nome else None
            email_obj = Email(request.email) if request.email else None
            telefone = request.telefone.strip() if request.telefone else None
            endereco = request.endereco.strip() if request.endereco else None
            
            # Verificar se novo email já existe (se foi fornecido)
            if email_obj and email_obj.valor != cliente.email.valor:
                if await self.cliente_repository.existe_email(email_obj.valor):
                    raise ValueError(f"Email {email_obj.mascarado()} já está em uso")
            
            # Atualizar dados do cliente
            cliente.atualizar_dados_pessoais(
                nome=nome,
                email=email_obj,
                telefone=telefone,
                endereco=endereco
            )
            
            # Persistir alterações
            cliente_atualizado = await self.cliente_repository.atualizar(cliente)
            
            # Converter para DTO
            cliente_dto = self._entidade_para_dto(cliente_atualizado)
            
            # Invalidar cache
            await self._invalidar_cache(cliente.cpf)
            
            logger.info(
                "Cliente atualizado com sucesso",
                cliente_id=cliente_id,
                cpf=cliente.cpf.mascarado()
            )
            
            return cliente_dto
            
        except ValueError as e:
            logger.error(
                "Erro de validação ao atualizar cliente",
                cliente_id=cliente_id,
                error=str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado ao atualizar cliente",
                cliente_id=cliente_id,
                error=str(e),
                exc_info=True
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
            historico_interacoes=cliente.historico_interacoes
        )
