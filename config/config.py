# config/config.py

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME', 'session')  # Значение по умолчанию 'session'

# Проверка наличия необходимых конфигураций
if not API_ID or not API_HASH:
    raise ValueError("API_ID и API_HASH должны быть установлены в .env файле.")
