from typing import Dict, Optional
from faker import Faker
import pymorphy3
import random

class FakerEngine:
    """
    Движок для генерации реалистичных фейков.
    Поддерживает падежи для русских имён (PyMorphy3).
    """
    def __init__(self):
        self.fake_ru = Faker('ru_RU')
        self.fake_in = Faker('en_IN')
        self.morph = pymorphy3.MorphAnalyzer()
        
    def generate_fake(self, entity_type: str, original_value: str) -> str:
        """
        Генерирует фейковое значение для заданного типа сущности.
        Если тип неизвестен, возвращает формат [ТИП_random].
        """
        # --- Россия ---
        if entity_type == "PERSON":
            return self.fake_ru.name()
        elif entity_type == "PHONE_RU":
            return self.fake_ru.phone_number()
        elif entity_type == "INN_RU":
            if len(original_value) == 10:
                return str(self.fake_ru.random_number(digits=10, fix_len=True))
            return str(self.fake_ru.random_number(digits=12, fix_len=True))
        elif entity_type == "SNILS_RU":
            # 123-456-789 12
            parts = [str(self.fake_ru.random_number(digits=3, fix_len=True)) for _ in range(3)]
            check = str(self.fake_ru.random_number(digits=2, fix_len=True))
            return f"{parts[0]}-{parts[1]}-{parts[2]} {check}"
        elif entity_type == "PASSPORT_RU":
            parts = re.split(r'[-\s]', original_value)
            if len(parts) >= 2:
                # Серия и номер с сохранением формата
                return f"{self.fake_ru.random_number(digits=4, fix_len=True)} {self.fake_ru.random_number(digits=6, fix_len=True)}"
            return str(self.fake_ru.random_number(digits=10, fix_len=True))
        elif entity_type == "BANK_ACCOUNT_RU":
            return "4" + str(self.fake_ru.random_number(digits=19, fix_len=True))
        elif entity_type == "CREDIT_CARD":
            return self.fake_ru.credit_card_number()
        
        # --- ТРАНСПОРТ (РФ) ---
        elif entity_type.startswith("VEHICLE_"):
            # Генерируем случайный номер, сохраняя оригинальную структуру
            fake_val = ""
            chars_ru = 'АВЕКМНОРСТУХ'
            for c in original_value:
                if c.isdigit():
                    fake_val += str(random.randint(0, 9))
                elif c.upper() in chars_ru or c.upper() in 'A-Z':
                    fake_val += random.choice(chars_ru)
                else:
                    fake_val += c
            return fake_val
            
        elif entity_type == "VIN":
            chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
            return ''.join(random.choice(chars) for _ in range(17))

        # --- Индия ---
        elif entity_type == "AADHAAR_IN":
            return f"{self.fake_in.random_number(digits=4, fix_len=True)} {self.fake_in.random_number(digits=4, fix_len=True)} {self.fake_in.random_number(digits=4, fix_len=True)}"
        elif entity_type == "PAN_IN":
            letters = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(5))
            digits = str(self.fake_in.random_number(digits=4, fix_len=True))
            last_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            return f"{letters}{digits}{last_letter}"
        elif entity_type == "VOTER_ID_IN":
            letters = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3))
            digits = str(self.fake_in.random_number(digits=7, fix_len=True))
            return f"{letters}{digits}"
        elif entity_type == "PHONE_IN":
            return f"+91 {self.fake_in.random_number(digits=10, fix_len=True)}"
        
        # --- Общее ---
        elif entity_type == "EMAIL_ADDRESS":
            return self.fake_ru.email()
        elif entity_type == "RU_ORGANIZATION":
            return self.fake_ru.company()
            
        return f"[{entity_type}_{random.randint(1000, 9999)}]"

    def morph_russian_name(self, original_words: list, fake_words: list, case: str) -> tuple:
        """
        Склоняет оригинальное и фейковое имя в нужный падеж.
        """
        inf_orig_words = []
        for w in original_words:
            p = self.morph.parse(w)[0]
            inf = p.inflect({case})
            inf_res = inf.word if inf else w
            if w.istitle(): inf_res = inf_res.capitalize()
            inf_orig_words.append(inf_res)
            
        inf_fake_words = []
        for w in fake_words:
            p = self.morph.parse(w)[0]
            inf = p.inflect({case})
            inf_res = inf.word if inf else w
            if w.istitle(): inf_res = inf_res.capitalize()
            inf_fake_words.append(inf_res)
            
        return " ".join(inf_orig_words), " ".join(inf_fake_words), inf_orig_words, inf_fake_words
