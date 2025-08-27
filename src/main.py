"""
API de Consulta de Boletos - v2
Arquitetura Hexagonal com segurança e performance aprimoradas
"""

import os
import random
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import structlog
import uvicorn
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel
from pymongo import MongoClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Pydantic Models


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    message: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "access_token": "jwt_token_example_admin",
                "token_type": "bearer",
                "expires_in": 1800,
                "message": "Login realizado com sucesso"
            }
        }


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class ClienteResponse(BaseModel):
    cpf: str
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[str] = None
    status: str
    endereco: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DividaResponse(BaseModel):
    id: str
    tipo: str  # "emprestimo", "cartao_credito", "cheque_especial", "financiamento", "outros"
    descricao: str
    valor_original: float
    valor_atual: float  # Com juros, multas, etc.
    data_vencimento: str
    dias_atraso: int
    status: str  # "ativo", "vencido", "negociado", "quitado"
    juros_mes: Optional[float] = None
    multa: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BoletoResponse(BaseModel):
    id: str
    numero_boleto: str
    divida_id: Optional[str] = None  # Referência à dívida que gerou este boleto
    valor: float
    data_vencimento: str
    linha_digitavel: str
    codigo_barras: str
    banco: str
    status: str  # "ativo", "pago", "cancelado", "vencido"
    url_pagamento: Optional[str] = None


class DividasClienteResponse(BaseModel):
    cliente_cpf: str
    cliente_nome: str
    total_dividas: int
    valor_total_original: float
    valor_total_atual: float  # Com juros e multas
    dividas_ativas: int
    dividas_vencidas: int
    dividas: List[DividaResponse]


class BoletoRequest(BaseModel):
    cliente_cpf: str
    dividas_ids: List[str]  # IDs das dívidas para incluir no boleto
    parcelas: int = 1  # Número de parcelas (1 a 5)
    descricao: Optional[str] = "Pagamento de dívidas"


class BoletoGeradoResponse(BaseModel):
    id: str
    numero_boleto: str
    valor_total: float
    valor_parcela: float
    parcelas: int
    data_vencimento: str
    linha_digitavel: str
    codigo_barras: str
    banco: str
    url_pagamento: str
    dividas_incluidas: List[str]  # IDs das dívidas incluídas
    message: str


class PagamentoStatusResponse(BaseModel):
    id: str
    status: str
    valor: Optional[float] = None
    data_pagamento: Optional[str] = None
    message: Optional[str] = None


class BoletoCanceladoResponse(BaseModel):
    boleto_id: str
    status: str
    data_cancelamento: str
    dividas_restauradas: List[str]  # IDs das dívidas que voltaram ao estado original
    historico_preservado: bool
    message: str


class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str
    environment: Optional[str] = None
    checks: Optional[dict] = None


class ApiInfoResponse(BaseModel):
    name: str
    version: str
    description: str
    docs_url: Optional[str] = None
    health_url: str
    metrics_url: Optional[str] = None
    environment: str


# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")
ACTIVE_CONNECTIONS = Counter("active_connections_total", "Active connections")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Simple settings for testing


class Settings:
    APP_NAME = "API Consulta v2"
    APP_DESCRIPTION = "Sistema Completo de Gestão Financeira"
    APP_VERSION = "2.1.0"
    DOCS_URL = "/docs"
    REDOC_URL = "/redoc"
    ENABLE_DOCS = True
    ENABLE_CORS = True
    CORS_ORIGINS = ["*"]
    ENVIRONMENT = "development"
    ENABLE_METRICS = True
    METRICS_PATH = "/metrics"


settings = Settings()

# MongoDB Connection


def get_mongodb_connection():
    """Get MongoDB connection"""
    # Load environment variables
    load_dotenv('/app/scripts/database/.env')

    mongo_uri = os.getenv('MONGO_URI')
    database_name = os.getenv('DATABASE_NAME', 'api_consulta_v2')

    if not mongo_uri:
        raise ValueError("MONGO_URI não encontrado nas variáveis de ambiente")

    client = MongoClient(mongo_uri)
    return client[database_name]


# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def validate_cpf(cpf: str) -> bool:
    """
    Valida um CPF usando o algoritmo oficial brasileiro
    """
    import re

    # Remove caracteres não numéricos
    cpf = re.sub(r'[^\d]', '', cpf)

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se não são todos iguais
    if cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    digito1 = 0 if resto >= 10 else resto

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    digito2 = 0 if resto >= 10 else resto

    # Verifica se os dígitos são corretos
    return int(cpf[9]) == digito1 and int(cpf[10]) == digito2


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Verifica o token e retorna o usuário atual
    """
    # Valida tokens simples para desenvolvimento
    valid_tokens = [
        "jwt_token_example_admin",
        "valid_token"
    ]

    if token in valid_tokens:
        return {"username": "admin", "role": "admin"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""

    logger.info("🚀 Starting API de Consulta e Cobranças v2.0")

    try:
        # Initialize components here (database, cache, etc.)
        logger.info("✅ Application started successfully")
        yield

    except Exception as e:
        logger.error("💥 Failed to start application", error=str(e))
        raise
    finally:
        logger.info("🛑 Shutting down application")
        logger.info("👋 Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL if settings.ENABLE_DOCS else None,
    redoc_url=settings.REDOC_URL if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # CSP mais permissivo para Swagger UI funcionar
    if request.url.path in ["/docs", "/redoc"]:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "font-src 'self' https://cdn.jsdelivr.net"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response


# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    REQUEST_LATENCY.observe(time.time() - start_time)

    return response


# Logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        client_ip=request.client.host if request.client else None,
    )

    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )

    return response


# Health check endpoints
@app.get("/health",
         tags=["Health"],
         response_model=HealthResponse)
async def health_check():
    """Basic health check"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version=settings.APP_VERSION
    )


@app.get("/health/detailed",
         tags=["Health"],
         response_model=HealthResponse)
async def detailed_health_check():
    """Detailed health check with dependencies"""
    # TODO: Implement real database and cache checks
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        checks={
            "database": "healthy",  # TODO: Implement real database check
            "cache": "healthy",  # TODO: Implement real cache check
        }
    )


# Metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    if not settings.ENABLE_METRICS:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# API Info endpoint
@app.get("/",
         tags=["Info"],
         response_model=ApiInfoResponse)
async def api_info():
    """API information"""
    return ApiInfoResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url=settings.DOCS_URL if settings.ENABLE_DOCS else None,
        health_url="/health",
        metrics_url=settings.METRICS_PATH if settings.ENABLE_METRICS else None,
        environment=settings.ENVIRONMENT
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time(),
                "path": request.url.path,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "status_code": 500,
                "timestamp": time.time(),
                "path": request.url.path,
            }
        },
    )


# Example protected endpoints with rate limiting and proper validation


