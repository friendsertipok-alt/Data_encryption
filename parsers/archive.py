import io
import zipfile
import os

class ArchiveParser:
    """
    Парсер для ZIP-архивов.
    Автоматически рекурсивно обрабатывает все вложенные документы внутри архива,
    сохраняя оригинальную структуру папок и подкаталогов.
    """
    @staticmethod
    def anonymize_zip(file_bytes: bytes, file_processor_func) -> bytes:
        in_zip = zipfile.ZipFile(io.BytesIO(file_bytes), 'r')
        out_buffer = io.BytesIO()
        out_zip = zipfile.ZipFile(out_buffer, 'w', compression=zipfile.ZIP_DEFLATED)

        for item in in_zip.infolist():
            content = in_zip.read(item.filename)
            filename = item.filename
            
            # Пропускаем служебные директории zip
            if item.is_dir():
                out_zip.writestr(item, content)
                continue

            # Вызываем универсальный обработчик файла по имени и содержимому
            processed_content = file_processor_func(filename, content, is_deanonymize=False)
            out_zip.writestr(item, processed_content)

        in_zip.close()
        out_zip.close()
        return out_buffer.getvalue()

    @staticmethod
    def deanonymize_zip(file_bytes: bytes, file_processor_func) -> bytes:
        in_zip = zipfile.ZipFile(io.BytesIO(file_bytes), 'r')
        out_buffer = io.BytesIO()
        out_zip = zipfile.ZipFile(out_buffer, 'w', compression=zipfile.ZIP_DEFLATED)

        for item in in_zip.infolist():
            content = in_zip.read(item.filename)
            filename = item.filename
            
            if item.is_dir():
                out_zip.writestr(item, content)
                continue

            processed_content = file_processor_func(filename, content, is_deanonymize=True)
            out_zip.writestr(item, processed_content)

        in_zip.close()
        out_zip.close()
        return out_buffer.getvalue()
