"""
API de Consulta de Boletos - v2
Arquitetura Hexagonal com segurança e performance aprimoradas
"""
import random
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional

import structlog
import uvicorn
from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel
from pymongo import MongoClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.config.settings import get_settings
from src.infra.cache.redis_cache import RedisCache
from src.infra.db.mongo import MongoProvider
from src.infra.repositories.cliente_repository import ClienteRepository

# --- Models (DTOs) ---
# Geralmente, estes modelos estariam em seus próprios arquivos (ex: src/domain/dtos.py)
# mas para simplificar, estão aqui.


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


class ClienteResponse(BaseModel):
    id: str
    nome: str
    cpf: str
    email: str
    telefone: str
    data_cadastro: str
    data_nascimento: Optional[str] = None
    endereco: Optional[dict] = None
    status: str = "ativo"
    score_credito: Optional[int] = None
    limite_credito: Optional[float] = None
    dividas_ativas: Optional[int] = None
    valor_total_dividas: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DividaResponse(BaseModel):
    id: str
    tipo: Optional[str] = "outros"
    descricao: str
    valor: float
    valor_original: Optional[float] = None
    valor_atual: Optional[float] = None
    status: str
    data_vencimento: str
    dias_atraso: Optional[int] = 0
    juros_mes: Optional[float] = None
    multa: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DividasClienteResponse(BaseModel):
    cliente_id: Optional[str] = None
    cliente_cpf: str
    cliente_nome: Optional[str] = None
    total_dividas: int
    valor_total: float
    valor_total_original: Optional[float] = None
    valor_total_atual: Optional[float] = None
    dividas_ativas: Optional[int] = 0
    dividas_vencidas: Optional[int] = 0
    dividas: List[DividaResponse]


class BoletoResponse(BaseModel):
    id: str
    numero_boleto: str
    divida_id: Optional[str] = None
    valor: float
    data_vencimento: str
    linha_digitavel: str
    codigo_barras: str
    banco: str
    status: str
    url_pagamento: str


class BoletoRequest(BaseModel):
    cliente_cpf: str
    dividas_ids: List[str]
    parcelas: int = 1
    descricao: Optional[str] = "Negociação de dívidas"


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
    dividas_incluidas: List[str]
    message: str


class BoletoCanceladoResponse(BaseModel):
    boleto_id: str
    status: str
    data_cancelamento: str
    dividas_restauradas: List[str]
    historico_preservado: bool
    message: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    message: str
    status_code: int
    timestamp: float
    path: str


class LoginRequest(BaseModel):
    username: str
    password: str


class PagamentoStatusResponse(BaseModel):
    pagamento_id: str
    status: str
    data_processamento: str
    mensagem: str


# --- Configuração ---
settings = get_settings()

# Logger
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Variáveis Globais ---
mongo_provider: Optional[MongoProvider] = None
redis_cache: Optional[RedisCache] = None

# --- Métricas Prometheus ---
REQUEST_COUNT = Counter(
    "request_count",
    "App Request Count",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency",
    ["endpoint"]
)
ACTIVE_SESSIONS = Gauge(
    "active_sessions",
    "Number of active user sessions"
)

# --- Funções de Autenticação ---


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Token inválido: sem 'sub'"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Token inválido ou expirado"
        )


def normalize_cpf(cpf: str) -> str:
    """Remove todos os caracteres não numéricos do CPF"""
    return re.sub(r'[^\d]', '', cpf)


