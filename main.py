import os
import httpx
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from anonymizer import DlpSession
from user_profiles import get_all_data, save_all_data, is_dlp_enabled
from audit_logger import log_audit_event
from session_store import create_session, get_session_map, get_user_sessions
from file_parsers import anonymize_docx, deanonymize_docx, anonymize_xlsx, deanonymize_xlsx, anonymize_pptx, deanonymize_pptx
import urllib.parse

app = FastAPI(title="DLP Anonymizer App")

# Разрешаем CORS для локальной разработки (Admin Panel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ЭНДПОИНТЫ ADMIN API — управление из панели администратора
# ============================================================

@app.get("/admin/api/data")
async def admin_get_data():
    """Отдает все данные (пользователи, промпты, настройки) для панели."""
    return get_all_data()

@app.post("/admin/api/data")
async def admin_save_data(request: Request):
    """Сохраняет все данные из панели администратора."""
    data = await request.json()
    save_all_data(data)
    return {"status": "ok", "message": "Данные сохранены"}

# ============================================================
# ОСНОВНЫЕ ЭНДПОИНТЫ ДЛЯ РАБОТЫ С ФАЙЛАМИ
# ============================================================

@app.post("/api/anonymize/file")
async def anonymize_file(
    file: UploadFile = File(...),
    user_token: str = Form("default")
):
    if not is_dlp_enabled():
        return JSONResponse(status_code=400, content={"error": "DLP отключен в настройках"})
        
    filename = file.filename.lower()
    file_bytes = await file.read()
    
    session = DlpSession()
    anonymized_bytes = b""
    
    try:
        if filename.endswith(".docx"):
            anonymized_bytes = anonymize_docx(file_bytes, session.custom_anonymize)
        elif filename.endswith(".xlsx"):
            anonymized_bytes = anonymize_xlsx(
                file_bytes, 
                anonymize_func=session.custom_anonymize,
                context_anonymize_func=session.anonymize_context_number
            )
        elif filename.endswith(".pptx"):
            anonymized_bytes = anonymize_pptx(file_bytes, session.custom_anonymize)
        else:
            return JSONResponse(status_code=400, content={"error": "Поддерживаются только форматы .docx, .xlsx и .pptx"})
            
        # Сохраняем сессию с именем файла
        session_id = create_session(session.entity_map, file.filename, user_token)
        
        # Кодируем имя файла для безопасной передачи в заголовке
        encoded_filename = urllib.parse.quote(f"anonymized_{file.filename}")
        
        # Возвращаем файл и session_id в заголовках
        return Response(
            content=anonymized_bytes,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}",
                "X-Session-ID": session_id
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Ошибка обработки: {str(e)}"})

@app.get("/api/sessions")
async def get_sessions(user_token: str = "default"):
    """Возвращает историю сессий (файлов) пользователя"""
    sessions = get_user_sessions(user_token)
    return JSONResponse(content={"sessions": sessions})

@app.post("/api/deanonymize/file")
async def deanonymize_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    entity_map = get_session_map(session_id)
    if entity_map is None:
        return JSONResponse(status_code=404, content={"error": "Сессия не найдена. Возможно она устарела."})
        
    session = DlpSession()
    session.entity_map = entity_map
    
    filename = file.filename.lower()
    file_bytes = await file.read()
    deanonymized_bytes = b""
    
    try:
        if filename.endswith(".docx"):
            deanonymized_bytes = deanonymize_docx(file_bytes, session.deanonymize)
        elif filename.endswith(".xlsx"):
            deanonymized_bytes = deanonymize_xlsx(file_bytes, session.deanonymize)
        elif filename.endswith(".pptx"):
            deanonymized_bytes = deanonymize_pptx(file_bytes, session.deanonymize)
        else:
            return JSONResponse(status_code=400, content={"error": "Поддерживаются только форматы .docx, .xlsx и .pptx"})
            
        # Кодируем имя файла для безопасной передачи в заголовке
        encoded_filename = urllib.parse.quote(f"restored_{file.filename}")
            
        return Response(
            content=deanonymized_bytes,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Ошибка обработки: {str(e)}"})

# Подключаем статические файлы для Frontend интерфейса
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