@app.get("/api/v1/cliente/{cpf}", response_model=ClienteResponse, tags=["Clientes"])
async def buscar_cliente(
    cpf: str,
    current_user: str = Depends(get_current_user)
):
    """
    Busca dados de um cliente por CPF

    - **cpf**: CPF do cliente (com ou sem formatação)
    - **Retorna**: Dados completos do cliente
    """
    try:
        # Valida o CPF
        cpf_valido = validate_cpf(cpf)
        if not cpf_valido:
            raise HTTPException(
                status_code=400,
                detail="CPF inválido"
            )

        # Conecta ao MongoDB
        db = get_mongodb_connection()

        # Remove formatação do CPF para busca
        cpf_numerico = re.sub(r'[^\d]', '', cpf)

        # Busca o cliente na coleção
        cliente = db.clientes.find_one({"cpf": cpf_numerico})

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente com CPF {cpf} não encontrado"
            )

        # Formata os dados para retorno
        return ClienteResponse(
            id=str(cliente["_id"]),
            nome=cliente.get("nome", ""),
            cpf=cliente.get("cpf", ""),
            email=cliente.get("email", ""),
            telefone=cliente.get("telefone", ""),
            data_nascimento=cliente.get("data_nascimento", ""),
            endereco=cliente.get("endereco", {}),
            status=cliente.get("status", "ativo"),
            created_at=str(cliente.get("created_at", "")
                           ) if cliente.get("created_at") else "",
            updated_at=str(cliente.get("updated_at", "")
                           ) if cliente.get("updated_at") else ""
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@app.get("/api/v1/cliente/{cpf}/dividas",
         response_model=DividasClienteResponse,
         tags=["Dívidas"])
async def consultar_dividas_cliente(
    cpf: str,
    current_user: str = Depends(get_current_user)
):
    """
    Consulta todas as dívidas de um cliente por CPF

    - **cpf**: CPF do cliente (com ou sem formatação)
    - **Retorna**: Lista completa das dívidas do cliente com tipos como empréstimos, cartão de crédito, cheque especial, etc.
    """
    try:
        # Valida o CPF
        cpf_valido = validate_cpf(cpf)
        if not cpf_valido:
            raise HTTPException(
                status_code=400,
                detail="CPF inválido"
            )

        # Conecta ao MongoDB
        db = get_mongodb_connection()

        # Remove formatação do CPF para busca
        cpf_numerico = re.sub(r'[^\d]', '', cpf)

        # Busca o cliente na coleção
        cliente = db.clientes.find_one({"cpf": cpf_numerico})

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente com CPF {cpf} não encontrado"
            )

        # Busca todas as dívidas do cliente
        dividas_cursor = db.dividas.find({"cliente_id": cliente["_id"]})
        dividas_list = list(dividas_cursor)

        # Converte as dívidas para o formato de resposta
        dividas_formatadas = []
        valor_total_original = 0.0
        valor_total_atual = 0.0
        dividas_ativas = 0
        dividas_vencidas = 0

        for divida in dividas_list:
            # Converte Decimal128 para float se necessário
            valor_original = divida.get("valor_original", 0)
            if hasattr(valor_original, 'to_decimal'):
                valor_original = float(valor_original.to_decimal())
            else:
                valor_original = float(valor_original)

            valor_atual = divida.get("valor_atual", 0)
            if hasattr(valor_atual, 'to_decimal'):
                valor_atual = float(valor_atual.to_decimal())
            else:
                valor_atual = float(valor_atual)

            # Conta estatísticas
            status = divida.get("status", "ativo")
            if status in ["ativo", "vencido", "inadimplente"]:
                valor_total_original += valor_original
                valor_total_atual += valor_atual

                if status == "ativo":
                    dividas_ativas += 1
                elif status in ["vencido", "inadimplente"]:
                    dividas_vencidas += 1

            divida_response = DividaResponse(
                id=str(divida["_id"]),
                tipo=divida.get("tipo", "outros"),
                descricao=divida.get("descricao", ""),
                valor_original=valor_original,
                valor_atual=valor_atual,
                data_vencimento=str(divida.get("data_vencimento", "")
                                    ) if divida.get("data_vencimento") else "",
                dias_atraso=int(divida.get("dias_atraso", 0)),
                status=status,
                juros_mes=float(divida.get("juros_mes", 0)) if divida.get(
                    "juros_mes") else None,
                multa=float(divida.get("multa", 0)) if divida.get("multa") else None,
                created_at=str(divida.get("created_at", "")
                               ) if divida.get("created_at") else "",
                updated_at=str(divida.get("updated_at", "")
                               ) if divida.get("updated_at") else ""
            )
            dividas_formatadas.append(divida_response)

        return DividasClienteResponse(
            cliente_cpf=cpf,
            cliente_nome=cliente.get("nome", ""),
            total_dividas=len(dividas_formatadas),
            valor_total_original=valor_total_original,
            valor_total_atual=valor_total_atual,
            dividas_ativas=dividas_ativas,
            dividas_vencidas=dividas_vencidas,
            dividas=dividas_formatadas
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao consultar dívidas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@app.get("/api/v1/cliente/{cpf}/boletos",
         response_model=List[BoletoResponse],
         tags=["Boletos"])
async def consultar_boletos_cliente(
    cpf: str,
    current_user: str = Depends(get_current_user)
):
    """
    Consulta todos os boletos emitidos para um cliente

    - **cpf**: CPF do cliente (com ou sem formatação)
    - **Retorna**: Lista de boletos (promessas de pagamento) emitidos para o cliente
    """
    try:
        # Valida o CPF
        cpf_valido = validate_cpf(cpf)
        if not cpf_valido:
            raise HTTPException(
                status_code=400,
                detail="CPF inválido"
            )

        # Conecta ao MongoDB
        db = get_mongodb_connection()

        # Remove formatação do CPF para busca
        cpf_numerico = re.sub(r'[^\d]', '', cpf)

        # Busca o cliente na coleção
        cliente = db.clientes.find_one({"cpf": cpf_numerico})

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente com CPF {cpf} não encontrado"
            )

        # Busca todos os boletos do cliente
        boletos_cursor = db.boletos.find({"cliente_id": cliente["_id"]})
        boletos_list = list(boletos_cursor)

        boletos_formatados = []

        for boleto in boletos_list:
            # Converte Decimal128 para float se necessário
            valor = boleto.get("valor", 0)
            if hasattr(valor, 'to_decimal'):
                valor = float(valor.to_decimal())
            else:
                valor = float(valor)

            boleto_response = BoletoResponse(
                id=str(boleto["_id"]),
                numero_boleto=boleto.get("numero_boleto", ""),
                divida_id=str(boleto.get("divida_id", "")) if boleto.get(
                    "divida_id") else None,
                valor=valor,
                data_vencimento=str(boleto.get("data_vencimento", "")
                                    ) if boleto.get("data_vencimento") else "",
                linha_digitavel=boleto.get("linha_digitavel", ""),
                codigo_barras=boleto.get("codigo_barras", ""),
                banco=str(boleto.get("banco", "")),
                status=boleto.get("status", "ativo"),
                url_pagamento=f"https://api.banco.com/boleto/{boleto.get('numero_boleto', '')}"
            )
            boletos_formatados.append(boleto_response)

        return boletos_formatados

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao consultar boletos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@app.post("/api/v1/boleto/gerar", response_model=BoletoGeradoResponse, tags=["Boletos"])
async def gerar_boleto(
    request: BoletoRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Gera um boleto para pagamento de uma ou mais dívidas

    **Regras de Negócio:**
    - Pode incluir 1 ou mais dívidas
    - Pode dividir em até 5 parcelas
    - Parcela mínima: R$ 50,00
    - Só pode negociar dívidas não pagas e sem boleto existente

    **Parâmetros:**
    - **cliente_cpf**: CPF do cliente
    - **dividas_ids**: Lista de IDs das dívidas a incluir
    - **parcelas**: Número de parcelas (1 a 5)
    - **descricao**: Descrição opcional do boleto
    """
    try:
        # Validações iniciais
        if not (1 <= request.parcelas <= 5):
            raise HTTPException(
                status_code=400,
                detail="Número de parcelas deve ser entre 1 e 5"
            )

        if not request.dividas_ids:
            raise HTTPException(
                status_code=400,
                detail="Deve incluir pelo menos uma dívida"
            )

        # Valida o CPF
        cpf_valido = validate_cpf(request.cliente_cpf)
        if not cpf_valido:
            raise HTTPException(
                status_code=400,
                detail="CPF inválido"
            )

        # Conecta ao MongoDB
        db = get_mongodb_connection()

        # Remove formatação do CPF para busca
        cpf_numerico = re.sub(r'[^\d]', '', request.cliente_cpf)

        # Busca o cliente
        cliente = db.clientes.find_one({"cpf": cpf_numerico})
        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente com CPF {request.cliente_cpf} não encontrado"
            )

        # Converte IDs de string para ObjectId
        try:
            dividas_object_ids = [ObjectId(id_str) for id_str in request.dividas_ids]
        except BaseException:
            raise HTTPException(
                status_code=400,
                detail="IDs de dívidas inválidos"
            )

        # Busca as dívidas especificadas
        dividas = list(db.dividas.find({
            "_id": {"$in": dividas_object_ids},
            "cliente_id": cliente["_id"]
        }))

        if len(dividas) != len(request.dividas_ids):
            raise HTTPException(
                status_code=404,
                detail="Uma ou mais dívidas não encontradas para este cliente"
            )

        # Verifica se as dívidas podem ser negociadas
        dividas_nao_negociaveis = []
        valor_total = 0.0

        for divida in dividas:
            # Só pode negociar dívidas ativas, vencidas ou inadimplentes
            if divida.get("status") not in ["ativo", "vencido", "inadimplente"]:
                dividas_nao_negociaveis.append(str(divida["_id"]))
                continue

            # Verifica se já existe boleto ativo para esta dívida
            boleto_existente = db.boletos.find_one({
                "divida_id": divida["_id"],
                "status": {"$in": ["ativo", "pendente"]}
            })

            if boleto_existente:
                dividas_nao_negociaveis.append(str(divida["_id"]))
                continue

            # Soma o valor atual da dívida
            valor = divida.get("valor_atual", divida.get("valor_original", 0))
            if hasattr(valor, 'to_decimal'):
                valor = float(valor.to_decimal())
            else:
                valor = float(valor)
            valor_total += valor

        if dividas_nao_negociaveis:
            raise HTTPException(
                status_code=400,
                detail=(f"Dívidas não podem ser negociadas "
                        f"(já pagas ou com boleto ativo): "
                        f"{', '.join(dividas_nao_negociaveis)}")
            )

        # Calcula valor da parcela
        valor_parcela = valor_total / request.parcelas

        # Verifica se parcela não é menor que R$ 50
        if valor_parcela < 50.0:
            max_parcelas = int(valor_total / 50.0)
            raise HTTPException(
                status_code=400, 
                detail=(f"Valor da parcela (R$ {valor_parcela:.2f}) é menor que "
                       f"R$ 50,00. Máximo de {max_parcelas} parcelas para este valor")
            )

        # Gera dados do boleto
        import random

        # Gera número do boleto de forma mais simples
        p1 = random.randint(10000, 99999)
        p2 = random.randint(10000, 99999)
        p3 = random.randint(10000, 99999)
        p4 = random.randint(100000, 999999)
        p5 = random.randint(10000, 99999)
        p6 = random.randint(100000, 999999)
        dv = random.randint(1, 9)
        codigo = random.randint(10000000000000, 99999999999999)
        
        numero_boleto = f"{p1}.{p2} {p3}.{p4} {p5}.{p6} {dv} {codigo}"
        
        # Gera linha digitável
        ld1 = random.randint(10000, 99999)
        ld2 = random.randint(10000, 99999)
        ld3 = random.randint(10000, 99999)
        ld4 = random.randint(100000, 999999)
        ld5 = random.randint(10000, 99999)
        ld6 = random.randint(100000, 999999)
        ld_dv = random.randint(1, 9)
        ld_codigo = random.randint(10000000000000, 99999999999999)
        
        linha_digitavel = f"{ld1}.{ld2} {ld3}.{ld4} {ld5}.{ld6} {ld_dv} {ld_codigo}"
        
        # Gera código de barras (44 dígitos)
        codigo_barras = f"{random.randint(10000000000000000000000000000000000000000, 99999999999999999999999999999999999999999):044d}"
        
        banco = random.choice(["001", "033", "104", "237", "341", "399"])

        # Importa timedelta localmente
        data_vencimento = (datetime.now() + 
                          datetime.timedelta(days=7))  # 7 dias

        # Cria o boleto no banco
        from bson.decimal128 import Decimal128

        boleto_data = {
            "_id": ObjectId(),
            "numero_boleto": numero_boleto,
            "cliente_id": cliente["_id"],
            # Converte para Decimal128
            "valor": Decimal128(str(round(valor_parcela, 2))),
            "dividas_ids": dividas_object_ids,  # Referência às dívidas incluídas
            "valor_total": valor_total,
            "valor_parcela": round(valor_parcela, 2),
            "parcelas": request.parcelas,
            "parcela_atual": 1,  # Primeira parcela
            "data_vencimento": data_vencimento,
            "linha_digitavel": linha_digitavel,
            "codigo_barras": codigo_barras,
            "banco": banco,
            "agencia": f"{random.randint(1000, 9999)}",
            "conta": f"{random.randint(10000, 99999)}-{random.randint(0, 9)}",
            "status": "ativo",
            "descricao": request.descricao,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        resultado = db.boletos.insert_one(boleto_data)

        # Atualiza status das dívidas para "negociado"
        db.dividas.update_many(
            {"_id": {"$in": dividas_object_ids}},
            {
                "$set": {
                    "status": "negociado",
                    "boleto_id": resultado.inserted_id,
                    "updated_at": datetime.now()
                }
            }
        )

        return BoletoGeradoResponse(
            id=str(resultado.inserted_id),
            numero_boleto=numero_boleto,
            valor_total=valor_total,
            valor_parcela=round(valor_parcela, 2),
            parcelas=request.parcelas,
            data_vencimento=data_vencimento.strftime("%Y-%m-%d %H:%M:%S"),
            linha_digitavel=linha_digitavel,
            codigo_barras=codigo_barras,
            banco=banco,
            url_pagamento=f"https://api.banco.com/boleto/{numero_boleto.replace(' ', '')}",
            dividas_incluidas=request.dividas_ids,
            message=f"Boleto gerado com sucesso! {request.parcelas} parcela(s) de R$ {valor_parcela:.2f}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar boleto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@app.post("/api/v1/boleto/{boleto_id}/cancelar",
          response_model=BoletoCanceladoResponse,
          tags=["Boletos"])
async def cancelar_boleto(
        boleto_id: str,
        current_user: dict = Depends(get_current_user)):
    """
    Cancelar boleto e restaurar dívidas

    Cancela um boleto existente e restaura as dívidas ao estado original,
    preservando todo o histórico da negociação.
    """
    try:
        # Conexão com MongoDB
        db = get_mongodb_connection()

        # Verifica se o boleto existe
        try:
            boleto_object_id = ObjectId(boleto_id)
        except BaseException:
            raise HTTPException(
                status_code=400,
                detail="ID do boleto inválido"
            )

        boleto = db.boletos.find_one({"_id": boleto_object_id})

        if not boleto:
            raise HTTPException(
                status_code=404,
                detail="Boleto não encontrado"
            )

        # Verifica se o boleto pode ser cancelado
        if boleto.get("status") in ["pago", "cancelado"]:
            raise HTTPException(
                status_code=400,
                detail=f"Boleto não pode ser cancelado. Status atual: {
                    boleto.get('status')}")

        # Busca as dívidas associadas ao boleto
        dividas_associadas = list(db.dividas.find({
            "boleto_id": boleto_object_id
        }))

        if not dividas_associadas:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma dívida associada encontrada para este boleto"
            )

        data_cancelamento = datetime.now()

        # Inicia transação para garantir consistência
        with db.client.start_session() as session:
            with session.start_transaction():

                # 1. Atualiza o status do boleto para cancelado
                db.boletos.update_one(
                    {"_id": boleto_object_id},
                    {
                        "$set": {
                            "status": "cancelado",
                            "data_cancelamento": data_cancelamento,
                            "cancelado_por": current_user.get("username", "sistema"),
                            "updated_at": data_cancelamento
                        }
                    },
                    session=session
                )

                # 2. Restaura as dívidas ao estado original
                dividas_ids = [divida["_id"] for divida in dividas_associadas]
                dividas_restauradas = []

                for divida in dividas_associadas:
                    # Define o status original baseado na data de vencimento
                    status_original = "ativo"
                    data_vencimento = divida.get("data_vencimento")

                    if data_vencimento:
                        if isinstance(data_vencimento, str):
                            data_vencimento = datetime.strptime(
                                data_vencimento, "%Y-%m-%d")

                        dias_vencido = (datetime.now() - data_vencimento).days

                        if dias_vencido > 0:
                            if dias_vencido <= 30:
                                status_original = "vencido"
                            else:
                                status_original = "inadimplente"

                    # Atualiza a dívida
                    db.dividas.update_one(
                        {"_id": divida["_id"]},
                        {
                            "$set": {
                                "status": status_original,
                                "updated_at": data_cancelamento
                            },
                            "$unset": {
                                "boleto_id": ""
                            }
                        },
                        session=session
                    )

                    dividas_restauradas.append(str(divida["_id"]))

                # 3. Registra o cancelamento no histórico/auditoria
                auditoria_data = {
                    "acao": "cancelamento_boleto",
                    "boleto_id": boleto_object_id,
                    "dividas_restauradas": dividas_ids,
                    "usuario": current_user.get("username", "sistema"),
                    "data": data_cancelamento,
                    "detalhes": {
                        "boleto_numero": boleto.get("numero_boleto"),
                        "valor_total": boleto.get("valor_total"),
                        "motivo": "cancelamento_solicitado"
                    }
                }

                db.auditoria.insert_one(auditoria_data, session=session)

        logger.info(
            "Boleto cancelado com sucesso",
            boleto_id=boleto_id,
            dividas_restauradas=len(dividas_restauradas),
            usuario=current_user.get("username")
        )

        return BoletoCanceladoResponse(
            boleto_id=boleto_id,
            status="cancelado",
            data_cancelamento=data_cancelamento.strftime("%Y-%m-%d %H:%M:%S"),
            dividas_restauradas=dividas_restauradas,
            historico_preservado=True,
            message=f"Boleto cancelado com sucesso! {
                len(dividas_restauradas)} dívida(s) restaurada(s) ao estado original.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cancelar boleto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@app.post("/auth/token",
          tags=["Authentication"],
          response_model=TokenResponse,
          summary="OAuth2 Login",
          description="Endpoint de autenticação OAuth2 Password Flow",
          responses={
              200: {"model": TokenResponse, "description": "Login realizado com sucesso"},
              400: {"model": ErrorResponse, "description": "Credenciais inválidas"},
              429: {"model": ErrorResponse, "description": "Rate limit excedido"}
          })
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    # Login com OAuth2 Password Flow

    **Credenciais de teste:**
    - username: `admin`
    - password: `admin123`

    **Retorna:**
    - access_token: Token JWT para autenticação
    - token_type: Tipo do token (bearer)
    - expires_in: Tempo de expiração em segundos

    **Como usar:**
    1. Preencha username e password
    2. Clique em "Execute"
    3. Copie o access_token da resposta
    4. Use o token em endpoints protegidos
    """
    logger.info("Tentativa de login", username=form_data.username)

    # TODO: Implementar validação real com casos de uso
    # Por enquanto, aceita admin/admin123 para testes
    if form_data.username == "admin" and form_data.password == "admin123":
        logger.info("Login realizado com sucesso", username=form_data.username)
        return TokenResponse(
            access_token="jwt_token_example_admin",
            token_type="bearer",
            expires_in=1800,  # 30 minutos
            message="Login realizado com sucesso"
        )

    # Credenciais inválidas
    logger.warning("Tentativa de login com credenciais inválidas",
                   username=form_data.username)
    raise HTTPException(
        status_code=400,
        detail="Credenciais inválidas. Use admin/admin123 para testes."
    )


@app.post("/auth/login",
          tags=["Authentication"],
          response_model=TokenResponse,
          responses={
              400: {"model": ErrorResponse, "description": "Credenciais inválidas"},
              429: {"model": ErrorResponse, "description": "Rate limit excedido"}
          })
@limiter.limit("5/minute")
async def login_json(
    request: Request,
    credentials: LoginRequest
):
    """
    Login alternativo com JSON

    Aceita credenciais via JSON:
    - username: nome de usuário ou email
    - password: senha do usuário

    Retorna token JWT para autenticação nas demais rotas.
    """
    logger.info("Tentativa de login via JSON", username=credentials.username)

    # TODO: Implementar validação real com casos de uso
    # Por enquanto, aceita admin/admin123 para testes
    if credentials.username == "admin" and credentials.password == "admin123":
        logger.info("Login JSON realizado com sucesso", username=credentials.username)
        return TokenResponse(
            access_token="jwt_token_example_admin",
            token_type="bearer",
            expires_in=1800,  # 30 minutos
            message="Login realizado com sucesso"
        )

    # Credenciais inválidas
    logger.warning("Tentativa de login JSON com credenciais inválidas",
                   username=credentials.username)
    raise HTTPException(
        status_code=400,
        detail="Credenciais inválidas. Use admin/admin123 para testes."
    )


@app.get("/pagamentos/status/{id_pagamento}",
         tags=["Pagamentos"],
         response_model=PagamentoStatusResponse,
         responses={
             404: {"model": ErrorResponse, "description": "Pagamento não encontrado"},
             429: {"model": ErrorResponse, "description": "Rate limit excedido"}
         })
@limiter.limit("30/minute")
async def status_pagamento(request: Request, id_pagamento: str):
    """
    Consulta status de pagamento

    Retorna o status atual de um pagamento específico.
    """
    logger.info("Status de pagamento consultado", pagamento_id=id_pagamento)

    # TODO: Implement real payment status use case
    status_options = ["pendente", "pago", "cancelado"]
    status = random.choice(status_options)

    return PagamentoStatusResponse(
        id=id_pagamento,
        status=status,
        valor=random.uniform(10.0, 1000.0),
        data_pagamento=(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if status == "pago" else None
        ),
        message="Implementação pendente - usar casos de uso de pagamento"
    )


# TODO: Include routers from presentation layer when implemented
# app.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
# app.include_router(
#     cliente_controller.router, prefix="/clientes", tags=["Clientes"]
# )
# app.include_router(
#     pagamento_controller.router, prefix="/pagamentos", tags=["Pagamentos"]
# )
# app.include_router(boleto_controller.router, prefix="/boletos", tags=["Boletos"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
