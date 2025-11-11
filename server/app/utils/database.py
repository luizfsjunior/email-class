"""
Database utilities - Gerenciamento de conexão e operações básicas
Usa SQLite para MVP, facilmente migrável para Postgres
"""
import sqlite3
import hashlib
import logging
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class Database:
    """Classe para operações de banco de dados"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = self._parse_db_path()
        self._init_db()
    
    def _parse_db_path(self) -> str:
        """Extrai caminho do DATABASE_URL"""
        url = self.settings.DATABASE_URL
        if url.startswith("sqlite:///"):
            path = url.replace("sqlite:///", "")
            # Cria diretório se não existir
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            return path
        return "db.sqlite3"
    
    def _init_db(self):
        """Inicializa schema do banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de análises
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    text_hash TEXT NOT NULL,
                    category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    suggested_reply TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    full_text TEXT,
                    metadata TEXT
                )
            """)
            
            # Tabela de feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    edited_reply TEXT,
                    user_category TEXT,
                    rating INTEGER,
                    comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
                )
            """)
            
            # Índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_text_hash ON analyses(text_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON analyses(created_at)")
            
            conn.commit()
            conn.close()
            logger.info(f"Database inicializado: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar database: {str(e)}")
    
    def save_analysis(self, analysis_data: Dict) -> bool:
        """Salva resultado de análise"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash do texto (para deduplicação)
            text_hash = hashlib.sha256(
                analysis_data.get("full_text", "").encode()
            ).hexdigest()
            
            # Decide se salva full_text baseado no ambiente
            full_text = None
            if self.settings.APP_ENV == "development":
                full_text = analysis_data.get("full_text")
            
            cursor.execute("""
                INSERT INTO analyses 
                (id, text_hash, category, confidence, suggested_reply, summary, model_used, reason, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_data["id"],
                text_hash,
                analysis_data["category"],
                analysis_data["confidence"],
                analysis_data["suggested_reply"],
                analysis_data["summary"],
                analysis_data["model_used"],
                analysis_data.get("reason"),
                full_text
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise: {str(e)}")
            return False
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Busca análise por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM analyses WHERE id = ?
            """, (analysis_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar análise: {str(e)}")
            return None
    
    def save_feedback(self, feedback_data: Dict) -> bool:
        """Salva feedback do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback 
                (analysis_id, edited_reply, user_category, rating, comments)
                VALUES (?, ?, ?, ?, ?)
            """, (
                feedback_data["analysis_id"],
                feedback_data.get("edited_reply"),
                feedback_data.get("user_category"),
                feedback_data.get("rating"),
                feedback_data.get("comments")
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar feedback: {str(e)}")
            return False
    
    def check_duplicate(self, text: str) -> Optional[str]:
        """Verifica se texto já foi processado (retorna ID se sim)"""
        try:
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM analyses 
                WHERE text_hash = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (text_hash,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return row[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao verificar duplicata: {str(e)}")
            return None


# Singleton instance
_database: Optional[Database] = None

def get_database() -> Database:
    """Retorna instância singleton do database"""
    global _database
    if _database is None:
        _database = Database()
    return _database
