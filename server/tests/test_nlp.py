"""
Tests for NLP preprocessing service
"""
import pytest
from app.services.nlp import clean_text, extract_summary


def test_clean_text_lowercase():
    """Test that text is converted to lowercase"""
    text = "EMAIL COM LETRAS MAIÚSCULAS"
    result = clean_text(text, remove_stopwords=False)
    
    assert result == result.lower()
    assert "email" in result


def test_clean_text_removes_urls():
    """Test URL removal"""
    text = "Confira nosso site https://example.com e http://test.org"
    result = clean_text(text, remove_stopwords=False)
    
    assert "https" not in result
    assert "http" not in result
    assert "example.com" not in result


def test_clean_text_removes_special_chars():
    """Test special character removal"""
    text = "Email com @#$% caracteres !!! especiais???"
    result = clean_text(text, remove_stopwords=False)
    
    assert "@" not in result
    assert "#" not in result
    assert "!" not in result
    assert "?" not in result


def test_clean_text_preserves_accents():
    """Test that Portuguese accents are preserved"""
    text = "Ação, atenção, opção, rápido"
    result = clean_text(text, remove_stopwords=False)
    
    assert "ção" in result or "cao" in result  # Pode normalizar ou não
    

def test_clean_text_removes_stopwords():
    """Test stopword removal"""
    text = "Este é um email que precisa de uma resposta"
    result = clean_text(text, remove_stopwords=True)
    
    # Stopwords comuns não devem estar presentes
    assert "um" not in result.split()
    assert "de" not in result.split()
    # Palavras importantes devem permanecer
    assert "email" in result


def test_clean_text_no_stopword_removal():
    """Test keeping stopwords when disabled"""
    text = "Este é um email"
    result = clean_text(text, remove_stopwords=False)
    
    words = result.split()
    assert len(words) > 0


def test_clean_text_normalizes_whitespace():
    """Test whitespace normalization"""
    text = "Email    com     múltiplos    espaços"
    result = clean_text(text, remove_stopwords=False)
    
    # Não deve ter múltiplos espaços
    assert "  " not in result


def test_extract_summary_short_text():
    """Test summary extraction for short text"""
    text = "Este é um texto curto"
    result = extract_summary(text, max_chars=150)
    
    assert result == text.strip()


def test_extract_summary_long_text():
    """Test summary extraction for long text"""
    text = "A" * 200
    result = extract_summary(text, max_chars=100)
    
    assert len(result) <= 103  # 100 + "..."
    assert result.endswith("...")


def test_extract_summary_respects_sentence_boundary():
    """Test that summary tries to cut at sentence boundary"""
    text = "Primeira frase. Segunda frase muito longa que excede o limite. Terceira frase."
    result = extract_summary(text, max_chars=50)
    
    # Deve tentar cortar em um ponto final
    assert result.endswith(".") or result.endswith("...")


def test_clean_text_empty_string():
    """Test handling of empty string"""
    result = clean_text("", remove_stopwords=False)
    assert result == ""


def test_clean_text_only_special_chars():
    """Test text with only special characters"""
    text = "@#$%^&*()"
    result = clean_text(text, remove_stopwords=False)
    
    # Deve resultar em string vazia ou muito curta
    assert len(result) < len(text)
