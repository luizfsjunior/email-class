# 🏗️ Arquitetura do Sistema - Email Classifier

## Visão Geral

Sistema de classificação de emails com arquitetura em 3 camadas: Frontend (React), Backend (FastAPI), e Integração OpenAI.

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React + TypeScript + Tailwind (SPA)                        │
│  - Upload de arquivos (.txt/.pdf)                           │
│  - Interface de resultado                                    │
│  - Histórico (localStorage)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
                     │ (JSON)
┌────────────────────▼────────────────────────────────────────┐
│                       BACKEND                                │
│  FastAPI (Python 3.13 - Async)                             │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Layer (Endpoints)                              │   │
│  │  /api/process, /api/feedback, /health              │   │
│  └──────────┬──────────────────────────────────────────┘   │
│             │                                               │
│  ┌──────────▼──────────────────────────────────────────┐   │
│  │  Services Layer                                      │   │
│  │  - parsing.py    (PDF/TXT extraction)               │   │
│  │  - nlp.py        (Preprocessing)                    │   │
│  │  - ai_client.py  (OpenAI integration)               │   │
│  └──────────┬──────────────────────────────────────────┘   │
│             │                                               │
│  ┌──────────▼──────────────────────────────────────────┐   │
│  │  Data Layer                                          │   │
│  │  - database.py (SQLite/Postgres)                    │   │
│  │  - models/schemas.py (Pydantic)                     │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌────────────────────────┐
         │                        │
      ┌────▼───┐             ┌────▼────┐       
      │ OpenAI │             │ SQLite/ │       
      │  API   │             │Postgres │       
      └────────┘             └─────────┘       
```

## Componentes Principais

### Frontend (client/)

**Stack:** React 18 + TypeScript + Vite + TailwindCSS

#### Estrutura de Arquivos
```
client/
├── src/
│   ├── components/
│   │   ├── EmailForm.tsx      # Formulário upload/texto
│   │   ├── ResultDisplay.tsx  # Exibição de resultado
│   │   └── History.tsx        # Histórico de análises
│   ├── services/
│   │   └── api.ts             # Cliente HTTP (fetch)
│   ├── lib/
│   │   └── storage.ts         # localStorage helpers
│   ├── App.tsx                # Componente raiz
│   └── main.tsx               # Entry point
├── index.html
└── package.json
```

#### Fluxo de Dados
1. Usuário faz upload ou cola texto
2. `EmailForm` valida input
3. `api.processFile()` ou `api.processText()` chama backend
4. `ResultDisplay` exibe resposta
5. `storage.addItem()` salva no localStorage

### Backend (server/)

**Stack:** FastAPI + Uvicorn + SQLAlchemy + OpenAI SDK

#### Estrutura de Arquivos
```
server/
├── app/
│   ├── api/
│   │   └── process.py         # Endpoints principais
│   ├── services/
│   │   ├── parsing.py         # Extração de texto
│   │   ├── nlp.py             # Preprocessing NLP
│   │   └── ai_client.py       # OpenAI integration
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── core/
│   │   └── settings.py        # Configuração (.env)
│   ├── utils/
│   │   └── database.py        # SQLite/Postgres
│   └── main.py                # FastAPI app
├── tests/                     # Pytest tests
└── requirements.txt
```

#### Pipeline de Processamento

```python
# Pseudo-código do fluxo principal
async def process_email(file_or_text):
    # 1. Extração
    text = extract_text(file_or_text)
    
    # 2. Preprocessing
    clean = clean_text(text)
    summary = extract_summary(text)
    
    # 3. Classificação via OpenAI
    result = await openai_client.classify(clean)
    
    # 4. Geração de resposta
    reply = await openai_client.generate_reply(result, summary)
    
    # 5. Persistência
    db.save_analysis({...})
    
    # 6. Retorno
    return ProcessResponse(...)
```

## Integrações Externas

### OpenAI API

**Modelo:** gpt-4o-mini  
**Custo:** ~$0.15/1M tokens input, ~$0.60/1M output  
**Rate Limits:** 500 RPM, 200k TPM (tier free)

**Configuração:**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.3,
    max_tokens=500,
    response_format={"type": "json_object"}
)
```

**Tratamento de Erros:**
1. Timeout de 10s por requisição
2. Se falhar → retorna HTTP 500 com mensagem de erro
3. Logs de erro para monitoramento e debug

