"""
API de Consulta e Cobranças v2.0
Arquitetura Hexagonal com segurança e performance aprimoradas
"""

import time
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.config.settings import get_settings

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

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")
ACTIVE_CONNECTIONS = Counter("active_connections_total", "Active connections")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Settings
settings = get_settings()


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
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": "healthy",  # TODO: Implement real database check
            "cache": "healthy",  # TODO: Implement real cache check
        },
    }
    return health_status


# Metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    if not settings.ENABLE_METRICS:
        raise HTTPException(status_code=404, detail="Metrics disabled")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# API Info endpoint
@app.get("/", tags=["Info"])
async def api_info():
    """API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": settings.DOCS_URL if settings.ENABLE_DOCS else None,
        "health_url": "/health",
        "metrics_url": settings.METRICS_PATH if settings.ENABLE_METRICS else None,
        "environment": settings.ENVIRONMENT,
    }


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


@app.get("/clientes/{cpf}", tags=["Clientes"])
@limiter.limit("60/minute")
async def buscar_cliente(request: Request, cpf: str):
    """Busca cliente por CPF com rate limiting e validação"""
    try:
        # Import here to avoid circular imports
        from src.domain.value_objects.cpf import CPF

        # Validate CPF
        cpf_obj = CPF(cpf)

        logger.info("Cliente consultado", cpf=cpf_obj.mascarado())

        # TODO: Implement real use case
        return {
            "cpf": cpf_obj.formatado(),
            "nome": "Cliente Exemplo",
            "status": "ativo",
            "message": (
                "Implementação pendente - usar casos de uso da camada de aplicação"
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/token", tags=["Authentication"])
@limiter.limit("5/minute")
async def login(request: Request):
    """Login com rate limiting rigoroso"""
    logger.info("Tentativa de login")

    # TODO: Implement real authentication use case
    return {
        "access_token": "example_token",
        "token_type": "bearer",
        "message": "Implementação pendente - usar casos de uso de autenticação",
    }


@app.post("/boletos/gerar", tags=["Boletos"])
@limiter.limit("10/minute")
async def gerar_boleto(request: Request):
    """Gerar boleto com rate limiting"""
    logger.info("Boleto gerado")

    # TODO: Implement real boleto generation use case
    return {
        "id": "boleto123",
        "url": "/boletos/download/boleto123",
        "message": "Implementação pendente - usar casos de uso de geração de boleto",
    }


@app.get("/pagamentos/status/{id_pagamento}", tags=["Pagamentos"])
@limiter.limit("30/minute")
async def status_pagamento(request: Request, id_pagamento: str):
    """Consulta status de pagamento"""
    logger.info("Status de pagamento consultado", pagamento_id=id_pagamento)

    # TODO: Implement real payment status use case
    return {
        "id": id_pagamento,
        "status": "pendente",
        "message": "Implementação pendente - usar casos de uso de pagamento",
    }


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
