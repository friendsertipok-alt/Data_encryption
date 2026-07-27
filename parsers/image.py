import io
from PIL import Image, ImageDraw, ImageFont
import logging

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

logger = logging.getLogger("ImageParser")

class ImageParser:
    """
    Парсер изображений для извлечения текста (OCR) и визуальной анонимизации конфиденциальных данных.
    """
    @staticmethod
    def anonymize_image(image_bytes: bytes, anonymize_func, entity_map: dict) -> bytes:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        if not PYTESSERACT_AVAILABLE:
            logger.warning("pytesseract не установлен. Возвращается исходное изображение.")
            output = io.BytesIO()
            img.save(output, format="PNG")
            return output.getvalue()
            
        try:
            # Выполняем OCR с помощью pytesseract (русский + английский)
            data = pytesseract.image_to_data(img, lang="rus+eng", output_type=pytesseract.Output.DICT)
            
            n_boxes = len(data['text'])
            draw = ImageDraw.Draw(img)
            
            # Извлекаем все слова и проверяем на PII
            full_text = " ".join([data['text'][i] for i in range(n_boxes) if data['text'][i].strip()])
            anonymize_func(full_text) # Наполняет entity_map
            
            sensitive_words = set()
            for token, real_val in entity_map.items():
                for part in real_val.split():
                    if len(part) > 2:
                        sensitive_words.add(part.lower())
                        
            # Маскируем черными прямоугольниками найденные PII слова
            for i in range(n_boxes):
                word = data['text'][i].strip().lower()
                if not word:
                    continue
                    
                if any(s_word in word or word in s_word for s_word in sensitive_words):
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    # Закрашиваем чувствительное слово черным блёром/плашкой
                    draw.rectangle([x, y, x + w, y + h], fill="black")
                    
        except Exception as e:
            logger.error(f"Ошибка OCR при обработке изображения: {e}")
            
        output = io.BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()

    @staticmethod
    def deanonymize_image(image_bytes: bytes, deanonymize_func) -> bytes:
        # Для растровых картинок цензурированные плашки необратимы без бекапа оригинала,
        # поэтому возвращаем замаскированное изображение
        return image_bytes
