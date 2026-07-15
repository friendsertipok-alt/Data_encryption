"""
Профили пользователей и системные промпты.
В реальном проде это была бы PostgreSQL база данных.
Для прототипа — JSON-файл + Python-словарь.
"""
import json
import os
from pathlib import Path

# Файл хранилища пользователей и промптов
DATA_FILE = Path(__file__).parent / "data" / "profiles.json"

# =======================================================
# СТАНДАРТНЫЕ СИСТЕМНЫЕ ПРОМПТЫ ПО ОТДЕЛАМ
# =======================================================
DEFAULT_DEPARTMENT_PROMPTS = {
    "legal": (
        "Ты опытный корпоративный юрист компании. Отвечай строго в рамках законодательства РФ. "
        "При анализе документов всегда указывай на юридические риски и возможные последствия. "
        "Структурируй ответы: используй нумерованные списки и заголовки. "
        "Если задача требует официального заключения, предупреди, что ответ носит информационный характер."
    ),
    "finance": (
        "Ты финансовый аналитик компании. Работаешь с цифрами точно и без ошибок. "
        "Всегда используй таблицы для сравнения показателей. "
        "При анализе документов выделяй ключевые финансовые метрики (EBITDA, маржинальность, ROI). "
        "Ответы давай кратко и по делу, без воды."
    ),
    "accounting": (
        "Ты опытный бухгалтер. Работаешь в соответствии с ПБУ, НК РФ и ФСБУ. "
        "При анализе документов проверяй корректность проводок и соответствие законодательству. "
        "Если видишь ошибку или риск — сразу указывай на это. "
        "Помогай формировать отчёты и сводные таблицы."
    ),
    "hr": (
        "Ты HR-специалист компании. Отвечаешь строго в соответствии с ТК РФ. "
        "Помогаешь с кадровыми документами, оформлением, мотивацией персонала. "
        "Поддерживай поддерживающий и профессиональный тон в ответах. "
        "При вопросах об увольнении всегда указывай на права сотрудника."
    ),
    "management": (
        "Ты бизнес-ассистент руководства. Помогаешь с анализом данных, подготовкой презентаций и отчётов. "
        "Давай ёмкие выводы и рекомендации. Структурируй ответы для удобства восприятия топ-менеджментом. "
        "Используй деловой язык без технического жаргона."
    ),
    "default": (
        "Ты умный корпоративный ассистент компании. Помогай сотрудникам с рабочими задачами. "
        "Отвечай вежливо, точно и по делу. Если не знаешь ответа — честно скажи об этом."
    ),
}

# =======================================================
# ФУНКЦИИ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ
# =======================================================

def _load_data() -> dict:
    """Загружает данные из JSON файла."""
    DATA_FILE.parent.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        # Инициализируем с дефолтными данными
        initial_data = {
            "departments": {
                "legal": {"name": "Юридический департамент", "prompt": DEFAULT_DEPARTMENT_PROMPTS["legal"]},
                "finance": {"name": "Финансовый департамент", "prompt": DEFAULT_DEPARTMENT_PROMPTS["finance"]},
                "accounting": {"name": "Бухгалтерия", "prompt": DEFAULT_DEPARTMENT_PROMPTS["accounting"]},
                "hr": {"name": "HR", "prompt": DEFAULT_DEPARTMENT_PROMPTS["hr"]},
                "management": {"name": "Руководство", "prompt": DEFAULT_DEPARTMENT_PROMPTS["management"]},
                "default": {"name": "Общий", "prompt": DEFAULT_DEPARTMENT_PROMPTS["default"]},
            },
            "users": {
                # Ключ — API-токен (используется как Bearer token в Open-WebUI)
                # В реальной системе это будет JWT от Open-WebUI
                "token-user-1": {
                    "name": "Пользователь 1",
                    "email": "user1@company.com",
                    "department": "legal",
                    "custom_prompt": None,  # Если None — используется промпт отдела
                    "token_budget": 50000,
                    "tokens_used": 0,
                },
                "token-user-2": {
                    "name": "Пользователь 2",
                    "email": "user2@company.com",
                    "department": "finance",
                    "custom_prompt": None,
                    "token_budget": 50000,
                    "tokens_used": 0,
                },
                "token-user-3": {
                    "name": "Пользователь 3",
                    "email": "user3@company.com",
                    "department": "accounting",
                    "custom_prompt": None,
                    "token_budget": 50000,
                    "tokens_used": 0,
                },
                "token-user-4": {
                    "name": "Пользователь 4",
                    "email": "user4@company.com",
                    "department": "hr",
                    "custom_prompt": None,
                    "token_budget": 50000,
                    "tokens_used": 0,
                },
                "token-admin": {
                    "name": "Администратор",
                    "email": "admin@company.com",
                    "department": "management",
                    "custom_prompt": None,
                    "token_budget": 500000,
                    "tokens_used": 0,
                },
            },
            "settings": {
                "dlp_enabled": True,
                "min_score_threshold": 0.5,
                "cloud_api_url": "https://api.anthropic.com/v1/messages",
                "cloud_model": "claude-sonnet-4-5",
            }
        }
        _save_data(initial_data)
        return initial_data
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_data(data: dict):
    """Сохраняет данные в JSON файл."""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_system_prompt_for_token(token: str) -> str:
    """
    По токену авторизации находит пользователя и возвращает 
    его персональный системный промпт или промпт его отдела.
    """
    data = _load_data()
    user = data["users"].get(token)
    
    if not user:
        print(f"[Profiles] Токен '{token}' не найден. Используем дефолтный промпт.")
        return data["departments"]["default"]["prompt"]
    
    # Приоритет: персональный промпт > промпт отдела
    if user.get("custom_prompt"):
        print(f"[Profiles] Пользователь '{user['name']}' — применён персональный промпт.")
        return user["custom_prompt"]
    
    dept_id = user.get("department", "default")
    dept = data["departments"].get(dept_id, data["departments"]["default"])
    print(f"[Profiles] Пользователь '{user['name']}' ({dept['name']}) — применён промпт отдела.")
    return dept["prompt"]


def get_user_department(token: str) -> str:
    """Возвращает отдел пользователя по токену для RBAC-фильтрации."""
    data = _load_data()
    user = data["users"].get(token)
    if not user:
        return "all"
    return user.get("department", "all")


def get_all_data() -> dict:
    return _load_data()


def save_all_data(data: dict):
    _save_data(data)


def is_dlp_enabled() -> bool:
    data = _load_data()
    return data.get("settings", {}).get("dlp_enabled", True)


def get_user_budget_info(token: str) -> dict:
    """Возвращает информацию о бюджете пользователя."""
    data = _load_data()
    user = data["users"].get(token)
    if not user:
        return {"budget": 10000, "used": 0} # Значения по умолчанию для неизвестных
    
    return {
        "budget": user.get("token_budget", 10000),
        "used": user.get("tokens_used", 0)
    }


def check_budget(token: str, estimated_cost: int) -> bool:
    """Проверяет, достаточно ли бюджета для выполнения запроса."""
    info = get_user_budget_info(token)
    return (info["used"] + estimated_cost) <= info["budget"]


def charge_tokens(token: str, actual_cost: int):
    """Списывает токены с баланса пользователя."""
    data = _load_data()
    user = data["users"].get(token)
    if user:
        current_used = user.get("tokens_used", 0)
        user["tokens_used"] = current_used + actual_cost
        _save_data(data)

