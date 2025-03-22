"""
Конфигурация проекта zAI.
"""

import os

# API ключи
# Проверяем наличие API ключа в переменных окружения, иначе используем ключ из файла
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")

# Настройки модели
DEFAULT_MODEL = "gpt-4o"  # или другая модель
DEFAULT_TEMPERATURE = 0.2

# Настройки веб-сервера
PORT = 5000
HOST = '0.0.0.0'
DEBUG = True

# Пути к ресурсам
RESOURCES_PATH = "./resources"

# Логирование
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Добавим в config.py
SERPAPI_KEY = "3f8be09f2b1d53774061335e1303b9494d5c4b79941ece65a531b010f051b087"