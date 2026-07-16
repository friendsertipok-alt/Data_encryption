import os

# Основные настройки
HOST = os.getenv("DLP_HOST", "0.0.0.0")
PORT = int(os.getenv("DLP_PORT", "8001"))

# Настройки LLM Proxy
UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://api.openai.com/v1/chat/completions")
UPSTREAM_API_KEY = os.getenv("UPSTREAM_API_KEY", "") # Можно задать тут или пробрасывать от клиента

# Кэширование
CACHE_CAPACITY = int(os.getenv("CACHE_CAPACITY", "2048"))

# Настройки безопасности
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*").split(",")
