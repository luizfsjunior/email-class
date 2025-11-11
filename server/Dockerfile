# Backend Dockerfile - FastAPI com Uvicorn
# Multi-stage build para otimizar tamanho da imagem

FROM python:3.11-slim AS builder

# Instala dependências do sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copia dependências instaladas do builder
COPY --from=builder /root/.local /root/.local

# Copia código da aplicação
COPY ./app ./app

# Cria diretórios necessários
RUN mkdir -p models data

# Baixa recursos NLTK na build
RUN python -c "import nltk; nltk.download('stopwords', quiet=True)"

# Define PATH para incluir pacotes do usuário
ENV PATH=/root/.local/bin:$PATH

# Expõe porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
