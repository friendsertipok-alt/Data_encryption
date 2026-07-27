import json
import os
from datetime import datetime

AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), "audit.log")

def log_audit_event(user_token: str, original_text: str, anonymized_text: str, entity_map: dict):
    """
    Записывает событие перехвата данных в журнал аудита.
    """
    # Считаем количество уникальных скрытых значений
    hidden_count = len(set(entity_map.values()))
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "token": user_token[:10] + "..." if user_token else "no_token",
        "action": "ANONYMIZED_REQUEST",
        "hidden_entities_count": hidden_count,
        "original_text_preview": original_text[:150] + "..." if len(original_text) > 150 else original_text,
    }
    
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
