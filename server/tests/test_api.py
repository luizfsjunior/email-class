"""
Tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns info"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "openai_configured" in data
    assert "database_connected" in data


def test_process_with_text():
    """Test /api/process with text input"""
    response = client.post(
        "/api/process",
        data={"text": "Prezado, solicito atualização do meu chamado urgente"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert "category" in data
    assert data["category"] in ["Produtivo", "Improdutivo"]
    assert "confidence" in data
    assert "suggested_reply" in data
    assert "summary" in data
    assert "model_used" in data


def test_process_without_input():
    """Test /api/process without text or file"""
    response = client.post("/api/process")
    
    assert response.status_code == 400
    assert "detail" in response.json()


def test_process_with_short_text():
    """Test /api/process with very short text"""
    response = client.post(
        "/api/process",
        data={"text": "Oi"}
    )
    
    assert response.status_code == 400


def test_status_endpoint_not_found():
    """Test /api/status with non-existent ID"""
    response = client.get("/api/status/nonexistent-id")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "not_found"


def test_feedback_endpoint():
    """Test /api/feedback endpoint"""
    # Primeiro cria uma análise
    process_response = client.post(
        "/api/process",
        data={"text": "Teste de feedback para análise"}
    )
    
    assert process_response.status_code == 200
    analysis_id = process_response.json()["id"]
    
    # Envia feedback
    feedback_response = client.post(
        "/api/feedback",
        json={
            "analysis_id": analysis_id,
            "rating": 5,
            "comments": "Excelente análise"
        }
    )
    
    assert feedback_response.status_code == 200
    assert feedback_response.json()["status"] == "success"


def test_feedback_with_invalid_id():
    """Test /api/feedback with invalid analysis ID"""
    response = client.post(
        "/api/feedback",
        json={
            "analysis_id": "invalid-id-12345",
            "rating": 3
        }
    )
    
    assert response.status_code == 404


def test_process_returns_valid_json():
    """Test that process endpoint returns valid structured JSON"""
    response = client.post(
        "/api/process",
        data={"text": "Email de teste para validação de estrutura JSON"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Valida estrutura completa
    required_fields = ["id", "category", "confidence", "suggested_reply", 
                      "summary", "model_used", "timestamp"]
    
    for field in required_fields:
        assert field in data, f"Campo {field} ausente no response"
    
    # Valida tipos
    assert isinstance(data["confidence"], (int, float))
    assert isinstance(data["suggested_reply"], str)
    assert len(data["suggested_reply"]) > 0
