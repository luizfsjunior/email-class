# 📧 Email Classifier MVP

**Classificador de Emails Produtivo/Improdutivo com Geração de Respostas Sugeridas**

Sistema completo que utiliza Machine Learning e LLMs para classificar emails automaticamente e gerar respostas contextualizadas.

---

## 🎯 Funcionalidades

- ✅ **Classificação Binária**: Produtivo (requer ação) vs Improdutivo (dispensável)
- ✅ **Classificação com OpenAI**: GPT-4o-mini para classificação precisa
- ✅ **Detecção de Spam**: Identifica propaganda e emails comerciais não solicitados
- ✅ **Geração de Respostas**: Sugestões contextualizadas prontas para uso
- ✅ **Upload de Arquivos**: Suporte para .txt e .pdf
- ✅ **Histórico Local**: Últimas análises salvas no navegador
- ✅ **Docker Ready**: Ambiente completo em containers
- ✅ **CI/CD**: Pipelines automatizados com GitHub Actions

---

## 🏗️ Arquitetura

### Stack Tecnológico

**Backend:**
- FastAPI (Python 3.13) - Framework async para APIs REST
- OpenAI API (gpt-4o-mini) - LLM para classificação e geração
- PyMuPDF - Extração de texto de PDFs
- NLTK - Preprocessing de texto (stopwords PT-BR)
- SQLite/PostgreSQL - Persistência de dados

**Frontend:**
- React 18 + TypeScript - SPA moderna e type-safe
- Vite - Build tool rápido
- TailwindCSS - Estilização utility-first
- LocalStorage - Histórico de análises

**Infraestrutura:**
- Docker + Docker Compose - Containerização
- GitHub Actions - CI/CD

### Fluxo de Processamento

```
1. Upload/Texto → 2. Extração → 3. Preprocessing → 4. Classificação OpenAI
                                                          ↓
5. Geração de Resposta ← 6. Persistência ← 7. Retorno JSON
```

---

## 🚀 Quickstart Local

### Pré-requisitos

- Python 3.13+
- Node.js 20+
- Docker + Docker Compose (opcional)
- OpenAI API Key (obrigatório)

### Opção 1: Docker Compose (Recomendado)

```bash
# 1. Clone o repositório
git clone <repo-url>
cd email-class

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY (obrigatório)

# 3. Inicie ambiente completo
docker-compose up --build

# 4. Acesse:
# - Frontend: http://localhost:5173
# - Backend:  http://localhost:8000
# - Docs API: http://localhost:8000/docs
```

### Opção 2: Setup Manual

#### Backend

```bash
cd server

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Configure .env
cp ../.env.example ../.env
# Edite .env com suas credenciais

# Baixe recursos NLTK
python -c "import nltk; nltk.download('stopwords')"

# Inicie servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd client

# Instale dependências
npm install

# Configure variável de ambiente
cp .env.example .env

# Inicie dev server
npm run dev
```

### Opção 3: Makefile (Unix/Linux/Mac)

```bash
# Setup completo
make setup

# Inicia ambiente de desenvolvimento
make dev

# Outros comandos úteis
make help
```

---

## 📚 Uso da API

### Endpoints Principais

#### `POST /api/process`

Processa email e retorna classificação + resposta sugerida.

**Request (multipart/form-data):**
```bash
# Com arquivo
curl -X POST http://localhost:8000/api/process \
  -F "file=@email.txt"

# Com texto direto
curl -X POST http://localhost:8000/api/process \
  -F "text=Prezado, solicito atualização urgente do chamado 12345"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "Produtivo",
  "confidence": 0.92,
  "suggested_reply": "Prezado(a), recebemos sua solicitação...",
  "summary": "Solicitação de atualização de chamado",
  "model_used": "openai-gpt-4o-mini",
  "timestamp": "2025-11-10T15:00:00Z",
  "reason": "Email contém solicitação explícita de ação"
}
```

#### `POST /api/feedback`

Envia feedback sobre uma análise.

```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "rating": 5,
    "edited_reply": "Resposta customizada pelo usuário",
    "comments": "Excelente classificação"
  }'
```

#### `GET /health`

Health check dos serviços.

```bash
curl http://localhost:8000/health
```

**Documentação interativa:** http://localhost:8000/docs

---

## 🧪 Testes

