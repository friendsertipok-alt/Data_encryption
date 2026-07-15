import re
with open("anonymizer.py", "r") as f:
    content = f.read()

import_statement = """
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
"""

# Insert imports and classes after faker import
content = content.replace("from faker import Faker\nimport pymorphy3", "from faker import Faker\nimport pymorphy3\n" + import_statement)

registration = """
# Регистрируем оба детектора
analyzer.registry.add_recognizer(ru_org_recognizer)
analyzer.registry.add_recognizer(ru_phone_recognizer)
analyzer.registry.add_recognizer(NatashaPersonRecognizer())

# Убираем дефолтный spaCy распознаватель PERSON
for rec in analyzer.registry.get_recognizers(language="ru", entities=["PERSON"]):
    if rec.name == "SpacyRecognizer" and "PERSON" in rec.supported_entities:
        rec.supported_entities.remove("PERSON")
"""

content = content.replace("# Регистрируем оба детектора\nanalyzer.registry.add_recognizer(ru_org_recognizer)\nanalyzer.registry.add_recognizer(ru_phone_recognizer)", registration)

with open("anonymizer.py", "w") as f:
    f.write(content)
