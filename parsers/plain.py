import json
import csv
import io
import xml.etree.ElementTree as ET

class PlainParser:
    @staticmethod
    def anonymize_txt(file_bytes: bytes, anonymize_func) -> bytes:
        text = file_bytes.decode('utf-8')
        anonymized = anonymize_func(text)
        return anonymized.encode('utf-8')

    @staticmethod
    def deanonymize_txt(file_bytes: bytes, deanonymize_func) -> bytes:
        text = file_bytes.decode('utf-8')
        restored = deanonymize_func(text)
        return restored.encode('utf-8')

    @staticmethod
    def anonymize_csv(file_bytes: bytes, anonymize_func) -> bytes:
        text = file_bytes.decode('utf-8')
        reader = csv.reader(io.StringIO(text))
        output = io.StringIO()
        writer = csv.writer(output)
        for row in reader:
            new_row = [anonymize_func(cell) if cell.strip() else cell for cell in row]
            writer.writerow(new_row)
        return output.getvalue().encode('utf-8')

    @staticmethod
    def deanonymize_csv(file_bytes: bytes, deanonymize_func) -> bytes:
        text = file_bytes.decode('utf-8')
        reader = csv.reader(io.StringIO(text))
        output = io.StringIO()
        writer = csv.writer(output)
        for row in reader:
            new_row = [deanonymize_func(cell) if cell.strip() else cell for cell in row]
            writer.writerow(new_row)
        return output.getvalue().encode('utf-8')

    @staticmethod
    def _recursive_json_anonymize(data, func):
        if isinstance(data, dict):
            return {k: PlainParser._recursive_json_anonymize(v, func) for k, v in data.items()}
        elif isinstance(data, list):
            return [PlainParser._recursive_json_anonymize(v, func) for v in data]
        elif isinstance(data, str):
            return func(data)
        return data

    @staticmethod
    def anonymize_json(file_bytes: bytes, anonymize_func) -> bytes:
        data = json.loads(file_bytes.decode('utf-8'))
        anonymized_data = PlainParser._recursive_json_anonymize(data, anonymize_func)
        return json.dumps(anonymized_data, ensure_ascii=False, indent=2).encode('utf-8')

    @staticmethod
    def deanonymize_json(file_bytes: bytes, deanonymize_func) -> bytes:
        data = json.loads(file_bytes.decode('utf-8'))
        restored_data = PlainParser._recursive_json_anonymize(data, deanonymize_func)
        return json.dumps(restored_data, ensure_ascii=False, indent=2).encode('utf-8')

    @staticmethod
    def anonymize_tsv(file_bytes: bytes, anonymize_func) -> bytes:
        text = file_bytes.decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(text), delimiter='\t')
        output = io.StringIO()
        writer = csv.writer(output, delimiter='\t')
        for row in reader:
            new_row = [anonymize_func(cell) if cell.strip() else cell for cell in row]
            writer.writerow(new_row)
        return output.getvalue().encode('utf-8')

    @staticmethod
    def deanonymize_tsv(file_bytes: bytes, deanonymize_func) -> bytes:
        text = file_bytes.decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(text), delimiter='\t')
        output = io.StringIO()
        writer = csv.writer(output, delimiter='\t')
        for row in reader:
            new_row = [deanonymize_func(cell) if cell.strip() else cell for cell in row]
            writer.writerow(new_row)
        return output.getvalue().encode('utf-8')

    @staticmethod
    def anonymize_html(file_bytes: bytes, anonymize_func) -> bytes:
        text = file_bytes.decode('utf-8', errors='ignore')
        # Использование ElementTree / HTMLParser для сохранения тегов
        try:
            tree = ET.ElementTree(ET.fromstring(text))
            for elem in tree.iter():
                if elem.text and elem.text.strip():
                    elem.text = anonymize_func(elem.text)
                if elem.tail and elem.tail.strip():
                    elem.tail = anonymize_func(elem.tail)
            output = io.BytesIO()
            tree.write(output, encoding='utf-8')
            return output.getvalue()
        except Exception:
            # Откат к контекстной строковой обработке для невалидного HTML
            return anonymize_func(text).encode('utf-8')

    @staticmethod
    def deanonymize_html(file_bytes: bytes, deanonymize_func) -> bytes:
        text = file_bytes.decode('utf-8', errors='ignore')
        try:
            tree = ET.ElementTree(ET.fromstring(text))
            for elem in tree.iter():
                if elem.text and elem.text.strip():
                    elem.text = deanonymize_func(elem.text)
                if elem.tail and elem.tail.strip():
                    elem.tail = deanonymize_func(elem.tail)
            output = io.BytesIO()
            tree.write(output, encoding='utf-8')
            return output.getvalue()
        except Exception:
            return deanonymize_func(text).encode('utf-8')

    @staticmethod
    def anonymize_xml(file_bytes: bytes, anonymize_func) -> bytes:
        tree = ET.ElementTree(ET.fromstring(file_bytes.decode('utf-8', errors='ignore')))
        for elem in tree.iter():
            if elem.text and elem.text.strip():
                elem.text = anonymize_func(elem.text)
            if elem.tail and elem.tail.strip():
                elem.tail = anonymize_func(elem.tail)
            for attr, val in elem.attrib.items():
                if val.strip():
                    elem.attrib[attr] = anonymize_func(val)
        output = io.BytesIO()
        tree.write(output, encoding='utf-8', xml_declaration=True)
        return output.getvalue()

    @staticmethod
    def deanonymize_xml(file_bytes: bytes, deanonymize_func) -> bytes:
        tree = ET.ElementTree(ET.fromstring(file_bytes.decode('utf-8', errors='ignore')))
        for elem in tree.iter():
            if elem.text and elem.text.strip():
                elem.text = deanonymize_func(elem.text)
            if elem.tail and elem.tail.strip():
                elem.tail = deanonymize_func(elem.tail)
            for attr, val in elem.attrib.items():
                if val.strip():
                    elem.attrib[attr] = deanonymize_func(val)
        output = io.BytesIO()
        tree.write(output, encoding='utf-8', xml_declaration=True)
        return output.getvalue()

    @staticmethod
    def anonymize_rtf(file_bytes: bytes, anonymize_func) -> bytes:
        text = file_bytes.decode('utf-8', errors='ignore')
        return anonymize_func(text).encode('utf-8')

    @staticmethod
    def deanonymize_rtf(file_bytes: bytes, deanonymize_func) -> bytes:
        text = file_bytes.decode('utf-8', errors='ignore')
        return deanonymize_func(text).encode('utf-8')
