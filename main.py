import os
import urllib.parse
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, Response, Depends, HTTPException, status, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import ENABLE_AUTH, VALID_API_KEYS, ALLOW_ORIGINS
from core.dependencies import detector
from session_store import create_session, get_session_map, get_user_sessions, cleanup_expired_sessions, get_group_entity_map
from parsers.office import OfficeParser
from parsers.plain import PlainParser
from parsers.pdf import PdfParser
from parsers.openoffice import OpenOfficeParser
from parsers.archive import ArchiveParser

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Очистка устаревших сессий при запуске сервера"""
    cleanup_expired_sessions()
    yield

app = FastAPI(
    title="Universal DLP Gateway API",
    description="Высокопроизводительный DLP-шлюз для анонимизации и деанонимизации конфиденциальных данных в тексте и документах.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Проверка API-ключа (если включен параметр ENABLE_AUTH в config.py)"""
    if not ENABLE_AUTH:
        return api_key or "guest"
        
    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или отсутствующий API-ключ (X-API-Key)"
        )
    return api_key


# --- Pydantic модели ---
class AnonymizeTextRequest(BaseModel):
    text: str = Field(..., description="Исходный текст для анонимизации", example="Иванов Иван (ivanov@mail.ru), тел +7 999 123-45-67")
    mode: str = Field("fake", description="Режим маскирования: 'fake' (реалистичные данные) или 'tags' (теги)")
    lang: str = Field("auto", description="Язык текста: 'ru', 'en' или 'auto'")
    group_id: str | None = Field(None, description="Код Группы/Проекта для сквозной анонимизации пакета файлов")

class AnonymizeTextResponse(BaseModel):
    anonymized_text: str
    session_id: str
    group_id: str | None
    entities_found: int

class DeanonymizeTextRequest(BaseModel):
    text: str = Field(..., description="Маскированный текст для восстановления")
    session_id: str = Field(..., description="ID сессии, список сессий через запятую или Group ID")

class DeanonymizeTextResponse(BaseModel):
    restored_text: str
    session_id: str


# --- REST API: Работа с текстом ---

