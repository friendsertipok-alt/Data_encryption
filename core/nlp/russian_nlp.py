from presidio_analyzer import EntityRecognizer, RecognizerResult
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsNERTagger, Doc

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)

class NatashaRecognizer(EntityRecognizer):
    """
    Распознаватель сущностей на основе библиотеки Natasha (работает для русского языка).
    Ищет ФИО (PERSON), Организации (RU_ORGANIZATION) и Локации/Адреса (RU_LOCATION).
    """
    def __init__(self):
        super().__init__(supported_entities=["PERSON", "RU_ORGANIZATION", "RU_LOCATION"], supported_language="ru")

    def load(self) -> None:
        pass

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        doc = Doc(text)
        doc.segment(segmenter)
        doc.tag_ner(ner_tagger)
        for span in doc.spans:
            if span.type == 'PER' and "PERSON" in entities:
                results.append(RecognizerResult(
                    entity_type="PERSON",
                    start=span.start,
                    end=span.stop,
                    score=0.95
                ))
            elif span.type == 'ORG' and "RU_ORGANIZATION" in entities:
                results.append(RecognizerResult(
                    entity_type="RU_ORGANIZATION",
                    start=span.start,
                    end=span.stop,
                    score=0.90
                ))
            elif span.type == 'LOC' and "RU_LOCATION" in entities:
                results.append(RecognizerResult(
                    entity_type="RU_LOCATION",
                    start=span.start,
                    end=span.stop,
                    score=0.90
                ))
        return results
