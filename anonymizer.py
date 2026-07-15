import re
from typing import Dict, List, Tuple
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
import pymorphy3

from presidio_analyzer import EntityRecognizer, RecognizerResult
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsNERTagger,
    NamesExtractor,
    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)
names_extractor = NamesExtractor(morph_vocab)

class NatashaPersonRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["PERSON"], supported_language="ru")

    def load(self) -> None:
        pass

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        doc = Doc(text)
        doc.segment(segmenter)
        doc.tag_ner(ner_tagger)
        for span in doc.spans:
            if span.type == 'PER':
                results.append(RecognizerResult(
                    entity_type="PERSON",
                    start=span.start,
                    end=span.stop,
                    score=0.95
                ))
        return results


# Инициализируем Faker и NLP Морфологию
fake = Faker('ru_RU')
morph = pymorphy3.MorphAnalyzer()

# Настройка NLP движка для русского языка через spaCy
nlp_configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ru", "model_name": "ru_core_news_md"}],
}

provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
nlp_engine = provider.create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ru"])

# =============================================
# КАСТОМНЫЙ ДЕТЕКТОР: Российские юридические лица
# Ищет паттерны вроде: ООО "Ромашка", ЗАО «Рога и копыта», ПАО 'Газпром'
# =============================================
ru_org_patterns = [
    Pattern(
        name="ru_org_quotes",
        regex=r"""(?:ООО|ОАО|ЗАО|ПАО|АО|НКО|ИП)\s*[«"'\u2018\u201c]([^»"'\u2019\u201d]+)[»"'\u2019\u201d]""",
        score=0.95,
    ),
    Pattern(
        name="ru_org_no_quotes",
        regex=r"""(?:ООО|ОАО|ЗАО|ПАО|АО|НКО|ИП)\s+(?:[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁа-яё]+)*)""",
        score=0.7,
    ),
]

ru_org_recognizer = PatternRecognizer(
    supported_entity="RU_ORGANIZATION",
    supported_language="ru",
    patterns=ru_org_patterns,
    name="RussianOrgRecognizer",
)

# =============================================
# КАСТОМНЫЙ ДЕТЕКТОР: Российские телефоны (+7...)
# Presidio по умолчанию плохо ловит +7 в русском контексте.
# Добавляем свой детектор с высокой уверенностью.
# =============================================
ru_phone_patterns = [
    Pattern(
        name="ru_phone_7",
        regex=r"\+7\s*[\(\-]?\d{3}[\)\-]?\s*\d{3}[\-\s]?\d{2}[\-\s]?\d{2}",
        score=0.9,
    ),
    Pattern(
        name="ru_phone_8",
        regex=r"\b8\s*[\(\-]?\d{3}[\)\-]?\s*\d{3}[\-\s]?\d{2}[\-\s]?\d{2}\b",
        score=0.85,
    ),
]

ru_phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    supported_language="ru",
    patterns=ru_phone_patterns,
    name="RussianPhoneRecognizer",
)

# =============================================
# КАСТОМНЫЙ ДЕТЕКТОР: Российские реквизиты, документы и ПДн
# =============================================
ru_financial_patterns = [
    Pattern(name="ru_bank_account", regex=r"\b\d{20}\b", score=0.9), # Расчетный / корр счет
    Pattern(name="ru_ogrn", regex=r"\b\d{13}\b|\b\d{15}\b", score=0.9), # ОГРН, ОГРНИП
    Pattern(name="ru_inn_kpp_bik", regex=r"\b\d{9}\b|\b\d{10}\b|\b\d{12}\b", score=0.9), # ИНН, КПП, БИК
    Pattern(name="ru_okpo", regex=r"\b\d{8}\b|\b\d{11}\b", score=0.8), # ОКПО и прочие
    Pattern(name="ru_oms", regex=r"\b\d{16}\b", score=0.9), # Полис ОМС
    Pattern(name="ru_passport", regex=r"\b\d{2}\s?\d{2}\s?\d{6}\b|\b\d{4}\s?\d{6}\b", score=0.9), # Паспорт РФ
    Pattern(name="ru_snils", regex=r"\b\d{3}-\d{3}-\d{3}\s\d{2}\b", score=0.95), # СНИЛС
    Pattern(name="ru_license_plate", regex=r"\b[АВЕКМНОРСТУХABCEHKMOPTX]\d{3}[АВЕКМНОРСТУХABCEHKMOPTX]{2}\d{2,3}\b", score=0.9), # Номера авто
]