def get_mongodb_connection():
    """Get MongoDB connection using application settings"""
    client = MongoClient(settings.MONGO_URI)
    return client[settings.MONGO_DB_NAME]


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
    Verifica o token JWT e retorna o usuário atual
    """
    username = verify_token(token)
    return {"username": username, "role": "admin"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""

    logger.info("🚀 Starting API de Consulta e Cobranças v2.0")

    try:
        # Initialize components here (database, cache, etc.)
        global mongo_provider, redis_cache
        mongo_provider = MongoProvider(settings)
        await mongo_provider.connect()

        redis_cache = RedisCache(settings)
        await redis_cache.connect()

        # Optionally ensure indexes
        if settings.AUTO_CREATE_INDEXES:
            try:
                from scripts.migrations._runner import ensure_indexes
                await ensure_indexes()
            except Exception as e:  # pragma: no cover - best-effort
                logger.warning("Falha ao garantir índices", error=str(e))
        logger.info("✅ Application started successfully")
        yield

    except Exception as e:
        logger.error("💥 Failed to start application", error=str(e))
        raise
    finally:
        logger.info("🛑 Shutting down application")
        if redis_cache:
            try:
                await redis_cache.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting Redis: {e}")
        if mongo_provider:
            try:
                await mongo_provider.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting MongoDB: {e}")
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

    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(time.time() - start_time)

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
    checks = {"database": "unknown", "cache": "unknown"}
    overall = "healthy"
    # Mongo
    try:
        if mongo_provider:
            await mongo_provider.db.command("ping")
            checks["database"] = "healthy"
        else:
            checks["database"] = "unavailable"
            overall = "degraded"
    except Exception as e:  # pragma: no cover
        checks["database"] = f"unhealthy: {str(e)}"
        overall = "unhealthy"

    # Redis
    try:
        if redis_cache and redis_cache._pool:
            pong = await redis_cache._pool.ping()
            checks["cache"] = "healthy" if pong else "unhealthy"
            if not pong:
                overall = "degraded"
        else:
            if settings.CACHE_ENABLED is False:
                checks["cache"] = "disabled"
            else:
                checks["cache"] = "unavailable"
    except Exception as e:  # pragma: no cover
        checks["cache"] = f"unhealthy: {str(e)}"
        overall = "degraded"

    return HealthResponse(
        status=overall,
        timestamp=time.time(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        checks=checks,
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

        # Usa repositório assíncrono com cache
        if not mongo_provider:
            raise HTTPException(status_code=500, detail="Banco de dados indisponível")
        repo = ClienteRepository(mongo_provider.db, cache=redis_cache)
        cliente = await repo.get_by_cpf(cpf)

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente com CPF {cpf} não encontrado"
            )

        # Calcula dados derivados (dívidas ativas e valor total)
        try:
            from bson import ObjectId as _ObjectId
            if isinstance(cliente["_id"], str):
                cliente_oid = _ObjectId(cliente["_id"])
            else:
                cliente_oid = cliente["_id"]

            # Busca dívidas ativas para calcular estatísticas
            cursor = mongo_provider.db.dividas.find({
                "cliente_id": cliente_oid,
                "status": {"$in": ["ativo", "vencido", "inadimplente"]}
            })
            dividas_ativas_list = await cursor.to_list(length=1000)

            dividas_ativas_count = len(dividas_ativas_list)
            valor_total_dividas = 0.0

            for divida in dividas_ativas_list:
                valor = divida.get("valor_atual", divida.get("valor_original", 0))
                if hasattr(valor, 'to_decimal'):
                    valor = float(valor.to_decimal())
                else:
                    valor = float(valor)
                valor_total_dividas += valor

        except Exception as e:
            logger.warning(f"Erro ao calcular dívidas ativas: {e}")
            dividas_ativas_count = 0
            valor_total_dividas = 0.0

        # Formata os dados para retorno
        return ClienteResponse(
            id=str(cliente.get("_id", "")),
            nome=cliente.get("nome", ""),
            cpf=cliente.get("cpf", ""),
            email=cliente.get("email", ""),
            telefone=cliente.get("telefone", ""),
            data_cadastro=(
                str(cliente.get("created_at", ""))
                if cliente.get("created_at") else datetime.now().strftime("%Y-%m-%d")
            ),
            data_nascimento=cliente.get("data_nascimento", ""),
            endereco=cliente.get("endereco", {}),
            status=cliente.get("status", "ativo"),
            score_credito=cliente.get("score_credito"),
            limite_credito=cliente.get("limite_credito"),
            dividas_ativas=dividas_ativas_count,
            valor_total_dividas=valor_total_dividas,
            created_at=(
                str(cliente.get("created_at", ""))
                if cliente.get("created_at") else ""
            ),
            updated_at=(
                str(cliente.get("updated_at", ""))
                if cliente.get("updated_at") else ""
            )
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
    - **Retorna**: Lista completa das dívidas do cliente com tipos como
      empréstimos, cartão de crédito, cheque especial, etc.
    """
    try:
        # Valida o CPF
        cpf_valido = validate_cpf(cpf)
        if not cpf_valido:
            raise HTTPException(
                status_code=400,
                detail="CPF inválido"
            )

        # Busca o cliente via repositório com cache
        if not mongo_provider:
            raise HTTPException(status_code=500, detail="Banco de dados indisponível")
        repo = ClienteRepository(mongo_provider.db, cache=redis_cache)
        cliente = await repo.get_by_cpf(cpf)

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente com CPF {cpf} não encontrado"
            )

        # Busca todas as dívidas do cliente (assíncrono)
        from bson import ObjectId as _ObjectId
        if isinstance(cliente["_id"], str):
            cliente_oid = _ObjectId(cliente["_id"])
        else:
            cliente_oid = cliente["_id"]
        cursor = mongo_provider.db.dividas.find({"cliente_id": cliente_oid})
        dividas_list = await cursor.to_list(length=1000)

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
                valor=valor_atual,  # Campo obrigatório usando valor_atual
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
            cliente_id=str(cliente.get("_id", "")),
            cliente_cpf=cpf,
            cliente_nome=cliente.get("nome", ""),
            total_dividas=len(dividas_formatadas),
            valor_total=valor_total_atual,  # Campo obrigatório
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

        # Busca o cliente via repositório
        if not mongo_provider:
            raise HTTPException(status_code=500, detail="Banco de dados indisponível")
        repo = ClienteRepository(mongo_provider.db, cache=redis_cache)
        cliente = await repo.get_by_cpf(cpf)

        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente com CPF {cpf} não encontrado"
            )

        # Busca todos os boletos do cliente (assíncrono)
        from bson import ObjectId as _ObjectId
        if isinstance(cliente["_id"], str):
            cliente_oid = _ObjectId(cliente["_id"])
        else:
            cliente_oid = cliente["_id"]
        cursor = mongo_provider.db.boletos.find({"cliente_id": cliente_oid})
        boletos_list = await cursor.to_list(length=1000)

        boletos_formatados = []

        for boleto in boletos_list:
            # Converte Decimal128 para float se necessário
            valor = boleto.get("valor", 0)
            if hasattr(valor, 'to_decimal'):
                valor = float(valor.to_decimal())
            else:
                valor = float(valor)

            numero_boleto = boleto.get("numero_boleto", "")

            boleto_response = BoletoResponse(
                id=str(boleto["_id"]),
                numero_boleto=numero_boleto,
                divida_id=str(boleto.get("divida_id", "")) if boleto.get(
                    "divida_id") else None,
                valor=valor,
                data_vencimento=str(boleto.get("data_vencimento", "")
                                    ) if boleto.get("data_vencimento") else "",
                linha_digitavel=boleto.get("linha_digitavel", ""),
                codigo_barras=boleto.get("codigo_barras", ""),
                banco=str(boleto.get("banco", "")),
                status=boleto.get("status", "ativo"),
                url_pagamento=f"https://api.banco.com/boleto/{numero_boleto}"
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
    current_user: str = Depends(get_current_user),
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

        # Conecta ao MongoDB (assíncrono)
        if not mongo_provider:
            raise HTTPException(status_code=500, detail="Banco de dados indisponível")
        db = mongo_provider.db

        # Busca o cliente
        cpf_numerico = re.sub(r'[^\d]', '', request.cliente_cpf)
        cliente = await db.clientes.find_one({"cpf": cpf_numerico})
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
        cursor = db.dividas.find({
            "_id": {"$in": dividas_object_ids},
            "cliente_id": cliente["_id"]
        })
        dividas = await cursor.to_list(length=1000)

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
            boleto_existente = await db.boletos.find_one({
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
        cb_min = 10000000000000000000000000000000000000000
        cb_max = 99999999999999999999999999999999999999999
        codigo_barras = f"{random.randint(cb_min, cb_max):044d}"
        banco = random.choice(["001", "033", "104", "237", "341", "399"])

        data_vencimento = datetime.now() + timedelta(days=7)

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

        resultado = await db.boletos.insert_one(boleto_data)

        # Atualiza status das dívidas para "negociado"
        await db.dividas.update_many(
            {"_id": {"$in": dividas_object_ids}},
            {
                "$set": {
                    "status": "negociado",
                    "boleto_id": resultado.inserted_id,
                    "updated_at": datetime.now()
                }
            }
        )

        numero_boleto_clean = numero_boleto.replace(' ', '')
        parcelas_info = (
            f"{request.parcelas} parcela(s) de R$ {valor_parcela:.2f}"
        )

        # Invalida cache do cliente (se habilitado)
        try:
            if redis_cache:
                cpf_normalized = normalize_cpf(request.cliente_cpf)
                await redis_cache.delete(f"cliente:cpf:{cpf_normalized}")
        except Exception as e:
            logger.warning(f"Error invalidating cache: {e}")

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
            url_pagamento=f"https://api.banco.com/boleto/{numero_boleto_clean}",
            dividas_incluidas=request.dividas_ids,
            message=f"Boleto gerado com sucesso! {parcelas_info}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar boleto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )


@app.post(
    "/api/v1/boleto/{boleto_id}/cancelar",
    response_model=BoletoCanceladoResponse,
    tags=["Boletos"]
)
async def cancelar_boleto(
    boleto_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancela um boleto e restaura as dívidas ao estado original."""
    try:
        if not mongo_provider:
            raise HTTPException(status_code=500, detail="Banco de dados indisponível")
        db = mongo_provider.db

        try:
            boleto_object_id = ObjectId(boleto_id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID do boleto inválido")

        boleto = await db.boletos.find_one({"_id": boleto_object_id})
        if not boleto:
            raise HTTPException(status_code=404, detail="Boleto não encontrado")
        if boleto.get("status") in ["pago", "cancelado"]:
            status_atual = boleto.get('status')
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Boleto não pode ser cancelado. "
                    f"Status atual: {status_atual}"
                )
            )

        dividas_associadas = await db.dividas.find(
            {"boleto_id": boleto_object_id}
        ).to_list(length=1000)
        if not dividas_associadas:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Nenhuma dívida associada encontrada para este boleto"
                )
            )

        data_cancelamento = datetime.now()
        await db.boletos.update_one(
            {"_id": boleto_object_id},
            {
                "$set": {
                    "status": "cancelado",
                    "data_cancelamento": data_cancelamento,
                    "cancelado_por": current_user.get("username", "sistema"),
                    "updated_at": data_cancelamento
                }
            }
        )

        dividas_ids = [d["_id"] for d in dividas_associadas]
        dividas_restauradas = []
        for d in dividas_associadas:
            status_original = "ativo"
            dv = d.get("data_vencimento")
            if dv:
                if isinstance(dv, str):
                    try:
                        dv = datetime.strptime(dv, "%Y-%m-%d")
                    except Exception as e:
                        logger.warning(f"Error parsing date {dv}: {e}")
                        dv = None
                if dv and hasattr(dv, "__class__"):
                    dias_vencido = (datetime.now() - dv).days
                    if dias_vencido > 0:
                        if dias_vencido <= 30:
                            status_original = "vencido"
                        else:
                            status_original = "inadimplente"
            await db.dividas.update_one(
                {"_id": d["_id"]},
                {
                    "$set": {
                        "status": status_original,
                        "updated_at": data_cancelamento
                    },
                    "$unset": {"boleto_id": ""}
                }
            )
            dividas_restauradas.append(str(d["_id"]))

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
            },
        }
        await db.auditoria.insert_one(auditoria_data)

        try:
            if redis_cache and boleto.get("cliente_id"):
                cliente_doc = await db.clientes.find_one(
                    {"_id": boleto.get("cliente_id")}
                )
                if cliente_doc and cliente_doc.get("cpf"):
                    cpf_normalizado = normalize_cpf(cliente_doc.get('cpf'))
                    await redis_cache.delete(f"cliente:cpf:{cpf_normalizado}")
        except Exception as e:
            logger.warning(f"Error invalidating cache during cancellation: {e}")

        return BoletoCanceladoResponse(
            boleto_id=boleto_id,
            status="cancelado",
            data_cancelamento=data_cancelamento.strftime("%Y-%m-%d %H:%M:%S"),
            dividas_restauradas=dividas_restauradas,
            historico_preservado=True,
            message=(
                f"Boleto cancelado com sucesso! "
                f"{len(dividas_restauradas)} dívida(s) restaurada(s) "
                f"ao estado original."
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cancelar boleto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@app.post("/auth/token",
          tags=["Authentication"],
          response_model=TokenResponse,
          summary="OAuth2 Login",
          description="Endpoint de autenticação OAuth2 Password Flow",
          responses={
              200: {
                  "model": TokenResponse,
                  "description": "Login realizado com sucesso"
              },
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

        # Gera JWT real
        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )

        # Gera refresh token (válido por mais tempo)
        refresh_token_expires = timedelta(days=7)
        refresh_token = create_access_token(
            data={"sub": form_data.username, "type": "refresh"},
            expires_delta=refresh_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
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

        # Gera JWT real
        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": credentials.username}, expires_delta=access_token_expires
        )

        # Gera refresh token (válido por mais tempo)
        refresh_token_expires = timedelta(days=7)
        refresh_token = create_access_token(
            data={"sub": credentials.username, "type": "refresh"},
            expires_delta=refresh_token_expires
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
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
