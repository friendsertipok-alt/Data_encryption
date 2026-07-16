import json
import os
import uuid
from datetime import datetime

SESSION_STORE_FILE = "data/sessions.json"

def _load_sessions():
    if not os.path.exists(SESSION_STORE_FILE):
        return {}
    try:
        with open(SESSION_STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_sessions(data):
    os.makedirs(os.path.dirname(SESSION_STORE_FILE), exist_ok=True)
    with open(SESSION_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_session(entity_map, filename="unknown", user_token="default", lang="ru"):
    """Создает новую сессию для пользователя и сохраняет маппинг"""
    sessions = _load_sessions()
    session_id = str(uuid.uuid4())
    
    sessions[session_id] = {
        "user_token": user_token,
        "filename": filename,
        "entity_map": entity_map,
        "entities_count": len(entity_map),
        "lang": lang,
        "created_at": datetime.now().isoformat()
    }
    
    _save_sessions(sessions)
    return session_id

def get_session_map(session_id):
    """Возвращает маппинг по ID сессии"""
    sessions = _load_sessions()
    if session_id in sessions:
        return sessions[session_id].get("entity_map", {})
    return None

def get_user_sessions(user_token="default"):
    """Возвращает список сессий пользователя"""
    sessions = _load_sessions()
    user_sessions = []
    for sid, data in sessions.items():
        if data.get("user_token") == user_token:
            user_sessions.append({
                "session_id": sid,
                "filename": data.get("filename", "unknown"),
                "created_at": data.get("created_at")
            })
    # Сортируем от новых к старым
    user_sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return user_sessions
