# 📖 API Reference - v2.0

## 🏗️ Arquitetura de Use Cases Implementados

### 🔐 Módulo de Autenticação

#### `AutenticarUsuarioUseCase`
**Arquivo**: `src/application/use_cases/auth/autenticar_usuario.py`

```python
# Entrada
LoginRequestDTO(username: str, password: str)

# Saída  
TokenDTO(
    access_token: str,
    refresh_token: str,
    token_type: str,
    expires_in: int,
    user_id: str,
    username: str
)
```

**Funcionalidades**:
- ✅ Validação de credenciais
- ✅ Hash bcrypt para senhas
- ✅ Geração de access/refresh tokens
- ✅ TTL configurável (30min access, 7 dias refresh)
- ✅ Logs estruturados de auditoria

#### `RenovarTokenUseCase`
**Arquivo**: `src/application/use_cases/auth/renovar_token.py`

```python
# Entrada
RefreshTokenDTO(refresh_token: str)

# Saída
TokenDTO(...)  # Novos tokens gerados
```

**Funcionalidades**:
- ✅ Validação de refresh token
- ✅ Verificação de tipo de token
- ✅ Geração de novos access/refresh tokens
- ✅ Invalidação automática do token anterior

### 👥 Módulo de Clientes

#### `BuscarClienteUseCase`
**Arquivo**: `src/application/use_cases/cliente/buscar_cliente.py`

```python
# Entrada
cliente_id: str

# Saída
BuscarClienteResponseDTO(
    cliente_id: str,
    nome: str,
    cpf: str,
    email: str,
    telefone: str,
    endereco: EnderecoDTO,
    data_cadastro: datetime,
    status: str
)
```

**Funcionalidades**:
- ✅ Cache Redis com TTL de 30 minutos
- ✅ Fallback para repositório se não estiver em cache
- ✅ Logs de performance e cache hits
- ✅ Validação de entrada

#### `CriarClienteUseCase`
**Arquivo**: `src/application/use_cases/cliente/criar_cliente.py`

```python
# Entrada
CriarClienteRequestDTO(
    nome: str,
    cpf: str,
    email: str,
    telefone: str,
    endereco: EnderecoDTO
)

# Saída
CriarClienteResponseDTO(
    cliente_id: str,
    mensagem: str,
    data_cadastro: datetime
)
```

**Funcionalidades**:
- ✅ Validação de CPF usando algoritmo oficial
- ✅ Validação de email com regex
- ✅ Verificação de duplicatas
- ✅ Criação de entidade de domínio
- ✅ Geração automática de UUID

#### `AtualizarClienteUseCase`
**Arquivo**: `src/application/use_cases/cliente/atualizar_cliente.py`

```python
# Entrada
AtualizarClienteRequestDTO(
    cliente_id: str,
    nome: Optional[str],
    email: Optional[str],
    telefone: Optional[str],
    endereco: Optional[EnderecoDTO]
)

# Saída
AtualizarClienteResponseDTO(
    cliente_id: str,
    mensagem: str,
    data_atualizacao: datetime
)
```

**Funcionalidades**:
- ✅ Atualização parcial (campos opcionais)
- ✅ Invalidação de cache após atualização
- ✅ Validação de dados atualizados
- ✅ Preservação de dados não alterados

### 💳 Módulo de Pagamentos

#### `ProcessarPagamentoUseCase`
**Arquivo**: `src/application/use_cases/pagamento/processar_pagamento.py`

```python
# Entrada
ProcessarPagamentoRequestDTO(
    cliente_id: str,
    valor: float,
    metodo: str,  # cartao_credito, pix, boleto, etc.
    descricao: str
)

# Saída
ProcessarPagamentoResponseDTO(
    pagamento_id: str,
    status: str,  # aprovado, rejeitado
    valor: float,
    data_processamento: datetime,
    codigo_transacao: Optional[str],
    mensagem: str
)
```

**Funcionalidades**:
- ✅ Validação de cliente existente
- ✅ Regras de negócio para aprovação/rejeição
- ✅ Geração de códigos de transação únicos
- ✅ Invalidação de cache do cliente
- ✅ Auditoria completa do processamento

#### `ConsultarPagamentoUseCase`
**Arquivo**: `src/application/use_cases/pagamento/consultar_pagamento.py`

```python
# Entrada
pagamento_id: str

# Saída
ConsultarPagamentoResponseDTO(
    pagamento_id: str,
    cliente_id: str,
    valor: float,
    metodo: str,
    status: str,
    descricao: str,
    data_pagamento: datetime,
    data_processamento: Optional[datetime],
    codigo_transacao: Optional[str]
)
```

**Funcionalidades**:
- ✅ Cache Redis com TTL de 30 minutos
- ✅ Busca otimizada por ID
- ✅ Serialização/deserialização automática
- ✅ Logs de performance

### 📄 Módulo de Boletos

#### `GerarBoletoUseCase`
**Arquivo**: `src/application/use_cases/boleto/gerar_boleto.py`

```python
# Entrada
GerarBoletoRequestDTO(
    cliente_id: str,
    valor: float,
    descricao: str,
    dias_vencimento: Optional[int] = 30,
    observacoes: Optional[str]
)

# Saída
GerarBoletoResponseDTO(
    boleto_id: str,
    linha_digitavel: str,
    codigo_barras: str,
    valor: float,
    data_emissao: datetime,
    data_vencimento: datetime,
    status: str,
    url_pdf: str
)
```

