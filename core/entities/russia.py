import re

# Россия: Регулярные выражения для поиска конфиденциальных данных

# Паспорт РФ (серия 4 цифры + опциональный №/N/-/номер + 6 цифр номера)
PASSPORT_RU_REGEX = re.compile(r'\b\d{2}\s*\d{2}\s*(?:№|N|-|номер)?\s*\d{6}\b', re.IGNORECASE)

# Загранпаспорт РФ (2 цифры + 7 цифр)
INTL_PASSPORT_RU_REGEX = re.compile(r'\b\d{2}\s*\d{7}\b')

# ИНН (10 или 12 цифр) — с ключевым словом для предотвращения ложных срабатываний
INN_RU_REGEX = re.compile(
    r'(?:(?<=ИНН\s)|(?<=ИНН:\s)|(?<=ИНН:)|(?<=ИНН\s№\s)|(?<=ИНН\s№)|(?<=ИНН№)|'
    r'(?<=инн\s)|(?<=инн:\s)|(?<=инн:)|(?<=INN\s)|(?<=INN:\s)|(?<=INN:)|'
    r'(?<=Инн\s)|(?<=Инн:\s))\d{10}(?:\d{2})?\b',
    re.IGNORECASE
)

# СНИЛС (123-456-789 12, 123-456-789-12, 123 456 789 12 или 11 цифр с ключевым словом)
SNILS_RU_REGEX = re.compile(
    r'(?:(?<=\bСНИЛС\s)|(?<=\bСНИЛС:\s)|(?<=\bСНИЛС:)|(?<=\bснилс\s)|(?<=\bснилс:\s)|(?<=\bснилс:))\d{11}\b|'
    r'\b\d{3}[-\s.]?\d{3}[-\s.]?\d{3}[-\s.]?\d{2}\b',
    re.IGNORECASE
)

# ОГРН (13 цифр) и ОГРНИП (15 цифр)
OGRN_RU_REGEX = re.compile(r'\b\d{13}(?:\d{2})?\b')

# КПП (9 цифр) — с ключевым словом КПП
KPP_RU_REGEX = re.compile(
    r'(?:(?<=КПП\s)|(?<=КПП:\s)|(?<=КПП:)|(?<=кпп\s)|(?<=кпп:\s)|(?<=кпп:))\d{9}\b',
    re.IGNORECASE
)

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

# Полис ОМС единого образца (16 цифр)
OMS_RU_REGEX = re.compile(
    r'(?:(?<=\bОМС\s)|(?<=\bОМС:\s)|(?<=\bОМС:)|(?<=\bполис\s)|(?<=\bполис:\s)|(?<=\bполис:))\d{16}\b|'
    r'(?:ОМС|полис|страхов)[:\s№]*?(\d{16})',
    re.IGNORECASE
)

# Адреса проживания РФ (город, улица, дом, квартира, область, район)
_address_prefix = r'(?:г\.|город|пос\.|поселок|посёлок|с\.|село|ст-ца|станица|д\.|деревня|обл\.|область|р-н|район|мкр\.|микрорайон|ул\.|улица|пер\.|переулок|пр-кт|проспект|бул\.|бульвар|наб\.|набережная)'
_address_part = r'(?:г\.|город|пос\.|поселок|посёлок|с\.|село|д\.|деревня|дом|ул\.|улица|пер\.|переулок|пр-кт|проспект|бул\.|бульвар|наб\.|набережная|кв\.|квартира|корп\.|корпус|стр\.|строение|обл\.|область|р-н|район|мкр\.|микрорайон)'

ADDRESS_RU_REGEX = re.compile(
    rf'\b(?:{_address_prefix}\s+[А-ЯЁа-яёA-Za-z0-9\-\.]+'
    rf'(?:\s*,\s*{_address_part}?\s*[А-ЯЁа-яёA-Za-z0-9\-\.]+)+)',
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
