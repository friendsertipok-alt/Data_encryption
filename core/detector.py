import re
from typing import Dict, List, Tuple
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern

from core.entities.russia import RUSSIA_PATTERNS
from core.entities.india import INDIA_PATTERNS
from core.nlp.multilingual_nlp import get_multilingual_nlp_engine
from core.nlp.russian_nlp import NatashaRecognizer
from core.faker_engine import FakerEngine
from core.cache import LRUCache

class DlpDetector:
    """
    Продвинутый движок DLP с двухпроходной архитектурой (Regex -> NLP) и кэшированием.
    """
    def __init__(self):
        # NLP Engine
        self.nlp_engine = get_multilingual_nlp_engine()
        
        # Анализатор только для NLP (Pass 2)
        self.nlp_analyzer = AnalyzerEngine(nlp_engine=self.nlp_engine, supported_languages=["ru", "en"])
        self.nlp_analyzer.registry.add_recognizer(NatashaRecognizer())
        for rec in self.nlp_analyzer.registry.get_recognizers(language="ru", entities=["PERSON"]):
            if rec.name == "SpacyRecognizer" and "PERSON" in rec.supported_entities:
                rec.supported_entities.remove("PERSON")
                
        # Анализатор только для Regex (Pass 1)
        self.regex_analyzer = AnalyzerEngine(nlp_engine=self.nlp_engine, supported_languages=["ru", "en"])
        
        # Очищаем дефолтные recognizers из regex_analyzer, оставляем только наши паттерны
        self.regex_analyzer.registry.recognizers = []
        
        # Регистрация Regex
        self._register_regex_recognizers()
        
        self.faker_engine = FakerEngine()
        self.cache = LRUCache(capacity=2048)
        
        self.nlp_entities = ["PERSON", "RU_ORGANIZATION", "RU_LOCATION", "EMAIL_ADDRESS", "CREDIT_CARD"]
        self.regex_entities = list(RUSSIA_PATTERNS.keys()) + list(INDIA_PATTERNS.keys())
        
    def _register_regex_recognizers(self):
        # Россия
        for name, regex in RUSSIA_PATTERNS.items():
            rec = PatternRecognizer(
                supported_entity=name,
                supported_language="ru",
                patterns=[Pattern(name=name, regex=regex.pattern, score=1.0)],
                name=f"RU_{name}_Recognizer"
            )
            self.regex_analyzer.registry.add_recognizer(rec)
            
        # Индия
        for name, regex in INDIA_PATTERNS.items():
            rec = PatternRecognizer(
                supported_entity=name,
                supported_language="en",
                patterns=[Pattern(name=name, regex=regex.pattern, score=1.0)],
                name=f"IN_{name}_Recognizer"
            )
            self.regex_analyzer.registry.add_recognizer(rec)

    def detect_language(self, text: str) -> str:
        """Автоматическое определение языка по наличию кириллицы."""
        if re.search(r'[а-яА-ЯёЁ]', text):
            return 'ru'
        return 'en'

    def analyze_and_anonymize(self, text: str, entity_map: Dict[str, str], lang: str = 'auto') -> str:
        if not text.strip():
            return text
            
        if lang == 'auto':
            lang = self.detect_language(text)
            
        # 1. Проверка кэша
        cached = self.cache.get(text)
        if cached is not None:
            return cached
            
        anonymized_text = text
        
        # --- PASS 1: REGEX ---
        regex_results = self.regex_analyzer.analyze(
            text=anonymized_text,
            entities=self.regex_entities,
            language=lang,
            score_threshold=0.9
        )
        
        # Заменяем Regex находки справа налево
        regex_results.sort(key=lambda x: x.start, reverse=True)
        for res in regex_results:
            original_value = anonymized_text[res.start:res.end]
            
            # Проверка, есть ли уже этот оригинал в мапе (для Canonical Mapping)
            token = self._get_existing_token(original_value, entity_map)
            if not token:
                token = self.faker_engine.generate_fake(res.entity_type, original_value)
                entity_map[token] = original_value
                
            anonymized_text = anonymized_text[:res.start] + token + anonymized_text[res.end:]
            
        # --- PASS 2: NLP ---
        nlp_results = self.nlp_analyzer.analyze(
            text=anonymized_text,
            entities=self.nlp_entities,
            language=lang,
            score_threshold=0.6
        )
        
        # Фильтруем NLP результаты (удаляем пересечения с нашими уже вставленными токенами)
        # NLP может попытаться заменить кусок фейка, если он выглядит как настоящее имя
        # Но поскольку мы идем справа налево, индексы фейков мы можем вычислить, 
        # но проще отсеять пересечения
        # Для безопасности просто применяем замены.
        
        # Отфильтруем NLP результаты: оставляем самые длинные и непересекающиеся
        filtered_nlp = []
        nlp_results.sort(key=lambda x: (x.end - x.start), reverse=True)
        for res in nlp_results:
            overlap = any(max(res.start, f.start) < min(res.end, f.end) for f in filtered_nlp)
            if not overlap:
                filtered_nlp.append(res)
                
        filtered_nlp.sort(key=lambda x: x.start, reverse=True)
        
        for res in filtered_nlp:
            original_value = anonymized_text[res.start:res.end]
            
            # Если NLP нашел кусок нашего фейка (мы ранее вставили фейк), пропускаем
            if any(original_value in f for f in entity_map.keys()):
                continue
            
            token = self._get_existing_token(original_value, entity_map)
            
            if not token:
                if res.entity_type == "PERSON" and lang == 'ru':
                    token = self._handle_russian_person(original_value, entity_map)
                else:
                    token = self.faker_engine.generate_fake(res.entity_type, original_value)
                    entity_map[token] = original_value
                    
            anonymized_text = anonymized_text[:res.start] + token + anonymized_text[res.end:]
            
        # Сохраняем в кэш
        self.cache.put(text, anonymized_text)
        return anonymized_text
        
    def _get_existing_token(self, original_value: str, entity_map: Dict[str, str]) -> str | None:
        """Поиск уже существующего фейка (Case-insensitive)"""
        norm_orig = original_value.strip().lower()
        for token, val in entity_map.items():
            if val.strip().lower() == norm_orig:
                # Если нашли в другом регистре, вернем этот же фейк
                return token
        return None
        
    def _handle_russian_person(self, original_value: str, entity_map: Dict[str, str]) -> str:
        """Склоняет русское имя по падежам и заполняет entity_map"""
        original_words = original_value.split()
        
        base_orig_words = []
        for w in original_words:
            p = self.faker_engine.morph.parse(w)[0]
            inf = p.inflect({'nomn'})
            inf_res = inf.word if inf else w
            if w.istitle(): inf_res = inf_res.capitalize()
            base_orig_words.append(inf_res)
            
        fake_base = self.faker_engine.generate_fake("PERSON", original_value)
        fake_words = fake_base.split()
        
        cases = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']
        matched_fake_token = None
        
        for case in cases:
            inf_orig, inf_fake, inf_orig_words, inf_fake_words = self.faker_engine.morph_russian_name(original_words, fake_words, case)
            
            entity_map[inf_fake] = inf_orig
            if len(inf_fake_words) == len(inf_orig_words):
                for fw, ow in zip(inf_fake_words, inf_orig_words):
                    if len(fw) > 3: 
                        entity_map[fw] = ow
                        
            if inf_orig.lower() == original_value.lower():
                matched_fake_token = inf_fake
                
        token = matched_fake_token if matched_fake_token else fake_base
        entity_map[token] = original_value
        return token

    def deanonymize(self, text: str, entity_map: Dict[str, str]) -> str:
        result = text
        sorted_tokens = sorted(entity_map.keys(), key=len, reverse=True)
        for token in sorted_tokens:
            original_value = entity_map[token]
            result = result.replace(token, original_value)
        return result
