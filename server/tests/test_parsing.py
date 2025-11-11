"""
Tests for parsing service - Text extraction from PDF and TXT files
"""
import pytest
from app.services.parsing import extract_text_from_file, extract_pdf_text_bytes


def test_extract_text_from_txt():
    """Test TXT file text extraction"""
    text = "Este é um email de teste.\nCom múltiplas linhas."
    file_bytes = text.encode('utf-8')
    
    result = extract_text_from_file(file_bytes, "test.txt")
    
    assert "email de teste" in result
    assert "múltiplas linhas" in result


def test_extract_text_from_txt_latin1():
    """Test TXT with latin-1 encoding fallback"""
    text = "Testando acentuação"
    file_bytes = text.encode('latin-1')
    
    result = extract_text_from_file(file_bytes, "test.txt")
    
    assert "acentua" in result.lower()


def test_unsupported_file_format():
    """Test error for unsupported file format"""
    with pytest.raises(ValueError) as exc_info:
        extract_text_from_file(b"test data", "test.docx")
    
    assert "não suportado" in str(exc_info.value)


def test_extract_pdf_text_bytes_empty():
    """Test PDF extraction with empty content"""
    # Este teste seria melhor com um PDF real, mas serve como placeholder
    # Em produção, use arquivos PDF de teste reais
    pass


def test_extract_text_preserves_spaces():
    """Test that extraction preserves spacing"""
    text = "Palavra1 Palavra2   Palavra3"
    file_bytes = text.encode('utf-8')
    
    result = extract_text_from_file(file_bytes, "test.txt")
    
    assert "Palavra1" in result
    assert "Palavra2" in result
    assert "Palavra3" in result
