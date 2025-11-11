"""
Pydantic schemas - Validação de dados de entrada/saída da API
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ProcessTextRequest(BaseModel):
    """Request body para processar texto direto"""
    text: str = Field(..., min_length=10, max_length=50000, description="Texto do email")


class ProcessResponse(BaseModel):
    """Response padrão do endpoint /api/process"""
    id: str = Field(..., description="UUID da análise")
    category: Literal["Produtivo", "Improdutivo"] = Field(..., description="Categoria do email")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da classificação")
    suggested_reply: str = Field(..., description="Resposta sugerida")
    summary: str = Field(..., description="Resumo do email")
    model_used: str = Field(..., description="Modelo usado (openai-gpt-4o-mini)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da análise")
    reason: Optional[str] = Field(None, description="Justificativa da classificação")


class FeedbackRequest(BaseModel):
    """Request body para feedback do usuário"""
    analysis_id: str = Field(..., description="ID da análise")
    edited_reply: Optional[str] = Field(None, description="Resposta editada pelo usuário")
    user_category: Optional[Literal["Produtivo", "Improdutivo"]] = Field(None, description="Categoria corrigida")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Avaliação 1-5")
    comments: Optional[str] = Field(None, max_length=500, description="Comentários adicionais")


class StatusResponse(BaseModel):
    """Response do endpoint /api/status/{id}"""
    id: str
    status: Literal["completed", "processing", "failed", "not_found"]
    category: Optional[str] = None
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Response do endpoint /health"""
    status: Literal["healthy", "degraded"]
    version: str = "1.0.0"
    openai_configured: bool
    database_connected: bool
