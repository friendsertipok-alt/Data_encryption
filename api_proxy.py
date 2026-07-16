import httpx
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
import json
import uuid

from core.dependencies import detector
from session_store import create_session, get_session_map
from audit_logger import log_audit_event
from config import UPSTREAM_URL

proxy_router = APIRouter()

def _recursive_mask(data, entity_map, lang):
    """Рекурсивно обходит JSON и маскирует все строковые значения"""
    if isinstance(data, dict):
        return {k: _recursive_mask(v, entity_map, lang) for k, v in data.items()}
    elif isinstance(data, list):
        return [_recursive_mask(v, entity_map, lang) for v in data]
    elif isinstance(data, str):
        return detector.analyze_and_anonymize(data, entity_map, lang=lang)
    return data

def _recursive_unmask(data, entity_map):
    """Рекурсивно обходит JSON и восстанавливает все строковые значения"""
    if isinstance(data, dict):
        return {k: _recursive_unmask(v, entity_map) for k, v in data.items()}
    elif isinstance(data, list):
        return [_recursive_unmask(v, entity_map) for v in data]
    elif isinstance(data, str):
        return detector.deanonymize(data, entity_map)
    return data

@proxy_router.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    """
    OpenAI-совместимый прокси.
    Перехватывает запрос, маскирует PII, отправляет в LLM, и деанонимизирует ответ.
    """
    body = await request.json()
    
    # 1. Если передали заголовок сессии, используем его, иначе создаем новый маппинг
    session_id = request.headers.get("X-Session-ID")
    if session_id:
        entity_map = get_session_map(session_id) or {}
    else:
        entity_map = {}
        session_id = str(uuid.uuid4())
        
    lang = request.headers.get("X-DLP-Lang", "ru")

    original_body = dict(body)

    # 2. Маскируем сообщения
    if "messages" in body:
        body["messages"] = _recursive_mask(body["messages"], entity_map, lang)
        
        # Сохраняем маппинг для будущего (если клиент захочет переиспользовать сессию)
        create_session(entity_map, filename="api_proxy", user_token="default", lang=lang)

        # Логируем событие в аудит
        log_audit_event(
            user_token=request.headers.get("Authorization", "no_token"),
            original_text=json.dumps(original_body, ensure_ascii=False),
            anonymized_text=json.dumps(body, ensure_ascii=False),
            entity_map=entity_map
        )

    # 3. Пересылка запроса (Upstream)
    auth_header = request.headers.get("Authorization")
    headers = {"Content-Type": "application/json"}
    if auth_header:
        headers["Authorization"] = auth_header

    # Если Streaming включен
    is_stream = body.get("stream", False)

    try:
        async with httpx.AsyncClient() as client:
            if is_stream:
                # В прототипе стриминг с деанонимизацией на лету сложен, т.к. токены могут быть разорваны.
                # Пока возвращаем ошибку или выключаем стриминг.
                return JSONResponse(status_code=400, content={"error": "Streaming пока не поддерживается DLP-Шлюзом"})
            else:
                response = await client.post(UPSTREAM_URL, json=body, headers=headers, timeout=60.0)
                
                # Если LLM вернула ошибку (например, неверный токен)
                if response.status_code != 200:
                    return JSONResponse(status_code=response.status_code, content=response.json())
                    
                resp_data = response.json()
                
                # 4. Деанонимизация ответа LLM
                if "choices" in resp_data:
                    for choice in resp_data["choices"]:
                        if "message" in choice and "content" in choice["message"]:
                            safe_content = choice["message"]["content"]
                            original_content = detector.deanonymize(safe_content, entity_map)
                            choice["message"]["content"] = original_content
                            
                headers_out = dict(response.headers)
                headers_out.pop("content-length", None)
                headers_out.pop("content-encoding", None)
                headers_out["X-Session-ID"] = session_id
                
                return JSONResponse(content=resp_data, headers={"X-Session-ID": session_id})
                
    except httpx.RequestError as e:
        return JSONResponse(status_code=502, content={"error": f"Ошибка связи с LLM: {str(e)}"})
