"""
Use Case: Buscar Cliente por CPF
"""

import structlog
from typing import Optional

from ...domain.entities.cliente import Cliente
from ...domain.value_objects.cpf import CPF
from ..interfaces.repositories.cliente_repository import IClienteRepository
from ..interfaces.services.cache_service import ICacheService
from ..dtos.cliente_dto import ClienteDTO, BuscarClienteDTO


logger = structlog.get_logger()


class BuscarClienteUseCase:
    """Use Case para buscar cliente por CPF"""
    
    def __init__(
        self, 
        cliente_repository: IClienteRepository,
        cache_service: ICacheService
    ):
        self.cliente_repository = cliente_repository
        self.cache_service = cache_service
    
    async def execute(self, request: BuscarClienteDTO) -> Optional[ClienteDTO]:
        """
        Executa a busca de cliente por CPF
        
        Args:
            request: DTO com dados da busca
            
        Returns:
            ClienteDTO se encontrado, None caso contrário
            
        Raises:
            ValueError: Se CPF for inválido
        """
        try:
            # Validar e criar value object CPF
            cpf = CPF(request.cpf)
            
            logger.info(
                "Iniciando busca de cliente",
                cpf=cpf.mascarado(),
                use_case="BuscarClienteUseCase"
            )
            
            # Verificar cache primeiro
            cache_key = f"cliente:cpf:{cpf.limpo()}"
            cached_cliente = await self.cache_service.get_json(cache_key)
            
            if cached_cliente:
                logger.info(
                    "Cliente encontrado no cache",
                    cpf=cpf.mascarado(),
                    cache_hit=True
                )
                return ClienteDTO(**cached_cliente)
            
            # Buscar no repositório
            cliente = await self.cliente_repository.buscar_por_cpf(cpf)
            
            if not cliente:
                logger.info(
                    "Cliente não encontrado",
                    cpf=cpf.mascarado(),
                    cache_hit=False
                )
                return None
            
            # Converter entidade para DTO
            cliente_dto = self._entidade_para_dto(cliente)
            
            # Armazenar no cache
            await self.cache_service.set_json(
                cache_key, 
                cliente_dto.to_dict(), 
                ttl=300  # 5 minutos
            )
            
            logger.info(
                "Cliente encontrado com sucesso",
                cpf=cpf.mascarado(),
                cliente_id=cliente.id,
                cache_hit=False
            )
            
            return cliente_dto
            
        except ValueError as e:
            logger.error(
                "Erro de validação ao buscar cliente",
                cpf=request.cpf,
                error=str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "Erro inesperado ao buscar cliente",
                cpf=request.cpf,
                error=str(e),
                exc_info=True
            )
            raise
    
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