@app.post("/api/anonymize/text", response_model=AnonymizeTextResponse, tags=["Text DLP"])
async def anonymize_text(
    payload: AnonymizeTextRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Анонимизирует конфиденциальные данные в строковом тексте.
    Поддерживает групповой режим (group_id) для сквозной анонимизации.
    """
    if not payload.text.strip():
        return AnonymizeTextResponse(anonymized_text="", session_id="", group_id=payload.group_id, entities_found=0)
        
    entity_map = {}
    if payload.group_id:
        existing_group_map = get_group_entity_map(payload.group_id)
        if existing_group_map:
            entity_map.update(existing_group_map)

    anonymized = detector.analyze_and_anonymize(
        payload.text,
        entity_map=entity_map,
        lang=payload.lang,
        mode=payload.mode
    )
    
    session_id = create_session(entity_map, filename="text_input", user_token="default", lang=payload.lang, group_id=payload.group_id)
    
    return AnonymizeTextResponse(
        anonymized_text=anonymized,
        session_id=session_id,
        group_id=payload.group_id,
        entities_found=len(entity_map)
    )

@app.post("/api/deanonymize/text", response_model=DeanonymizeTextResponse, tags=["Text DLP"])
async def deanonymize_text(
    payload: DeanonymizeTextRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Восстанавливает оригинальные данные в замаскированном тексте.
    Поддерживает одиночный session_id, список через запятую или group_id.
    """
    entity_map = get_session_map(payload.session_id)
    if entity_map is None:
        raise HTTPException(status_code=404, detail="Сессия или Группа не найдена или истекла")
        
    restored = detector.deanonymize(payload.text, entity_map)
    
    return DeanonymizeTextResponse(
        restored_text=restored,
        session_id=payload.session_id
    )


# --- REST API: Работа с файлами ---

def process_single_file(filename: str, file_bytes: bytes, anonymize_func, deanonymize_func, entity_map: dict, is_deanonymize: bool = False, mode: str = "fake") -> bytes:
    """Универсальный диспетчер обработки всех поддерживаемых форматов документов (23+ формата + ZIP)."""
    fname = filename.lower()

    if not is_deanonymize:
        if fname.endswith(".docx"):
            return OfficeParser.anonymize_docx(file_bytes, anonymize_func)
        elif fname.endswith((".xlsx", ".xls")):
            return OfficeParser.anonymize_xlsx(file_bytes, anonymize_func, context_anonymize_func=anonymize_func)
        elif fname.endswith((".pptx", ".pptm", ".ppt")):
            return OfficeParser.anonymize_pptx(file_bytes, anonymize_func)
        elif fname.endswith((".odt", ".ods", ".odp", ".vsdx")):
            return OpenOfficeParser.anonymize_opendocument(file_bytes, anonymize_func)
        elif fname.endswith(".pdf"):
            return PdfParser.anonymize_pdf(file_bytes, anonymize_func, entity_map)
        elif fname.endswith((".txt", ".md", ".markdown")):
            return PlainParser.anonymize_txt(file_bytes, anonymize_func)
        elif fname.endswith(".csv"):
            return PlainParser.anonymize_csv(file_bytes, anonymize_func)
        elif fname.endswith(".tsv"):
            return PlainParser.anonymize_tsv(file_bytes, anonymize_func)
        elif fname.endswith(".json"):
            return PlainParser.anonymize_json(file_bytes, anonymize_func)
        elif fname.endswith((".xml", ".mxl")):
            return PlainParser.anonymize_xml(file_bytes, anonymize_func)
        elif fname.endswith((".html", ".htm")):
            return PlainParser.anonymize_html(file_bytes, anonymize_func)
        elif fname.endswith(".rtf"):
            return PlainParser.anonymize_rtf(file_bytes, anonymize_func)
        elif fname.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            from parsers.image import ImageParser
            return ImageParser.anonymize_image(file_bytes, anonymize_func, entity_map)
        elif fname.endswith((".zip", ".pbix")):
            def zip_file_processor(inner_fname, inner_bytes, is_deanonymize=False):
                return process_single_file(inner_fname, inner_bytes, anonymize_func, deanonymize_func, entity_map, is_deanonymize=is_deanonymize, mode=mode)
            return ArchiveParser.anonymize_zip(file_bytes, zip_file_processor)
        else:
            raise ValueError(f"Формат {filename.split('.')[-1]} не поддерживается")
    else:
        if fname.endswith(".docx"):
            return OfficeParser.deanonymize_docx(file_bytes, deanonymize_func)
        elif fname.endswith((".xlsx", ".xls")):
            return OfficeParser.deanonymize_xlsx(file_bytes, deanonymize_func)
        elif fname.endswith((".pptx", ".pptm", ".ppt")):
            return OfficeParser.deanonymize_pptx(file_bytes, deanonymize_func)
        elif fname.endswith((".odt", ".ods", ".odp", ".vsdx")):
            return OpenOfficeParser.deanonymize_opendocument(file_bytes, deanonymize_func)
        elif fname.endswith(".pdf"):
            return PdfParser.deanonymize_pdf(file_bytes, entity_map)
        elif fname.endswith((".txt", ".md", ".markdown")):
            return PlainParser.deanonymize_txt(file_bytes, deanonymize_func)
        elif fname.endswith(".csv"):
            return PlainParser.deanonymize_csv(file_bytes, deanonymize_func)
        elif fname.endswith(".tsv"):
            return PlainParser.deanonymize_tsv(file_bytes, deanonymize_func)
        elif fname.endswith(".json"):
            return PlainParser.deanonymize_json(file_bytes, deanonymize_func)
        elif fname.endswith((".xml", ".mxl")):
            return PlainParser.deanonymize_xml(file_bytes, deanonymize_func)
        elif fname.endswith((".html", ".htm")):
            return PlainParser.deanonymize_html(file_bytes, deanonymize_func)
        elif fname.endswith(".rtf"):
            return PlainParser.deanonymize_rtf(file_bytes, deanonymize_func)
        elif fname.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            from parsers.image import ImageParser
            return ImageParser.deanonymize_image(file_bytes, deanonymize_func)
        elif fname.endswith((".zip", ".pbix")):
            def zip_file_processor(inner_fname, inner_bytes, is_deanonymize=True):
                return process_single_file(inner_fname, inner_bytes, anonymize_func, deanonymize_func, entity_map, is_deanonymize=is_deanonymize, mode=mode)
            return ArchiveParser.deanonymize_zip(file_bytes, zip_file_processor)
        else:
            raise ValueError(f"Формат {filename.split('.')[-1]} не поддерживается")


# --- REST API: Работа с файлами ---

@app.post("/api/anonymize/file", tags=["File DLP"])
async def anonymize_file(
    file: UploadFile = File(...),
    mode: str = Form("fake"),
    group_id: str | None = Form(None),
    api_key: str = Depends(verify_api_key)
):
    """
    Загружает и анонимизирует документ любого поддерживаемого формата (17 форматов + ZIP).
    Возвращает защищенный файл с заголовками X-Session-ID и X-Group-ID.
    """
    file_bytes = await file.read()
    entity_map = {}
    
    if group_id:
        existing_group_map = get_group_entity_map(group_id)
        if existing_group_map:
            entity_map.update(existing_group_map)
    
    def anonymize_func(text: str) -> str:
        return detector.analyze_and_anonymize(text, entity_map, "auto", mode=mode)

    def deanonymize_func(text: str) -> str:
        return detector.deanonymize(text, entity_map)
        
    try:
        anonymized_bytes = process_single_file(
            file.filename, file_bytes, anonymize_func, deanonymize_func, entity_map, is_deanonymize=False, mode=mode
        )
            
        session_id = create_session(entity_map, file.filename, "default", "auto", group_id=group_id)
        encoded_filename = urllib.parse.quote(f"safe_{file.filename}")
        
        headers = {
            "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}",
            "X-Session-ID": session_id
        }
        if group_id:
            headers["X-Group-ID"] = group_id

        return Response(
            content=anonymized_bytes,
            media_type="application/octet-stream",
            headers=headers
        )
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Ошибка обработки файла: {str(e)}"})

@app.post("/api/deanonymize/file", tags=["File DLP"])
async def deanonymize_file(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Восстанавливает оригинальный документ по защищенному файлу и ID сессии.
    """
    entity_map = get_session_map(session_id)
    if entity_map is None:
        return JSONResponse(status_code=404, content={"error": "Сессия не найдена или истекла"})
        
    file_bytes = await file.read()
    
    def anonymize_func(text: str) -> str:
        return text

    def deanonymize_func(text: str) -> str:
        return detector.deanonymize(text, entity_map)
        
    try:
        deanonymized_bytes = process_single_file(
            file.filename, file_bytes, anonymize_func, deanonymize_func, entity_map, is_deanonymize=True
        )
            
        encoded_filename = urllib.parse.quote(f"restored_{file.filename}")
        return Response(
            content=deanonymized_bytes,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
            }
        )
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Ошибка восстановления файла: {str(e)}"})

@app.get("/api/sessions", tags=["Sessions"])
async def get_sessions(api_key: str = Depends(verify_api_key)):
    """Возвращает историю активных сессий анонимизации"""
    sessions = get_user_sessions("default")
    return JSONResponse(content={"sessions": sessions})



if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
    
if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
