from presidio_analyzer.nlp_engine import NlpEngineProvider

def get_multilingual_nlp_engine():
    """
    Возвращает настроенный NlpEngine для Microsoft Presidio, 
    поддерживающий русский (ru) и английский (en) языки через spaCy.
    """
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "ru", "model_name": "ru_core_news_md"},
            {"lang_code": "en", "model_name": "en_core_web_sm"}, # Используем sm для скорости (или lg для точности, если скачан)
        ],
    }

    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    return provider.create_engine()
