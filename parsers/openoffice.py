import io
import zipfile
import xml.etree.ElementTree as ET

class OpenOfficeParser:
    """
    Парсер для формата OpenDocument (LibreOffice / OpenOffice: .odt, .ods, .odp).
    Распаковывает ZIP-архив документа, модифицирует content.xml и сохраняет 100% верстки и стилей.
    """
    @staticmethod
    def _process_xml_content(content_bytes: bytes, process_func) -> bytes:
        tree = ET.ElementTree(ET.fromstring(content_bytes.decode('utf-8')))
        for elem in tree.iter():
            if elem.text and elem.text.strip():
                processed = process_func(elem.text)
                if processed != elem.text:
                    elem.text = processed
            if elem.tail and elem.tail.strip():
                processed = process_func(elem.tail)
                if processed != elem.tail:
                    elem.tail = processed
        output = io.BytesIO()
        tree.write(output, encoding='utf-8', xml_declaration=True)
        return output.getvalue()

    @staticmethod
    def anonymize_opendocument(file_bytes: bytes, anonymize_func) -> bytes:
        in_zip = zipfile.ZipFile(io.BytesIO(file_bytes), 'r')
        out_buffer = io.BytesIO()
        out_zip = zipfile.ZipFile(out_buffer, 'w', compression=zipfile.ZIP_DEFLATED)

        for item in in_zip.infolist():
            content = in_zip.read(item.filename)
            if item.filename in ("content.xml", "styles.xml"):
                content = OpenOfficeParser._process_xml_content(content, anonymize_func)
            out_zip.writestr(item, content)

        in_zip.close()
        out_zip.close()
        return out_buffer.getvalue()

    @staticmethod
    def deanonymize_opendocument(file_bytes: bytes, deanonymize_func) -> bytes:
        in_zip = zipfile.ZipFile(io.BytesIO(file_bytes), 'r')
        out_buffer = io.BytesIO()
        out_zip = zipfile.ZipFile(out_buffer, 'w', compression=zipfile.ZIP_DEFLATED)

        for item in in_zip.infolist():
            content = in_zip.read(item.filename)
            if item.filename in ("content.xml", "styles.xml"):
                content = OpenOfficeParser._process_xml_content(content, deanonymize_func)
            out_zip.writestr(item, content)

        in_zip.close()
        out_zip.close()
        return out_buffer.getvalue()
