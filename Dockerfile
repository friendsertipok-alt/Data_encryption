FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
# В продакшене лучше использовать requirements.txt, но для прототипа установим напрямую
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    python-multipart \
    presidio-analyzer \
    presidio-anonymizer \
    faker \
    pymorphy3 \
    natasha \
    pymupdf \
    python-docx \
    openpyxl \
    python-pptx \
    spacy

# Загрузка языковых моделей
RUN python -m spacy download ru_core_news_md
RUN python -m spacy download en_core_web_sm

# Копирование исходного кода
COPY . .

# Проброс порта
EXPOSE 8001

# Запуск
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
