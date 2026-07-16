from core.detector import DlpDetector

# Глобальный экземпляр детектора, чтобы не загружать тяжелые NLP модели дважды
detector = DlpDetector()
