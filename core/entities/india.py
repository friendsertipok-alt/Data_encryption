import re

# Индия: Регулярные выражения для поиска конфиденциальных данных

# Aadhaar (12 цифр, опциональные пробелы или дефисы)
AADHAAR_IN_REGEX = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

# PAN (5 букв, 4 цифры, 1 буква)
PAN_IN_REGEX = re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b', re.IGNORECASE)

# Voter ID / EPIC (3 буквы, 7 цифр)
VOTER_ID_IN_REGEX = re.compile(r'\b[A-Z]{3}\d{7}\b', re.IGNORECASE)

# Паспорт Индии (1 буква, 7 цифр)
PASSPORT_IN_REGEX = re.compile(r'\b[A-Z]\d{7}\b', re.IGNORECASE)

# GSTIN (15 символов: 2 цифры + PAN + 1 цифра + 1 буква/цифра + 1 буква/цифра)
GSTIN_IN_REGEX = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b', re.IGNORECASE)

# Driving License Индии (XX00YYYYNNNNNNN - State, RTO, Year, 7 digits)
DRIVING_LICENSE_IN_REGEX = re.compile(r'\b[A-Z]{2}[-\s]?\d{2}[-\s]?\d{4}[-\s]?\d{7}\b', re.IGNORECASE)

# Телефон Индии (+91)
PHONE_IN_REGEX = re.compile(r'\b(?:\+91|91)?[-\s]?\d{10}\b')

# IFSC Code (11 символов: 4 буквы, 0, 6 символов)
IFSC_IN_REGEX = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', re.IGNORECASE)

# --- ТРАНСПОРТНЫЕ СРЕДСТВА ---

# 1. Стандартные номера, коммерческие номера (такси/автобусы) имеют тот же буквенно-цифровой формат
# Формат: State(2 буквы) RTO(2 цифры) Series(1-3 буквы) Number(4 цифры)
# Например: MH 12 AB 1234
VEHICLE_STANDARD_IN_REGEX = re.compile(r'\b[A-Z]{2}[-\s]?\d{1,2}[-\s]?[A-Z]{1,3}[-\s]?\d{4}\b', re.IGNORECASE)

# 2. BH (Bharat) Серия: Year(2 цифры) BH Series(4 цифры) Letters(1-2 буквы)
# Например: 21 BH 1234 AB
VEHICLE_BH_IN_REGEX = re.compile(r'\b\d{2}[-\s]?BH[-\s]?\d{4}[-\s]?[A-Z]{1,2}\b', re.IGNORECASE)

# Объединенный список паттернов
INDIA_PATTERNS = {
    "AADHAAR_IN": AADHAAR_IN_REGEX,
    "PAN_IN": PAN_IN_REGEX,
    "VOTER_ID_IN": VOTER_ID_IN_REGEX,
    "PASSPORT_IN": PASSPORT_IN_REGEX,
    "GSTIN_IN": GSTIN_IN_REGEX,
    "DRIVING_LICENSE_IN": DRIVING_LICENSE_IN_REGEX,
    "PHONE_IN": PHONE_IN_REGEX,
    "IFSC_IN": IFSC_IN_REGEX,
    "VEHICLE_STANDARD_IN": VEHICLE_STANDARD_IN_REGEX,
    "VEHICLE_BH_IN": VEHICLE_BH_IN_REGEX
}
