import io
import fitz  # PyMuPDF

class PdfParser:
    """
    Парсер для PDF.
    Использует PyMuPDF для поиска конфиденциального текста и его редактирования (redaction).
    """
    @staticmethod
    def anonymize_pdf(file_bytes: bytes, anonymize_func, entity_map: dict) -> bytes:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        for page in doc:
            text = page.get_text("text")
            if not text.strip():
                continue
                
            # Прогоняем текст через функцию анонимизации, 
            # которая пополнит общий словарь entity_map
            anonymize_func(text)
                    
            # Для каждого найденного значения в словаре ищем его на странице и заменяем
            # В entity_map ключи - это токены(фейки), значения - оригинальные строки
            for token, original_value in entity_map.items():
                text_instances = page.search_for(original_value)
                for inst in text_instances:
                    # Добавляем аннотацию redaction с текстом замены
                    page.add_redact_annot(inst, text=token, fill=(0, 0, 0), text_color=(1, 1, 1))
                    
            # Применяем все redactions на странице
            page.apply_redactions()
            
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue()

    @staticmethod
    def deanonymize_pdf(file_bytes: bytes, entity_map: dict) -> bytes:
        """
        Восстановление PDF - очень сложная задача, так как redaction разрушает оригинальный текст.
        Для прототипа мы просто ищем токены и пытаемся их заменить, но визуально это может выглядеть криво.
        """
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            for token, original_value in entity_map.items():
                text_instances = page.search_for(token)
                for inst in text_instances:
                    page.add_redact_annot(inst, text=original_value, fill=(1, 1, 1), text_color=(0, 0, 0))
            page.apply_redactions()
            
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue()