**Funcionalidades**:
- ✅ Geração de linha digitável simulada
- ✅ Geração de código de barras simulado
- ✅ Cálculo automático de vencimento
- ✅ Validação de cliente existente
- ✅ URL para PDF gerada automaticamente

#### `ConsultarBoletoUseCase`
**Arquivo**: `src/application/use_cases/boleto/consultar_boleto.py`

```python
# Entrada
boleto_id: str

# Saída
ConsultarBoletoResponseDTO(
    boleto_id: str,
    cliente_id: str,
    valor: float,
    descricao: str,
    data_emissao: datetime,
    data_vencimento: datetime,
    linha_digitavel: str,
    codigo_barras: str,
    status: str,
    observacoes: Optional[str],
    url_pdf: str
)
```

**Funcionalidades**:
- ✅ Cache Redis com TTL de 1 hora
- ✅ Busca otimizada por ID
- ✅ URL de PDF dinâmica
- ✅ Status automático (ativo, vencido, pago, cancelado)

#### `CancelarBoletoUseCase`
**Arquivo**: `src/application/use_cases/boleto/cancelar_boleto.py`

```python
# Entrada
boleto_id: str
motivo: Optional[str]

# Saída
CancelarBoletoResponseDTO(
    boleto_id: str,
    status: str,
    data_cancelamento: datetime,
    motivo: Optional[str],
    mensagem: str
)
```

**Funcionalidades**:
- ✅ Validação de status (não pode cancelar se já pago)
- ✅ Atualização de status para "cancelado"
- ✅ Registro de motivo nas observações
- ✅ Invalidação de cache (boleto + cliente)
- ✅ Data de cancelamento automática

## 🔧 Interfaces de Repositório

### `IClienteRepository`
```python
async def salvar(cliente: Cliente) -> Cliente
async def buscar_por_id(cliente_id: str) -> Optional[Cliente]
async def buscar_por_cpf(cpf: str) -> Optional[Cliente]
async def listar_todos(skip: int, limit: int) -> List[Cliente]
async def deletar(cliente_id: str) -> bool
```

### `IPagamentoRepository`
```python
async def salvar(pagamento: Pagamento) -> Pagamento
async def buscar_por_id(pagamento_id: str) -> Optional[Pagamento]
async def buscar_por_cliente(cliente_id: str) -> List[Pagamento]
async def buscar_por_status(status: str) -> List[Pagamento]
async def listar_todos(skip: int, limit: int) -> List[Pagamento]
async def deletar(pagamento_id: str) -> bool
```

### `IBoletoRepository`
```python
async def salvar(boleto: Boleto) -> Boleto
async def buscar_por_id(boleto_id: str) -> Optional[Boleto]
async def buscar_por_linha_digitavel(linha_digitavel: str) -> Optional[Boleto]
async def buscar_por_cliente(cliente_id: str) -> List[Boleto]
async def buscar_por_status(status: str) -> List[Boleto]
async def listar_todos(skip: int, limit: int) -> List[Boleto]
async def deletar(boleto_id: str) -> bool
```

## 🛠️ Interfaces de Serviços

### `IJWTService`
```python
def create_access_token(data: dict, expires_delta: timedelta) -> str
def create_refresh_token(data: dict, expires_delta: timedelta) -> str
def verify_token(token: str) -> Optional[dict]
def decode_token(token: str) -> dict
```

### `ICacheService`
```python
async def get(key: str) -> Optional[dict]
async def set(key: str, value: dict, ttl: int) -> bool
async def delete(key: str) -> bool
async def exists(key: str) -> bool
async def clear_pattern(pattern: str) -> int
```

## 📊 DTOs (Data Transfer Objects)

### Módulo Cliente
- `BuscarClienteResponseDTO`
- `CriarClienteRequestDTO` / `CriarClienteResponseDTO`
- `AtualizarClienteRequestDTO` / `AtualizarClienteResponseDTO`
- `EnderecoDTO`

### Módulo Auth
- `LoginRequestDTO`
- `RefreshTokenDTO` 
- `TokenDTO`

### Módulo Pagamento
- `ProcessarPagamentoRequestDTO` / `ProcessarPagamentoResponseDTO`
- `ConsultarPagamentoResponseDTO`

### Módulo Boleto
- `GerarBoletoRequestDTO` / `GerarBoletoResponseDTO`
- `ConsultarBoletoResponseDTO`
- `CancelarBoletoResponseDTO`

## 🔍 Logging e Observabilidade

Todos os use cases implementam:
- ✅ **Logs estruturados** com structlog
- ✅ **Contexto de operação** (use_case, IDs, valores)
- ✅ **Métricas de performance** (tempo de execução)
- ✅ **Tratamento de erros** com stack traces
- ✅ **Auditoria de operações** (quem, quando, o que)

## 🚀 Próximos Passos

1. **Infrastructure Layer** - Implementar repositórios MongoDB e serviços Redis/JWT
2. **Presentation Layer** - Refatorar controllers FastAPI para usar os use cases
3. **Testes** - Expandir cobertura de testes unitários para os use cases
4. **Documentação** - Gerar OpenAPI specs automáticos
