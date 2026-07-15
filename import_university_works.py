import os
import subprocess
from rag_engine import add_document

WORK_DIRS = [
    os.path.expanduser("~/Desktop/Работы"),
    os.path.expanduser("~/Desktop/курсачи и дтз"),
    os.path.expanduser("~/Desktop/Работа РГ менеджмент")
]

def extract_text_from_docx(filepath):
    try:
        # Конвертация docx в текст через встроенную утилиту macOS textutil
        result = subprocess.run(['textutil', '-convert', 'txt', '-stdout', filepath], 
                                capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        print(f"Ошибка чтения {filepath}: {e}")
        return ""

def load_files():
    print(f"Начинаю сканирование папок: {WORK_DIRS}")
    count = 0
    for work_dir in WORK_DIRS:
        if not os.path.exists(work_dir):
            continue
        for root, dirs, files in os.walk(work_dir):
            for f in files:
                if f.startswith("~") or f.startswith("."): 
                    continue # пропускаем временные файлы Word
                    
                filepath = os.path.join(root, f)
                
                text = ""
                if f.endswith(".docx"):
                    text = extract_text_from_docx(filepath)
                elif f.endswith(".txt"):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            text = file.read()
                    except Exception:
                        pass
                        
                if text.strip():
                    # Разбиваем на параграфы
                    chunks = [chunk.strip() for chunk in text.split("\n") if len(chunk.strip()) > 100]
                    
                    # Загрузим все абзацы
                    added_chunks = 0
                    for i, chunk in enumerate(chunks):
                        add_document(
                            text=chunk[:1500], # Ограничиваем длину куска
                            doc_name=f"{f} [Часть {added_chunks+1}]",
                            allowed_roles=["all"] # Публичный доступ (чтобы работало для всех ролей)
                        )
                        added_chunks += 1
                        
                    print(f"Загружен файл: {f} ({added_chunks} фрагментов)")
                    count += 1
                    
    print(f"\nЗагрузка завершена. Обработано файлов: {count}")

if __name__ == "__main__":
    load_files()
