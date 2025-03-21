"""
Точка входа для запуска веб-интерфейса zAI.

Этот скрипт запускает веб-сервер Flask для взаимодействия с мастер-агентом через браузер.
"""

import logging
import os
import sys

# Добавляем родительский каталог в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import run_server
from config import LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """
    Настраивает систему логирования.
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """
    Основная функция для запуска веб-сервера.
    """
    # Настраиваем логирование
    setup_logging()
    logger = logging.getLogger("zai_web")
    
    logger.info("Запуск веб-интерфейса zAI...")
    
    try:
        # Запускаем веб-сервер
        run_server()
    except Exception as e:
        logger.exception("Ошибка при запуске веб-сервера")
        print(f"\nОшибка: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()