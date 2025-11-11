"""
Text extraction service - Extrai texto de PDFs e arquivos texto
Utiliza PyMuPDF (fitz) para PDFs por ser rápido e confiável
"""
import fitz  # PyMuPDF
from typing import Union


def extract_pdf_text_bytes(file_bytes: bytes) -> str:
    """
    Extrai texto de um PDF a partir de bytes
    
    Args:
        file_bytes: Bytes do arquivo PDF
        
    Returns:
        Texto extraído de todas as páginas
        
    Raises:
        Exception: Se houver erro ao abrir ou processar o PDF
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Extrai texto baseado na extensão do arquivo
    
    Args:
        file_bytes: Bytes do arquivo
        filename: Nome do arquivo (usado para determinar extensão)
        
    Returns:
        Texto extraído
        
    Raises:
        ValueError: Se formato não suportado
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_pdf_text_bytes(file_bytes)
    elif filename_lower.endswith('.txt'):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback para latin-1 se UTF-8 falhar
            return file_bytes.decode('latin-1')
    else:
        raise ValueError(f"Formato de arquivo não suportado: {filename}")
