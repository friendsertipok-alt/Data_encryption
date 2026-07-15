"""
Скрипт для тестирования работы прокси-сервера.
Имитирует отправку сообщения пользователем из интерфейса (например, Open-WebUI).
"""
import httpx
import asyncio
import json

PROXY_URL = "http://localhost:8001/v1/chat/completions"

# Токен пользователя (определяет его отдел и системный промпт)
# Возможные варианты: token-user-1 (Юристы), token-user-2 (Финансы), и т.д.
USER_TOKEN = "token-user-1" 

async def main():
    # Сообщение, в котором есть ФИО (Тестов Тест Тестович) и запрос по документу
    user_message = "Посмотри в базе, какой оклад у сотрудника Тестов Тест Тестович и кем он работает?"
    
    payload = {
        "model": "claude-3-5-sonnet", # Это значение игнорируется нашим прокси, он сам решает, куда слать
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {USER_TOKEN}"
    }
    
    print(f"👤 Отправляем запрос от имени '{USER_TOKEN}'...")
    print(f"📝 Сообщение: {user_message}\n")
    print("⏳ Ожидание ответа от прокси (это может занять несколько секунд)...\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(PROXY_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                print("✅ ОТВЕТ ОТ НЕЙРОСЕТИ (уже деанонимизированный):")
                print("=" * 60)
                print(reply)
                print("=" * 60)
            else:
                print(f"❌ Ошибка от сервера: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    asyncio.run(main())
