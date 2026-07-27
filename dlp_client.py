import urllib.request
import urllib.parse
import json
import os
from typing import List, Dict, Tuple, Optional

class ProjectSession:
    """Вспомогательный класс для работы с группой документов в рамках одного проекта."""
    def __init__(self, client: 'DlpGatewayClient', group_id: str):
        self.client = client
        self.group_id = group_id

    def anonymize_file(self, filepath: str, mode: str = "fake") -> Tuple[str, str]:
        return self.client.anonymize_file(filepath, group_id=self.group_id, mode=mode)

    def anonymize_files(self, filepaths: List[str], mode: str = "fake") -> List[Tuple[str, str]]:
        return self.client.anonymize_batch(filepaths, group_id=self.group_id, mode=mode)

    def anonymize_text(self, text: str, mode: str = "fake") -> Tuple[str, str]:
        return self.client.anonymize_text(text, group_id=self.group_id, mode=mode)

    def deanonymize_text(self, text: str) -> str:
        return self.client.deanonymize_text(text, session_id_or_group_id=self.group_id)

    def deanonymize_file(self, filepath: str) -> str:
        return self.client.deanonymize_file(filepath, session_id_or_group_id=self.group_id)


class DlpGatewayClient:
    """
    Официальный Python SDK клиент для интеграции Universal DLP Gateway в любые сторонние проекты.
    Не требует сторонних зависимостей (использует встроенную библиотеку urllib).
    """
    def __init__(self, base_url: str = "http://localhost:8001", api_key: str = "test_key_123"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def create_project(self, group_id: str) -> ProjectSession:
        """Создает проектную сессию для пакета файлов с гарантией единого контекста замен."""
        return ProjectSession(self, group_id)

    def anonymize_text(self, text: str, group_id: Optional[str] = None, mode: str = "fake", lang: str = "auto") -> Tuple[str, str]:
        """Анонимизирует строку текста. Возвращает (anonymized_text, session_id)."""
        url = f"{self.base_url}/api/anonymize/text"
        payload = {
            "text": text,
            "mode": mode,
            "lang": lang,
            "group_id": group_id
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        })
        with urllib.request.urlopen(req) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            return res_json["anonymized_text"], res_json["session_id"]

    def deanonymize_text(self, text: str, session_id_or_group_id: str) -> str:
        """Восстанавливает текст по одному ID, нескольким ID через запятую или Коду Проекта (group_id)."""
        url = f"{self.base_url}/api/deanonymize/text"
        payload = {
            "text": text,
            "session_id": session_id_or_group_id
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        })
        with urllib.request.urlopen(req) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            return res_json["restored_text"]

    def _multipart_encode(self, fields: dict, files: dict) -> Tuple[bytes, str]:
        boundary = '----DlpGatewayBoundary' + os.urandom(16).hex()
        body = []
        for name, value in fields.items():
            if value is None:
                continue
            body.append(f'--{boundary}'.encode('utf-8'))
            body.append(f'Content-Disposition: form-data; name="{name}"'.encode('utf-8'))
            body.append(b'')
            body.append(str(value).encode('utf-8'))
        for name, (filename, content) in files.items():
            body.append(f'--{boundary}'.encode('utf-8'))
            body.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode('utf-8'))
            body.append(b'Content-Type: application/octet-stream')
            body.append(b'')
            body.append(content)
        body.append(f'--{boundary}--'.encode('utf-8'))
        body.append(b'')
        payload = b'\r\n'.join(body)
        content_type = f'multipart/form-data; boundary={boundary}'
        return payload, content_type

    def anonymize_file(self, filepath: str, group_id: Optional[str] = None, mode: str = "fake", output_path: Optional[str] = None) -> Tuple[str, str]:
        """Анонимизирует файл на диске. Возвращает (путь_к_анонимизированному_файлу, session_id)."""
        url = f"{self.base_url}/api/anonymize/file"
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            file_bytes = f.read()

        fields = {'mode': mode}
        if group_id:
            fields['group_id'] = group_id
        files = {'file': (filename, file_bytes)}
        
        payload, content_type = self._multipart_encode(fields, files)
        req = urllib.request.Request(url, data=payload, headers={
            'Content-Type': content_type,
            'X-API-Key': self.api_key
        })
        with urllib.request.urlopen(req) as resp:
            anon_bytes = resp.read()
            session_id = resp.headers.get('X-Session-ID', '')
            if not output_path:
                out_dir = os.path.dirname(filepath)
                output_path = os.path.join(out_dir, f"safe_{filename}")
            with open(output_path, 'wb') as out_f:
                out_f.write(anon_bytes)
            return output_path, session_id

    def deanonymize_file(self, filepath: str, session_id_or_group_id: str, output_path: Optional[str] = None) -> str:
        """Восстанавливает оригинальный документ по защищенному файлу и ID сессии/группы."""
        url = f"{self.base_url}/api/deanonymize/file"
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            file_bytes = f.read()

        fields = {'session_id': session_id_or_group_id}
        files = {'file': (filename, file_bytes)}
        payload, content_type = self._multipart_encode(fields, files)
        req = urllib.request.Request(url, data=payload, headers={
            'Content-Type': content_type,
            'X-API-Key': self.api_key
        })
        with urllib.request.urlopen(req) as resp:
            restored_bytes = resp.read()
            if not output_path:
                out_dir = os.path.dirname(filepath)
                prefix = "restored_" if not filename.startswith("safe_") else ""
                clean_name = filename[5:] if filename.startswith("safe_") else filename
                output_path = os.path.join(out_dir, f"{prefix}{clean_name}")
            with open(output_path, 'wb') as out_f:
                out_f.write(restored_bytes)
            return output_path

    def anonymize_batch(self, filepaths: List[str], group_id: Optional[str] = None, mode: str = "fake") -> List[Tuple[str, str]]:
        """Пакетная обработка любого количества файлов (10, 50, 100+)."""
        if not group_id:
            group_id = f"batch_{os.urandom(4).hex()}"
        results = []
        for fp in filepaths:
            res = self.anonymize_file(fp, group_id=group_id, mode=mode)
            results.append(res)
        return results