ru_financial_recognizer = PatternRecognizer(
    supported_entity="RU_FINANCIAL",
    supported_language="ru",
    patterns=ru_financial_patterns,
    name="RussianFinancialRecognizer",
)

# Регистрируем все детекторы
analyzer.registry.add_recognizer(ru_org_recognizer)
analyzer.registry.add_recognizer(ru_phone_recognizer)
analyzer.registry.add_recognizer(ru_financial_recognizer)
analyzer.registry.add_recognizer(NatashaPersonRecognizer())

# Убираем дефолтный spaCy распознаватель PERSON
for rec in analyzer.registry.get_recognizers(language="ru", entities=["PERSON"]):
    if rec.name == "SpacyRecognizer" and "PERSON" in rec.supported_entities:
        rec.supported_entities.remove("PERSON")


anonymizer_engine = AnonymizerEngine()

# Минимальный порог уверенности.
# Все срабатывания с уверенностью ниже этого порога будут отброшены.
# Это убирает ложные срабатывания (например, "350 000" → телефон).
MIN_SCORE_THRESHOLD = 0.5

# Список типов сущностей, которые мы ищем
ENTITIES_TO_DETECT = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "IBAN_CODE",
    "RU_ORGANIZATION",  # Наш кастомный детектор
    "RU_FINANCIAL",     # Реквизиты (ИНН, счета и тд)
]


