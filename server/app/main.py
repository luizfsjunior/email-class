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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação...")
    
    settings = get_settings()
    db = get_database()
    ai_client = get_ai_client()
    
    logger.info(f"Ambiente: {settings.APP_ENV}")
    logger.info(f"OpenAI configurado: {settings.OPENAI_API_KEY is not None}")
    
    yield
    
    logger.info("Encerrando aplicação...")


app = FastAPI(
    title="Email Classifier API",
    description="Classifica emails em Produtivo/Improdutivo e gera respostas sugeridas",
    version="1.0.0",
    lifespan=lifespan
)

settings = get_settings()
origins = settings.CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    db = get_database()
    
    db_connected = False
    try:
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


app.include_router(
    process.router,
    prefix="/api",
    tags=["processing"]
)


@app.get("/")
async def root():
    return {
        "name": "Email Classifier API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
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