### Base de Dados

**Desenvolvimento:** SQLite  
**Produção:** PostgreSQL (recomendado)

**Schema:**

```sql
-- Tabela de análises
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,
    text_hash TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    suggested_reply TEXT NOT NULL,
    summary TEXT NOT NULL,
    model_used TEXT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    full_text TEXT,  -- Apenas em dev
    metadata TEXT
);

-- Tabela de feedback
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    edited_reply TEXT,
    user_category TEXT,
    rating INTEGER,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);
```

## Segurança

### Camadas de Proteção

1. **Input Validation**
   - Tamanho máximo: 1MB
   - Formatos: .txt, .pdf
   - Sanitização de paths

2. **CORS**
   - Whitelist de origins
   - Credentials controlados

3. **Secrets Management**
   - Todas keys em .env
   - Nunca no código
   - .env no .gitignore

4. **Data Privacy**
   - PII não logada
   - `full_text` só em dev
   - Hash SHA256 para dedup

5. **Rate Limiting** (TODO)
   - Implementar throttling
   - IP-based limits

## Deploy

### Ambientes

| Ambiente | Frontend | Backend | Database |
|----------|----------|---------|----------|
| Dev | localhost:5173 | localhost:8000 | SQLite |
| Staging | Vercel preview | Render dev | Postgres |
| Prod | Vercel | Render/Cloud Run | Postgres |

### CI/CD Pipeline

```
┌─────────────┐
│ Git Push    │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────┐
│ GitHub Actions                          │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ 1. Testes                       │    │
│ │    - pytest (backend)           │    │
│ │    - eslint (frontend)          │    │
│ └──────────┬──────────────────────┘    │
│            │                            │
│ ┌──────────▼──────────────────────┐    │
│ │ 2. Build                        │    │
│ │    - Docker images              │    │
│ │    - Vite build                 │    │
│ └──────────┬──────────────────────┘    │
│            │                            │
│ ┌──────────▼──────────────────────┐    │
│ │ 3. Deploy (main branch only)    │    │
│ │    - Frontend → Vercel          │    │
│ │    - Backend → Render           │    │
│ └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## Monitoramento (Futuro)

### Métricas Chave

1. **Performance**
   - Latência p50, p95, p99
   - Throughput (req/s)
   - Erro rate

2. **Negócio**
   - Classificações/dia
   - % Produtivo vs Improdutivo
   - Rating médio
   - Taxa de edição de respostas

3. **Custos**
   - $ por classificação
   - Tokens consumidos
   - Taxa de erro OpenAI

### Stack Sugerida

- **Logs:** structlog → CloudWatch/Datadog
- **Métricas:** Prometheus + Grafana
- **Alertas:** PagerDuty/Slack
- **APM:** New Relic/Sentry

## Escalabilidade

### Bottlenecks Atuais

1. **OpenAI API:** Rate limits (500 RPM)
2. **SQLite:** Single-write (ok para MVP)
3. **Sincronous Processing:** Sem fila

### Soluções Futuras

```
┌──────────────┐
│   Nginx LB   │  # Load balancer
└──────┬───────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼───┐  # Múltiplas instâncias FastAPI
│ API │  │ API │
└──┬──┘  └──┬──┘
   │        │
   └───┬────┘
       │
┌──────▼────────┐
│  Redis Queue  │  # Fila assíncrona
└──────┬────────┘
       │
┌──────▼────────┐
│   Postgres    │  # DB escalável
└───────────────┘
```

## Decisões de Design

### Por que FastAPI?
- ✅ Performance comparável a Node.js
- ✅ Type hints nativos
- ✅ Documentação automática (Swagger)
- ✅ Async/await
- ❌ Menos maduro que Flask/Django

### Por que gpt-4o-mini?
- ✅ 10x mais barato que GPT-4
- ✅ Latência menor (~1s vs ~3s)
- ✅ Suficiente para classificação binária
- ❌ Menos capaz em tarefas muito complexas

### Por que SQLite → Postgres?
- ✅ SQLite: zero config, perfeito para MVP
- ✅ Postgres: escalável, ACID completo
- ✅ Migração trivial via DATABASE_URL
- ❌ SQLite: single-write, sem clustering

---

**Versão:** 1.0.0  
**Última atualização:** 2025-11-10
