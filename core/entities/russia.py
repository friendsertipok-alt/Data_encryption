import re

# Россия: Регулярные выражения для поиска конфиденциальных данных

# Паспорт РФ (серия 4 цифры + опциональный №/N/- + 6 цифр номера)
PASSPORT_RU_REGEX = re.compile(r'\b\d{2}\s*\d{2}\s*(?:№|N|-)?\s*\d{6}\b', re.IGNORECASE)

# Загранпаспорт РФ (2 цифры + 7 цифр)
INTL_PASSPORT_RU_REGEX = re.compile(r'\b\d{2}\s*\d{7}\b')

# ИНН (10 или 12 цифр) — с контекстным ключевым словом для снижения ложных срабатываний
INN_RU_REGEX = re.compile(r'(?:ИНН|инн|INN|Инн)[:\s№]*?(\d{10}(?:\d{2})?)', re.IGNORECASE)

# СНИЛС (123-456-789 12 или 12345678912)
SNILS_RU_REGEX = re.compile(r'\b\d{3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{2}\b')

# ОГРН (13 цифр) и ОГРНИП (15 цифр)
OGRN_RU_REGEX = re.compile(r'\b\d{13}(?:\d{2})?\b')

# КПП (9 цифр) — только при наличии ключевого слова "КПП"
KPP_RU_REGEX = re.compile(r'(?:КПП|кпп|Кпп)[:\s№]*?(\d{9})', re.IGNORECASE)

# Номер банковского счёта (20 цифр, в РФ начинается на 4)
BANK_ACCOUNT_RU_REGEX = re.compile(r'\b4\d{19}\b')

# БИК (9 цифр, начинается на 04)
BIK_RU_REGEX = re.compile(r'\b04\d{7}\b')

# Кредитные/дебетовые карты (16-19 цифр)
CREDIT_CARD_REGEX = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4,7}\b')

# Мобильные телефоны РФ
PHONE_RU_REGEX = re.compile(r'(?:(?<=\s)|(?<=\b)|^)(?:\+7|8)[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b')

# Водительское удостоверение РФ (10 символов: 2 цифры + 2 цифры/буквы + 6 цифр)
DRIVER_LICENSE_RU_REGEX = re.compile(r'\b\d{2}\s*(?:\d{2}|[А-ЯA-Z]{2})\s*\d{6}\b', re.IGNORECASE)

# Полис ОМС единого образца (16 цифр) — только при наличии ключевых слов
OMS_RU_REGEX = re.compile(r'(?:ОМС|полис|страхов)[:\s№]*?(\d{16})', re.IGNORECASE)

# Адреса проживания РФ (город, улица, дом, квартира)
ADDRESS_RU_REGEX = re.compile(
    r'\b(?:г\.|пос\.|с\.|ст-ца|д\.|ул\.|пер\.|пр-кт|проспект|бул\.|бульвар|наб\.|набережная)\s+[А-ЯЁа-яёA-Za-z0-9\-]+'
    r'(?:\s*,\s*(?:г\.|пос\.|с\.|д\.|ул\.|пер\.|пр-кт|кв\.|корп\.|стр\.)\s*[А-ЯЁа-яёA-Za-z0-9\-]+)+',
    re.IGNORECASE
)

# --- ТРАНСПОРТНЫЕ СРЕДСТВА ---
VALID_CHARS = r'[АВЕКМНОРСТУХA-Z]' 

# 1. Частные и коммерческие легковые/грузовые (А 123 ВС 77 / A 123 BC 777)
VEHICLE_PRIVATE_RU_REGEX = re.compile(f'\\b{VALID_CHARS}\\s*\\d{{3}}\\s*{VALID_CHARS}{{2}}\\s*\\d{{2,3}}\\b', re.IGNORECASE)

# 2. Такси и Автобусы (АВ 123 77 - желтые номера)
VEHICLE_TAXI_BUS_RU_REGEX = re.compile(f'\\b{VALID_CHARS}{{2}}\\s*\\d{{3}}\\s*\\d{{2,3}}\\b', re.IGNORECASE)

# 3. Прицепы (АВ 1234 77)
VEHICLE_TRAILER_RU_REGEX = re.compile(f'\\b{VALID_CHARS}{{2}}\\s*\\d{{4}}\\s*\\d{{2,3}}\\b', re.IGNORECASE)

# 4. Мотоциклы (1234 АВ 77)
VEHICLE_MOTO_RU_REGEX = re.compile(f'\\b\\d{{4}}\\s*{VALID_CHARS}{{2}}\\s*\\d{{2,3}}\\b', re.IGNORECASE)

# VIN номер (17 символов, исключая I, O, Q)
VIN_REGEX = re.compile(r'\b[A-HJ-NPR-Z0-9]{17}\b', re.IGNORECASE)

# Объединенный список всех паттернов
RUSSIA_PATTERNS = {
    "PASSPORT_RU": PASSPORT_RU_REGEX,
    "INTL_PASSPORT_RU": INTL_PASSPORT_RU_REGEX,
    "INN_RU": INN_RU_REGEX,
    "SNILS_RU": SNILS_RU_REGEX,
    "OGRN_RU": OGRN_RU_REGEX,
    "KPP_RU": KPP_RU_REGEX,
    "BANK_ACCOUNT_RU": BANK_ACCOUNT_RU_REGEX,
    "BIK_RU": BIK_RU_REGEX,
    "CREDIT_CARD": CREDIT_CARD_REGEX,
    "PHONE_RU": PHONE_RU_REGEX,
    "DRIVER_LICENSE_RU": DRIVER_LICENSE_RU_REGEX,
    "OMS_RU": OMS_RU_REGEX,
    "ADDRESS_RU": ADDRESS_RU_REGEX,
    "VEHICLE_PRIVATE_RU": VEHICLE_PRIVATE_RU_REGEX,
    "VEHICLE_TAXI_BUS_RU": VEHICLE_TAXI_BUS_RU_REGEX,
    "VEHICLE_TRAILER_RU": VEHICLE_TRAILER_RU_REGEX,
    "VEHICLE_MOTO_RU": VEHICLE_MOTO_RU_REGEX,
    "VIN": VIN_REGEX
}
