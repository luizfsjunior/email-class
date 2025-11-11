"""
Process API endpoints - Endpoint principal para processar emails
"""
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from datetime import datetime

from app.models.schemas import ProcessTextRequest, ProcessResponse, FeedbackRequest, StatusResponse
from app.services.parsing import extract_text_from_file
from app.services.nlp import clean_text, extract_summary
from app.services.ai_client import get_ai_client
from app.utils.database import get_database
from app.core.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_model=ProcessResponse)
async def process_email(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Processa email (arquivo ou texto) e retorna classificação + resposta sugerida
    
    Fluxo:
    1. Extrai texto (de arquivo ou campo text)
    2. Preprocessa
    3. Classifica usando LLM (ou fallback baseline)
    4. Gera resposta sugerida
    5. Salva no banco
    6. Retorna resultado
    """
    settings = get_settings()
    
    # Validação: precisa de file OU text
    if not file and not text:
        raise HTTPException(status_code=400, detail="Envie um arquivo ou texto")
    
    try:
        # 1. Extração de texto
        if file:
            # Valida tamanho
            file_bytes = await file.read()
            if len(file_bytes) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(status_code=413, detail="Arquivo muito grande (máx 1MB)")
            
            extracted_text = extract_text_from_file(file_bytes, file.filename)
        else:
            extracted_text = text
        
        if len(extracted_text) < 10:
            raise HTTPException(status_code=400, detail="Texto muito curto")
        
        # 2. Preprocessamento
        clean = clean_text(extracted_text, remove_stopwords=False)  # Mantém stopwords para LLM
        summary = extract_summary(extracted_text)
        
        # 3. Classificação usando LLM
        ai_client = get_ai_client()
        classification = await ai_client.classify_email(clean)
        model_used = f"{settings.LLM_MODEL}"
        
        # DEBUG: Log da classificação
        logger.info(f"🔍 CLASSIFICAÇÃO:")
        logger.info(f"   Categoria: {classification['category']}")
        logger.info(f"   Confiança: {classification['confidence']}")
        logger.info(f"   Razão: {classification.get('reason')}")
        logger.info(f"   Texto (primeiros 100 chars): {extracted_text[:100]}...")
        
        # 4. Geração de resposta
        reply_result = await ai_client.generate_reply(
            category=classification["category"],
            summary=summary,
            original_text=extracted_text
        )
        suggested_reply = reply_result["reply"]
        
        # 5. Salva no banco
        analysis_id = str(uuid.uuid4())
        db = get_database()
        
        analysis_data = {
            "id": analysis_id,
            "category": classification["category"],
            "confidence": classification["confidence"],
            "suggested_reply": suggested_reply,
            "summary": summary,
            "model_used": model_used,
            "reason": classification.get("reason"),
            "full_text": extracted_text
        }
        
        db.save_analysis(analysis_data)
        
        # 6. Retorna resultado
        return ProcessResponse(
            id=analysis_id,
            category=classification["category"],
            confidence=classification["confidence"],
            suggested_reply=suggested_reply,
            summary=summary,
            model_used=model_used,
            timestamp=datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None),
            reason=classification.get("reason")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar email: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Recebe feedback do usuário sobre a análise"""
    try:
        db = get_database()
        
        # Valida que análise existe
        analysis = db.get_analysis(feedback.analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        # Salva feedback
        feedback_data = feedback.model_dump()
        success = db.save_feedback(feedback_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao salvar feedback")
        
        return {"status": "success", "message": "Feedback recebido"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")


@router.get("/status/{analysis_id}", response_model=StatusResponse)
async def get_status(analysis_id: str):
    """Retorna status de uma análise"""
    try:
        db = get_database()
        analysis = db.get_analysis(analysis_id)
        
        if not analysis:
            return StatusResponse(
                id=analysis_id,
                status="not_found"
            )
        
        return StatusResponse(
            id=analysis_id,
            status="completed",
            category=analysis["category"],
            confidence=analysis["confidence"],
            created_at=datetime.fromisoformat(analysis["created_at"])
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar status: {str(e)}")
        return StatusResponse(
            id=analysis_id,
            status="failed"
        )