class DlpSession:
    """Класс для хранения состояния анонимизации одного запроса"""
    def __init__(self):
        self.entity_map: Dict[str, str] = {}
        self.base_fake_map: Dict[str, str] = {} # Нормализованный оригинал -> Нормализованный фейк
        self.counter: Dict[str, int] = {}

    def custom_anonymize(self, text: str) -> str:
        """Анонимизирует текст, сохраняя оригинальные значения в entity_map."""
        results = analyzer.analyze(
            text=text,
            entities=ENTITIES_TO_DETECT,
            language='ru',
            score_threshold=MIN_SCORE_THRESHOLD,  # Отсекаем ложные срабатывания
        )
        
        # Убираем пересекающиеся сущности (оставляем те, что длиннее)
        filtered_results = []
        # Сортируем: сначала длинные
        sorted_by_length = sorted(results, key=lambda x: (x.end - x.start), reverse=True)
        for res in sorted_by_length:
            overlap = False
            for f_res in filtered_results:
                if max(res.start, f_res.start) < min(res.end, f_res.end):
                    overlap = True
                    break
            if not overlap:
                filtered_results.append(res)
                
        # Сортируем с конца, чтобы замены не сдвигали индексы
        filtered_results.sort(key=lambda x: x.start, reverse=True)
        
        anonymized_text = text
        for res in filtered_results:
            original_value = text[res.start:res.end]
            entity_type = res.entity_type
            
            # Если мы уже встречали это значение в этом сеансе, используем тот же токен
            token = None
            for existing_token, val in self.entity_map.items():
                if val == original_value:
                    token = existing_token
                    break
            
            if not token:
                # Генерируем реалистичный фейк в зависимости от типа сущности
                if entity_type == "PERSON":
                    original_words = original_value.split()
                    
                    # 1. Приводим оригинал к начальной форме (Именительный падеж)
                    base_orig_words = []
                    for w in original_words:
                        p = morph.parse(w)[0]
                        inf = p.inflect({'nomn'})
                        inf_res = inf.word if inf else w
                        if w.istitle(): inf_res = inf_res.capitalize()
                        base_orig_words.append(inf_res)
                    base_orig = " ".join(base_orig_words)
                    
                    # 2. Получаем или генерируем фейк для этой персоны
                    if base_orig not in self.base_fake_map:
                        self.base_fake_map[base_orig] = fake.name()
                    
                    fake_base = self.base_fake_map[base_orig]
                    fake_words = fake_base.split()
                    
                    # 3. Генерируем все 6 падежей и записываем в словарь замен
                    cases = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']
                    matched_fake_token = None
                    
                    for case in cases:
                        inf_orig_words = []
                        for w in original_words:
                            p = morph.parse(w)[0]
                            inf = p.inflect({case})
                            inf_res = inf.word if inf else w
                            if w.istitle(): inf_res = inf_res.capitalize()
                            inf_orig_words.append(inf_res)
                        inf_orig = " ".join(inf_orig_words)
                        
                        inf_fake_words = []
                        for w in fake_words:
                            p = morph.parse(w)[0]
                            inf = p.inflect({case})
                            inf_res = inf.word if inf else w
                            if w.istitle(): inf_res = inf_res.capitalize()
                            inf_fake_words.append(inf_res)
                        inf_fake = " ".join(inf_fake_words)
                        
                        self.entity_map[inf_fake] = inf_orig
                        
                        # Добавляем пословный маппинг на случай, если нейросеть переставит слова местами (например ФИО -> ИОФ)
                        if len(inf_fake_words) == len(inf_orig_words):
                            for fw, ow in zip(inf_fake_words, inf_orig_words):
                                if len(fw) > 3: # Заменяем только слова от 4 букв, чтобы не сломать текст
                                    self.entity_map[fw] = ow
                        if inf_orig == original_value:
                            matched_fake_token = inf_fake
                            
                    # Подставляем правильный падеж, либо дефолт (Именительный)
                    token = matched_fake_token if matched_fake_token else fake_base
                    self.entity_map[token] = original_value # fallback
                    
                elif entity_type == "EMAIL_ADDRESS":
                    token = fake.ascii_company_email()
                    self.entity_map[token] = original_value
                elif entity_type == "PHONE_NUMBER":
                    token = fake.phone_number()
                    self.entity_map[token] = original_value
                elif entity_type == "CREDIT_CARD":
                    # Генерируем 16 цифр
                    token = str(fake.credit_card_number(card_type="mastercard"))
                    self.entity_map[token] = original_value
                    # На случай, если нейросеть сократит карту (например "4276...")
                    self.entity_map[token[:4] + "..."] = original_value[:4] + "..."
                elif entity_type == "RU_ORGANIZATION":
                    token = fake.company()
                    self.entity_map[token] = original_value
                elif entity_type == "RU_FINANCIAL":
                    # Генерируем случайные данные, сохраняя структуру (пробелы, тире, буквы)
                    token = ""
                    for char in original_value:
                        if char.isdigit():
                            token += str(fake.random.randint(0, 9))
                        elif char.isalpha():
                            token += fake.random.choice('АВЕКМНОРСТУХ')
                        else:
                            token += char
                    self.entity_map[token] = original_value
                elif entity_type == "URL":
                    token = fake.url()
                    self.entity_map[token] = original_value
                else:
                    if entity_type not in self.counter:
                        self.counter[entity_type] = 1
                    else:
                        self.counter[entity_type] += 1
                    token = f"[{entity_type}_{self.counter[entity_type]}]"
                    self.entity_map[token] = original_value
                    
            anonymized_text = anonymized_text[:res.start] + token + anonymized_text[res.end:]
            
        return anonymized_text

    def anonymize_context_number(self, text: str) -> str:
        """Анонимизирует числовые значения, сохраняя их формат. Используется для контекстных столбцов (например, Зарплата)."""
        original_value = str(text)
        
        # Если уже заменяли, возвращаем
        for existing_token, val in self.entity_map.items():
            if val == original_value:
                return existing_token
                
        # Генерируем случайное число с такой же структурой
        token = ""
        for char in original_value:
            if char.isdigit():
                token += str(fake.random.randint(0, 9))
            else:
                token += char
                
        self.entity_map[token] = original_value
        return token

    def deanonymize(self, text: str) -> str:
        """Восстанавливает оригинальные данные из текста."""
        result = text
        
        # Сортируем ключи по длине убыванию, чтобы сначала заменялись полные фразы, а потом отдельные слова
        sorted_tokens = sorted(self.entity_map.keys(), key=len, reverse=True)
        
        # Заменяем токены обратно на оригинальные значения
        for token in sorted_tokens:
            original_value = self.entity_map[token]
            result = result.replace(token, original_value)
            
        return result