```bash
# Backend - todos os testes
cd server
pytest tests/ -v

# Com coverage
pytest tests/ --cov=app --cov-report=html

# Frontend - lint
cd client
npm run lint

# Via Makefile
make test
```

---

## 🔑 Configuração de Ambiente

### Variáveis Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `OPENAI_API_KEY` | Chave API OpenAI (obrigatório) | `sk-...` |
| `DATABASE_URL` | URL do banco de dados | `sqlite:///./db.sqlite3` |
| `CORS_ORIGINS` | URLs permitidas (CORS) | `http://localhost:5173` |

### Variáveis Opcionais

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `APP_ENV` | `development` | Ambiente (development/production) |
| `LLM_MODEL` | `gpt-4o-mini` | Modelo OpenAI a usar |
| `LLM_TEMPERATURE` | `0.3` | Temperatura do modelo (0-1) |
| `MAX_UPLOAD_SIZE` | `1048576` | Tamanho máx upload (bytes) |


---


## 📊 Classificação com OpenAI

O sistema utiliza OpenAI GPT-4o-mini para:

- **Classificação**: Produtivo vs Improdutivo com precisão calibrada (0.60-0.99)
- **Detecção de Spam**: Identifica propaganda, ofertas comerciais não solicitadas
- **Geração de Respostas**: Contextualizadas e personalizadas por tipo de email
- **Custo-benefício**: ~$0.15/1M tokens input (~R$ 0,75)

### Configuração do Modelo

Edite `server/.env`:
```env
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3  # Classificação consistente
LLM_MAX_TOKENS=500
```

---

## 🔒 Segurança e Privacidade

### Políticas Implementadas

✅ **Não logar dados sensíveis**: PII (CPF, cartões) não são gravados em logs  
✅ **Armazenamento condicional**: `full_text` só salvo em `APP_ENV=development`  
✅ **Hashing**: Textos hasheados (SHA256) para deduplicação sem expor conteúdo  
✅ **CORS configurado**: Apenas origins autorizadas  
✅ **Rate limiting**: (TODO) Implementar throttling em produção  
✅ **HTTPS obrigatório**: Em produção, use TLS (Render/Vercel já incluem)


## 📖 Documentação Adicional

- [PROMPTS.md](./docs/PROMPTS.md) - Prompts do LLM e variações para A/B testing
- [docs/architecture.md](./docs/architecture.md) - Arquitetura detalhada do sistema
- API Docs: http://localhost:8000/docs (após iniciar backend)

---

## 🛠️ Troubleshooting

### Backend não inicia

```bash
# Verifique dependências
pip list | grep fastapi

# Reinstale
pip install -r server/requirements.txt --force-reinstall

# Verifique porta ocupada
lsof -i :8000  # Unix/Mac
netstat -ano | findstr :8000  # Windows
```

### Frontend não conecta ao backend

1. Verifique `VITE_API_URL` em `client/.env`
2. Confirme backend está rodando: `curl http://localhost:8000/health`
3. Verifique console do navegador para erros CORS


### OpenAI API falha

- Verifique créditos: https://platform.openai.com/usage
- Confirme chave em `.env`: `echo $OPENAI_API_KEY`
- Sistema retornará erro HTTP 500 se OpenAI indisponível

---

## 📝 Roadmap

### v1.0 (Atual - MVP)
- [x] Classificação binária
- [x] Geração de respostas
- [x] Upload PDF/TXT
- [x] Histórico local
- [x] Docker + CI/CD

---

## 📄 Licença

MIT License - veja [LICENSE](./LICENSE)

---

## 👥 Autores

Desenvolvido como MVP para demonstração de IA aplicada em triagem de emails.

**Justificativas Técnicas:**

- **FastAPI**: Escolhido por performance async, type hints, e docs automáticas
- **OpenAI GPT-4o-mini**: Melhor custo-benefício (~10x mais barato que GPT-4)
- **SQLite → Postgres**: Fácil migração via SQLAlchemy/DATABASE_URL
- **Tailwind**: Produtividade e bundle size otimizado
- **Vercel + Render**: Planos gratuitos generosos para MVPs

---

## 🆘 Suporte

- Issues: [GitHub Issues](https://github.com/luizfsjunior/email-class/issues)
- Email: luizfsjunior.2002@gmail.com
- Docs: http://localhost:8000/docs

