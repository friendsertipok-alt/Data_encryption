import os
import urllib.parse
from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.dependencies import detector
from session_store import create_session, get_session_map, get_user_sessions
from parsers.office import OfficeParser
from parsers.plain import PlainParser
from parsers.pdf import PdfParser
from api_proxy import proxy_router

app = FastAPI(title="Universal DLP Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API Proxy
app.include_router(proxy_router)

@app.post("/api/anonymize/file")
async def anonymize_file(
    file: UploadFile = File(...)
):
    filename = file.filename.lower()
    file_bytes = await file.read()
    
    entity_map = {}
    anonymized_bytes = b""
    
    # Замыкание для передачи в парсеры (используем auto)
    def anonymize_func(text: str) -> str:
        return detector.analyze_and_anonymize(text, entity_map, "auto")
        
    try:
        if filename.endswith(".docx"):
            anonymized_bytes = OfficeParser.anonymize_docx(file_bytes, anonymize_func)
        elif filename.endswith(".xlsx"):
            anonymized_bytes = OfficeParser.anonymize_xlsx(file_bytes, anonymize_func, context_anonymize_func=anonymize_func)
        elif filename.endswith(".pptx"):
            anonymized_bytes = OfficeParser.anonymize_pptx(file_bytes, anonymize_func)
        elif filename.endswith(".pdf"):
            anonymized_bytes = PdfParser.anonymize_pdf(file_bytes, anonymize_func, entity_map)
        elif filename.endswith(".txt"):
            anonymized_bytes = PlainParser.anonymize_txt(file_bytes, anonymize_func)
        elif filename.endswith(".csv"):
            anonymized_bytes = PlainParser.anonymize_csv(file_bytes, anonymize_func)
        elif filename.endswith(".json"):
            anonymized_bytes = PlainParser.anonymize_json(file_bytes, anonymize_func)
        elif filename.endswith(".xml"):
            anonymized_bytes = PlainParser.anonymize_xml(file_bytes, anonymize_func)
        else:
            return JSONResponse(status_code=400, content={"error": f"Формат {filename.split('.')[-1]} пока не поддерживается"})
            
        session_id = create_session(entity_map, file.filename, "default", "auto")
        encoded_filename = urllib.parse.quote(f"safe_{file.filename}")
        
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


@app.post("/api/deanonymize/file")
async def deanonymize_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    entity_map = get_session_map(session_id)
    if entity_map is None:
        return JSONResponse(status_code=404, content={"error": "Сессия не найдена"})
        
    filename = file.filename.lower()
    file_bytes = await file.read()
    deanonymized_bytes = b""
    
    def deanonymize_func(text: str) -> str:
        return detector.deanonymize(text, entity_map)
        
    try:
        if filename.endswith(".docx"):
            deanonymized_bytes = OfficeParser.deanonymize_docx(file_bytes, deanonymize_func)
        elif filename.endswith(".xlsx"):
            deanonymized_bytes = OfficeParser.deanonymize_xlsx(file_bytes, deanonymize_func)
        elif filename.endswith(".pptx"):
            deanonymized_bytes = OfficeParser.deanonymize_pptx(file_bytes, deanonymize_func)
        elif filename.endswith(".pdf"):
            deanonymized_bytes = PdfParser.deanonymize_pdf(file_bytes, entity_map)
        elif filename.endswith(".txt"):
            deanonymized_bytes = PlainParser.deanonymize_txt(file_bytes, deanonymize_func)
        elif filename.endswith(".csv"):
            deanonymized_bytes = PlainParser.deanonymize_csv(file_bytes, deanonymize_func)
        elif filename.endswith(".json"):
            deanonymized_bytes = PlainParser.deanonymize_json(file_bytes, deanonymize_func)
        elif filename.endswith(".xml"):
            deanonymized_bytes = PlainParser.deanonymize_xml(file_bytes, deanonymize_func)
        else:
            return JSONResponse(status_code=400, content={"error": "Формат не поддерживается"})
            
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

@app.get("/api/sessions")
async def get_sessions():
    sessions = get_user_sessions("default")
    return JSONResponse(content={"sessions": sessions})

if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
