"""
FastAPI Main Application - Email Classifier MVP
Classifica emails em Produtivo/Improdutivo e gera respostas sugeridas

Arquitetura:
- FastAPI async para performance
- LLM primário (OpenAI) com fallback para baseline (sklearn)
- SQLite para persistência
- CORS configurado para frontend local
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.settings import get_settings
from app.api import process
from app.models.schemas import HealthResponse
from app.services.ai_client import get_ai_client
from app.utils.database import get_database

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events - inicialização e cleanup"""
    logger.info("Iniciando aplicação...")
    
    # Inicializa componentes
    settings = get_settings()
    db = get_database()
    ai_client = get_ai_client()
    
    logger.info(f"Ambiente: {settings.APP_ENV}")
    logger.info(f"OpenAI configurado: {settings.OPENAI_API_KEY is not None}")
    
    yield
    
    logger.info("Encerrando aplicação...")


# Inicializa FastAPI app
app = FastAPI(
    title="Email Classifier API",
    description="Classifica emails em Produtivo/Improdutivo e gera respostas sugeridas",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração CORS
settings = get_settings()
origins = settings.CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check - verifica status dos componentes
    """
    settings = get_settings()
    db = get_database()
    
    # Verifica database
    db_connected = False
    try:
        # Tenta uma query simples
        test = db.get_analysis("test")
        db_connected = True
    except:
        pass
    
    all_healthy = db_connected and (settings.OPENAI_API_KEY is not None)
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        openai_configured=settings.OPENAI_API_KEY is not None,
        database_connected=db_connected
    )


# Include routers
app.include_router(
    process.router,
    prefix="/api",
    tags=["processing"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint com informações da API"""
    return {
        "name": "Email Classifier API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceptions não tratadas"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True if settings.APP_ENV == "development" else False
    )
