import os
import secrets

# Основные настройки сервера
HOST = os.getenv("DLP_HOST", "0.0.0.0")
PORT = int(os.getenv("DLP_PORT", "8001"))

# Настройки безопасности и авторизации
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() in ("true", "1", "yes")
VALID_API_KEYS = set(os.getenv("API_KEYS", "test_key_123").split(","))

# База данных SQLite и сессии
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "data", "dlp_gateway.db"))
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "24"))
# ВАЖНО: В продакшене обязательно задайте SECRET_KEY через переменную окружения!
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))

# Кэширование детектора
CACHE_CAPACITY = int(os.getenv("CACHE_CAPACITY", "2048"))

# CORS
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*").split(",")

