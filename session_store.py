import sqlite3
import json
import os
import uuid
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from config import DB_PATH, SESSION_TTL_HOURS, SECRET_KEY

def _get_fernet() -> Fernet:
    """Генерирует криптографический ключ Fernet (AES-256) из SECRET_KEY"""
    key = base64.urlsafe_b64encode(hashlib.sha256(SECRET_KEY.encode()).digest())
    return Fernet(key)

def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация таблицы сессий в SQLite с поддержкой групповых сессий."""
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                group_id TEXT,
                user_token TEXT NOT NULL,
                filename TEXT NOT NULL,
                entity_map_json TEXT NOT NULL,
                entities_count INTEGER NOT NULL,
                lang TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        # Миграция: проверяем наличие колонки group_id для существующих баз
        cursor = conn.execute("PRAGMA table_info(sessions)")
        columns = [row[1] for row in cursor.fetchall()]
        if "group_id" not in columns:
            conn.execute("ALTER TABLE sessions ADD COLUMN group_id TEXT")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_token);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_group ON sessions(group_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at);")
        conn.commit()

init_db()

def create_session(entity_map: dict, filename: str = "unknown", user_token: str = "default", lang: str = "ru", group_id: Optional[str] = None) -> str:
    """
    Создает новую сессию анонимизации.
    Поддерживает привязку к групповой сессии (group_id) для сквозной анонимизации пакета файлов.
    Карта замен (Entity Map) шифруется по алгоритму AES-256 (Fernet).
    """
    session_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    # 1. Сериализуем JSON в строку
    raw_json = json.dumps(entity_map, ensure_ascii=False)
    
    # 2. Шифруем (Encryption at Rest)
    fernet = _get_fernet()
    encrypted_json = fernet.encrypt(raw_json.encode('utf-8')).decode('utf-8')
    
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, group_id, user_token, filename, entity_map_json, entities_count, lang, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, group_id, user_token, filename, encrypted_json, len(entity_map), lang, created_at)
        )
        conn.commit()
        
    return session_id

def _decrypt_map(stored_data: str) -> dict:
    fernet = _get_fernet()
    try:
        decrypted_bytes = fernet.decrypt(stored_data.encode('utf-8'))
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception:
        try:
            return json.loads(stored_data)
        except Exception:
            return {}

def get_group_entity_map(group_id: str) -> dict:
    """Возвращает объединенную карту замен для всех сессий в указанной группе."""
    combined_map = {}
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT entity_map_json FROM sessions WHERE group_id = ? ORDER BY created_at ASC", (group_id,)
        ).fetchall()
        for row in rows:
            if row["entity_map_json"]:
                m = _decrypt_map(row["entity_map_json"])
                combined_map.update(m)
    return combined_map

def get_session_map(session_identifier: str) -> Optional[dict]:
    """
    Извлекает и расшифровывает маппинг сущностей (Entity Map).
    Поддерживает:
    1. Одиночный session_id: "550e8400-e29b-41d4-a716-446655440000"
    2. Список session_id через запятую: "id1, id2, id3"
    3. Групповой Идентификатор group_id: "GRP-PROJECT_2026"
    """
    if not session_identifier or not session_identifier.strip():
        return None

    raw_input = session_identifier.strip()
    
    # Делим по запятым или пробелам
    parts = [p.strip() for p in raw_input.replace("\n", ",").split(",") if p.strip()]
    
    combined_map = {}
    found_any = False
    
    fernet = _get_fernet()
    
    with _get_connection() as conn:
        for part in parts:
            # Сначала ищем как одиночный session_id
            row = conn.execute(
                "SELECT entity_map_json FROM sessions WHERE session_id = ?", (part,)
            ).fetchone()
            
            if row and row["entity_map_json"]:
                found_any = True
                combined_map.update(_decrypt_map(row["entity_map_json"]))
            else:
                # Если не найден как session_id, пробуем как group_id
                group_rows = conn.execute(
                    "SELECT entity_map_json FROM sessions WHERE group_id = ? ORDER BY created_at ASC", (part,)
                ).fetchall()
                if group_rows:
                    found_any = True
                    for g_row in group_rows:
                        if g_row["entity_map_json"]:
                            combined_map.update(_decrypt_map(g_row["entity_map_json"]))

    return combined_map if found_any else None

def get_user_sessions(user_token: str = "default") -> list:
    """Возвращает список сессий пользователя с информацией о группах."""
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT session_id, group_id, filename, created_at, entities_count
            FROM sessions
            WHERE user_token = ?
            ORDER BY created_at DESC
            """,
            (user_token,)
        ).fetchall()
        
        return [
            {
                "session_id": row["session_id"],
                "group_id": row["group_id"],
                "filename": row["filename"],
                "entities_count": row["entities_count"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

def cleanup_expired_sessions(ttl_hours: int = SESSION_TTL_HOURS):
    """Удаляет сессии старше указанного времени TTL."""
    cutoff_time = (datetime.now() - timedelta(hours=ttl_hours)).isoformat()
    with _get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE created_at < ?", (cutoff_time,))
        conn.commit()
