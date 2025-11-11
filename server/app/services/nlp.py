"""
NLP preprocessing service - Limpeza e normalização de texto
Utiliza NLTK para remoção de stopwords em português
"""
import re
import nltk
from nltk.corpus import stopwords
from typing import Set
import logging

logger = logging.getLogger(__name__)

# Download stopwords na primeira execução
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    logger.info("Baixando stopwords do NLTK...")
    nltk.download('stopwords', quiet=True)

# Cache das stopwords
STOP_WORDS: Set[str] = set(stopwords.words('portuguese'))


def clean_text(text: str, remove_stopwords: bool = True) -> str:
    """
    Limpa e normaliza texto para processamento
    
    Processo:
    1. Lowercase
    2. Remove URLs
    3. Remove quebras de linha excessivas
    4. Remove caracteres especiais (mantém acentos PT-BR)
    5. Remove stopwords (opcional)
    
    Args:
        text: Texto a ser limpo
        remove_stopwords: Se True, remove stopwords
        
    Returns:
        Texto limpo e normalizado
    """
    # Lowercase
    t = text.lower()
    
    # Remove URLs
    t = re.sub(r'http\S+|www\.\S+', '', t)
    
    # Normaliza espaços em branco
    t = re.sub(r'\s+', ' ', t)
    
    # Remove múltiplas quebras de linha
    t = re.sub(r'[\r\n]+', ' ', t)
    
    # Remove caracteres especiais, mantém letras com acentos PT-BR
    t = re.sub(r'[^a-z0-9ãâêîôõçáéíóú ]', ' ', t)
    
    # Remove espaços extras
    t = re.sub(r'\s+', ' ', t).strip()
    
    # Remove stopwords se solicitado
    if remove_stopwords:
        tokens = [w for w in t.split() if w not in STOP_WORDS and len(w) > 2]
        return " ".join(tokens)
    
    return t


def extract_summary(text: str, max_chars: int = 150) -> str:
    """
    Extrai um resumo simples do texto (primeiras linhas)
    
    Args:
        text: Texto completo
        max_chars: Máximo de caracteres do resumo
        
    Returns:
        Resumo do texto
    """
    clean = text.strip()
    if len(clean) <= max_chars:
        return clean
    
    # Tenta cortar em uma frase completa
    summary = clean[:max_chars]
    last_period = summary.rfind('.')
    last_exclamation = summary.rfind('!')
    last_question = summary.rfind('?')
    
    last_sentence_end = max(last_period, last_exclamation, last_question)
    
    if last_sentence_end > max_chars * 0.5:  # Se encontrar ponto após metade
        return summary[:last_sentence_end + 1]
    
    return summary + "..."
