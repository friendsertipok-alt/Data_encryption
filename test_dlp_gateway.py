import unittest
import io
import json
import sqlite3
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from main import app
from config import DB_PATH
from session_store import create_session, get_session_map, get_user_sessions

class TestDlpGateway(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_text_anonymize_and_deanonymize(self):
        original_text = "Сотрудник Иванов Иван Иванович (email: ivanov@company.ru, тел: +7 999 123-45-67) запросил отчет."
        
        # 1. Анонимизация текста
        response = self.client.post(
            "/api/anonymize/text",
            json={"text": original_text, "mode": "fake", "lang": "ru"}
        )
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")
        data = response.json()
        
        self.assertIn("anonymized_text", data)
        self.assertIn("session_id", data)
        self.assertGreater(data["entities_found"], 0)
        
        anonymized_text = data["anonymized_text"]
        session_id = data["session_id"]
        
        self.assertNotIn("ivanov@company.ru", anonymized_text)
        self.assertNotIn("+7 999 123-45-67", anonymized_text)
        
        # 2. Деанонимизация ответа
        fake_llm_reply = f"Получены данные: {anonymized_text}. Обработано успешно."
        
        deanon_resp = self.client.post(
            "/api/deanonymize/text",
            json={"text": fake_llm_reply, "session_id": session_id}
        )
        self.assertEqual(deanon_resp.status_code, 200)
        deanon_data = deanon_resp.json()
        
        restored = deanon_data["restored_text"]
        self.assertIn("ivanov@company.ru", restored)
        self.assertIn("+7 999 123-45-67", restored)

    def test_expanded_pii_detectors(self):
        """Тест новых детекторов: Водительские права, ОМС, Адрес, Карта с алгоритмом Луна"""
        test_text = (
            "Водительские права: 77 14 892015. "
            "Полис ОМС: 1234567890123456. "
            "Адрес проживания: г. Москва, ул. Тверская, д. 10, кв. 5. "
            "Карта Visa: 4532015112830366." # Валидный номер по алгоритму Луна
        )
        
        response = self.client.post(
            "/api/anonymize/text",
            json={"text": test_text, "mode": "fake", "lang": "ru"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        anon_text = data["anonymized_text"]
        
        self.assertNotIn("77 14 892015", anon_text)
        self.assertNotIn("1234567890123456", anon_text)
        self.assertNotIn("4532015112830366", anon_text)
        
        # Проверка деанонимизации
        deanon_resp = self.client.post(
            "/api/deanonymize/text",
            json={"text": anon_text, "session_id": data["session_id"]}
        )
        restored = deanon_resp.json()["restored_text"]
        self.assertIn("77 14 892015", restored)
        self.assertIn("1234567890123456", restored)
        self.assertIn("4532015112830366", restored)

    def test_sqlite_encryption(self):
        """Проверка Encryption at Rest: данные в SQLite базе хранятся в зашифрованном виде (Fernet AES-256)"""
        session_id = create_session({"REAL_SECRET_KEY_123": "ORIGINAL_SECRET_PII"}, filename="crypto_test.txt")
        
        # Читаем сырое содержимое из файла SQLite базы данных
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT entity_map_json FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        encrypted_blob = row[0]
        
        # В файле БД НЕ должно быть открытого текста "ORIGINAL_SECRET_PII"
        self.assertNotIn("ORIGINAL_SECRET_PII", encrypted_blob)
        self.assertTrue(encrypted_blob.startswith("gAAAAA"), "Blob should start with Fernet magic header 'gAAAAA'")
        
        # При этом get_session_map должен успешно расшифровывать данные
        decrypted_map = get_session_map(session_id)
        self.assertEqual(decrypted_map.get("REAL_SECRET_KEY_123"), "ORIGINAL_SECRET_PII")

    def test_image_anonymization(self):
        """Тестирование загрузки изображения PNG на эндпоинт анонимизации"""
        img = Image.new("RGB", (300, 100), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Паспорт 4510 123456", fill=(0, 0, 0))
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()
        
        response = self.client.post(
            "/api/anonymize/file",
            files={"file": ("passport_scan.png", io.BytesIO(img_bytes), "image/png")},
            data={"mode": "fake"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Session-ID", response.headers)
        self.assertEqual(response.headers["content-type"], "application/octet-stream")

if __name__ == "__main__":
    unittest.main()
