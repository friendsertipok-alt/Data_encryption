FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для Tesseract OCR и графики
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    python-multipart \
    presidio-analyzer \
    presidio-anonymizer \
    faker \
    pymorphy3 \
    pymorphy3-dicts-ru \
    natasha \
    pymupdf \
    python-docx \
    openpyxl \
    xlrd \
    python-pptx \
    pytesseract \
    pillow \
    cryptography \
    spacy

# Загрузка языковых моделей spaCy
RUN python -m spacy download ru_core_news_md
RUN python -m spacy download en_core_web_sm

# Копирование исходного кода
COPY . .

# Проброс порта
EXPOSE 8001

# Запуск DLP Gateway
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
