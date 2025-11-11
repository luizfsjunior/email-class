# Makefile - Comandos úteis para desenvolvimento

.PHONY: help dev build test clean install

# Variáveis
PYTHON := python
PIP := pip
NPM := npm
DOCKER_COMPOSE := docker-compose

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Instalação
install: ## Instala todas as dependências (backend + frontend)
	@echo "📦 Instalando dependências do backend..."
	cd server && $(PIP) install -r requirements.txt
	@echo "📦 Instalando dependências do frontend..."
	cd client && $(NPM) install
	@echo "✅ Instalação concluída!"

install-backend: ## Instala apenas dependências do backend
	cd server && $(PIP) install -r requirements.txt

install-frontend: ## Instala apenas dependências do frontend
	cd client && $(NPM) install

# Desenvolvimento
dev: ## Inicia ambiente de desenvolvimento com docker-compose
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	$(DOCKER_COMPOSE) up --build

dev-backend: ## Inicia apenas o backend em modo desenvolvimento
	cd server && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Inicia apenas o frontend em modo desenvolvimento
	cd client && $(NPM) run dev

# Build
build: ## Build dos containers Docker
	@echo "🏗️  Building containers..."
	$(DOCKER_COMPOSE) build

build-backend: ## Build apenas do backend
	docker build -t email-classifier-backend ./server

build-frontend: ## Build apenas do frontend
	docker build -t email-classifier-frontend ./client

# Testes
test: ## Executa todos os testes
	@echo "🧪 Executando testes do backend..."
	cd server && pytest tests/ -v
	@echo "🧪 Executando lint do frontend..."
	cd client && $(NPM) run lint

test-backend: ## Executa apenas testes do backend
	cd server && pytest tests/ -v --cov=app

test-watch: ## Executa testes em modo watch
	cd server && pytest-watch tests/

lint: ## Executa linters (flake8 + eslint)
	@echo "🔍 Linting backend..."
	cd server && flake8 app/ tests/
	@echo "🔍 Linting frontend..."
	cd client && $(NPM) run lint

# Database
db-init: ## Inicializa banco de dados
	@echo "💾 Inicializando banco de dados..."
	cd server && $(PYTHON) -c "from app.utils.database import get_database; get_database()"

# Limpeza
clean: ## Remove arquivos temporários e caches
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf server/htmlcov server/.coverage
	rm -f server/db.sqlite3 server/test_db.sqlite3
	@echo "✅ Limpeza concluída!"

clean-docker: ## Remove containers e volumes Docker
	$(DOCKER_COMPOSE) down -v

# Utilitários
logs: ## Mostra logs dos containers
	$(DOCKER_COMPOSE) logs -f

stop: ## Para todos os containers
	$(DOCKER_COMPOSE) stop

restart: ## Reinicia todos os containers
	$(DOCKER_COMPOSE) restart

shell-backend: ## Abre shell no container do backend
	$(DOCKER_COMPOSE) exec backend /bin/sh

shell-frontend: ## Abre shell no container do frontend
	$(DOCKER_COMPOSE) exec frontend /bin/sh

# Setup inicial
setup: install ## Setup completo: instala dependências
	@echo "✅ Setup inicial concluído!"
	@echo ""
	@echo "Próximos passos:"
	@echo "1. Copie .env.example para .env e configure OPENAI_API_KEY"
	@echo "2. Execute 'make dev' para iniciar o ambiente"

# Health check
health: ## Verifica status dos serviços
	@echo "🏥 Verificando saúde dos serviços..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ Backend offline"
	@curl -s http://localhost:5173 > /dev/null && echo "✅ Frontend online" || echo "❌ Frontend offline"
