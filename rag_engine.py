from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

import os

# Инициализируем клиент Qdrant с сохранением на диск.
DB_PATH = os.path.join(os.path.dirname(__file__), "qdrant_db")
client = QdrantClient(path=DB_PATH)

COLLECTION_NAME = "company_documents"

def setup_collection():
    """
    Создает коллекцию для хранения документов.
    Мы используем встроенный в Qdrant Client движок FastEmbed.
    Он автоматически, локально и очень быстро превращает текст в векторы (тот самый "двоичный код").
    """
    # Используем небольшую многоязычную модель (поддерживает русский)
    client.set_model("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    # Подключаем точный лексический поиск (BM25)
    client.set_sparse_model("Qdrant/bm25")
    
    if not client.collection_exists(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=client.get_fastembed_vector_params(),
            sparse_vectors_config=client.get_fastembed_sparse_vector_params()
        )
        print(f"[RAG Engine] Коллекция '{COLLECTION_NAME}' готова к работе.")

def add_document(text: str, doc_name: str, allowed_roles: list[str] = None):
    """
    Добавляет текст в векторную базу данных с указанием ролей доступа.
    Если roles не указан, документ считается публичным (доступен всем).
    """
    if allowed_roles is None:
        allowed_roles = ["all"]
        
    client.add(
        collection_name=COLLECTION_NAME,
        documents=[text],
        metadata=[{
            "doc_name": doc_name, 
            "original_text": text, 
            "allowed_roles": allowed_roles
        }]
    )
    print(f"[RAG Engine] Загружен документ: {doc_name} (Доступ: {allowed_roles})")

def search_similar_text(query: str, user_role: str = None, limit: int = 15) -> list[str]:
    """
    ВРЕМЕННО ОТКЛЮЧЕНО: Ищет куски текста в базе, фильтруя их по роли пользователя (RBAC).
    """
    return []
    
    query_filter = None
    if user_role:
        # Разрешаем доступ, если роль пользователя есть в списке разрешенных ИЛИ документ публичный ("all")
        query_filter = Filter(
            should=[
                FieldCondition(key="allowed_roles", match=MatchValue(value=user_role)),
                FieldCondition(key="allowed_roles", match=MatchValue(value="all"))
            ]
        )

    search_results = client.query(
        collection_name=COLLECTION_NAME,
        query_text=query,
        query_filter=query_filter,
        limit=limit
    )
    
    found_texts = []
    for hit in search_results:
        found_texts.append(hit.metadata.get("original_text", ""))
        
    return found_texts

# Вызываем настройку при импорте модуля (ВРЕМЕННО ОТКЛЮЧЕНО)
# setup_collection()

# --- ТЕСТОВЫЕ ДАННЫЕ ---
# Сразу загрузим в базу пару "секретных" тестовых документов, чтобы было на чем проверять
if __name__ == "__main__":
    print("\n--- Инициализация тестовой базы ---")
    
    # Документ только для менеджмента
    add_document(
        "Трудовой договор №45. Работник: Тестов Тест Тестович. Паспорт: 1234 567890. Оклад: 500 000 рублей. Должность: Разработчик.",
        "Договор_Тестова.txt",
        allowed_roles=["management", "hr"]
    )
    
    # Документ только для финансистов и руководства
    add_document(
        "Отчет о закупках ООО 'Пример' за 2025 год. Ответственный менеджер: Примерный Пример Примерович. Общая сумма закупок оборудования: 15 000 000 рублей.",
        "Отчет_Пример.txt",
        allowed_roles=["finance", "management"]
    )
    
    # Публичный документ (доступен всем отделам)
    add_document(
        "Регламент отпусков компании. Каждый сотрудник имеет право на 28 дней отпуска. Заявления подаются за 2 недели.",
        "Регламент_отпусков.txt",
        allowed_roles=["all"]
    )
    print("-----------------------------------\n")
