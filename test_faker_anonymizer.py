import sys
import os

# Добавляем путь к нашему проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anonymizer import DlpSession

test_cases = [
    # 1. Один человек упоминается несколько раз (проверка консистентности)
    "Сотрудник Иванов Иван Иванович запросил отпуск. Прошу согласовать отпуск для Иванова Ивана Ивановича. Также Иванов И.И. просил передать документы.",
    
    # 2. Несколько разных людей и email-ов
    "Директор Петров Алексей Сергеевич (petrov@company.ru) назначил встречу с менеджером Смирновой Анной Викторовной (smirnova@company.ru).",
    
    # 3. Сложный корпоративный текст с компаниями и деньгами
    "Согласно контракту №88-ПР, компания ООО 'Рога и Копыта' обязуется перевести ПАО 'Сбербанк' сумму 5 000 000 рублей. Контактное лицо: Сидоров В.В., телефон: +7 999 123-45-67.",
    
    # 4. Текст с английскими вставками и URL
    "Please send the report to ceo@startup.com. Our website is https://startup.com/admin. С уважением, генеральный директор John Doe.",
    
    # 5. Длинный запутанный текст
    "Вчера на совещании присутствовали: 1) Козлов Дмитрий (hr@hr-dept.ru) 2) Волкова Елена (finance@money.ru). ООО 'ТехноЛайн' задерживает поставку. Звонить по номеру 8 (800) 555-35-35."
]

def run_tests():
    print("=" * 80)
    print("🚀 СУПЕР-ТЕСТ FAKER АНОНИМИЗАТОРА")
    print("=" * 80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{'=' * 40}")
        print(f"🔹 ТЕСТ #{i}")
        print(f"{'=' * 40}")
        
        # Новая сессия для каждого текста (имитация нового запроса)
        session = DlpSession()
        
        # 1. Анонимизация
        anonymized = session.custom_anonymize(text)
        
        print(f"📄 ОРИГИНАЛ:\n   {text}\n")
        print(f"🔒 МАСКИРОВКА (улетит в Claude):\n   {anonymized}\n")
        
        print(f"🗺️  СЛОВАРЬ ЗАМЕН (в памяти):")
        for fake_val, real_val in session.entity_map.items():
            print(f"   {fake_val} -> {real_val}")
            
        # 2. Имитация ответа нейросети (представим, что Claude вернул тот же текст, но добавил от себя слова)
        fake_claude_response = f"Анализ текста: {anonymized}. Вывод: данные обработаны."
        
        # 3. Деанонимизация
        restored = session.deanonymize(fake_claude_response)
        
        print(f"\n✅ ВОССТАНОВЛЕНО (увидит пользователь):\n   {restored}\n")
        
        # Базовая проверка
        # Проверяем, что в восстановленном тексте нет фейковых ключей
        success = True
        for fake_val in session.entity_map.keys():
            if fake_val in restored:
                success = False
                print(f"❌ ОШИБКА: Фейковое значение '{fake_val}' не было заменено обратно!")
                
        if success:
            print("🟢 ТЕСТ ПРОЙДЕН УСПЕШНО")

if __name__ == "__main__":
    run_tests()
