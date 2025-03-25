"""
Модуль для инициализации интеграции инвестиционного агента с мастер-агентом.

Этот модуль должен быть импортирован при начальной настройке системы.
Он проверяет наличие необходимых зависимостей и инициализирует пути.
"""

import sys
import os
import logging
import importlib
from typing import Dict, List, Optional

# Настройка логирования
logger = logging.getLogger(__name__)

# Импортируем менеджер путей
from tools.shared_paths import path_manager

# Проверяем наличие директории
if not os.path.exists(path_manager.investment_agent_dir):
    logger.error(f"Директория инвестиционного агента не найдена: {path_manager.investment_agent_dir}")
    raise ImportError(f"Директория инвестиционного агента не найдена: {path_manager.investment_agent_dir}")

# Добавляем путь к инвестиционному агенту в sys.path
if path_manager.investment_agent_dir not in sys.path:
    sys.path.append(path_manager.investment_agent_dir)
    logger.info(f"Добавлен путь к инвестиционному агенту: {path_manager.investment_agent_dir}")

# Список необходимых зависимостей инвестиционного агента
REQUIRED_DEPENDENCIES = [
    "agents",  # OpenAI Agents SDK
    "requests",
    "sqlite3",
]

# Список необходимых PDF-библиотек (проверяем наличие хотя бы одной)
PDF_LIBRARIES = [
    "fitz",     # PyMuPDF
    "pdfminer", # PDFMiner
    "PyPDF2"    # PyPDF2
]

def check_dependencies() -> Dict[str, bool]:
    """
    Проверяет наличие необходимых зависимостей для работы инвестиционного агента.
    
    Returns:
        Словарь с результатами проверки зависимостей
    """
    results = {}
    
    # Проверяем основные зависимости
    for dependency in REQUIRED_DEPENDENCIES:
        try:
            importlib.import_module(dependency)
            results[dependency] = True
        except ImportError:
            results[dependency] = False
            logger.warning(f"Зависимость не найдена: {dependency}")
    
    # Проверяем наличие хотя бы одной PDF-библиотеки
    pdf_library_available = False
    for library in PDF_LIBRARIES:
        try:
            importlib.import_module(library)
            results[library] = True
            pdf_library_available = True
        except ImportError:
            results[library] = False
    
    if not pdf_library_available:
        logger.warning("Не найдена ни одна PDF-библиотека. Функции анализа PDF будут недоступны.")
    
    return results

def init_investment_integration() -> bool:
    """
    Инициализирует интеграцию инвестиционного агента с мастер-агентом.
    
    Returns:
        True, если инициализация прошла успешно, иначе False
    """
    try:
        # Проверяем зависимости
        dependencies = check_dependencies()
        if not all(dependencies.get(dep, False) for dep in REQUIRED_DEPENDENCIES):
            logger.error("Не все необходимые зависимости доступны для работы инвестиционного агента")
            return False
        
        # Проверяем наличие core-модулей инвестиционного агента
        try:
            # Импортируем ключевые модули
            import agent
            from agent import get_agent
            
            # Проверяем наличие механизмов регистрации инструментов
            import tools.registry_af
            
            # Пытаемся импортировать модули инструментов инвестиционного агента
            import tools.sec_downloader_af
            import tools.pdf_analyzer_af
            import tools.trade_tracker_af
            
            logger.info("Интеграция инвестиционного агента инициализирована успешно")
            return True
            
        except ImportError as e:
            logger.error(f"Не удалось импортировать ключевые модули инвестиционного агента: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при инициализации интеграции инвестиционного агента: {str(e)}")
        return False

# Выполняем инициализацию
integration_success = init_investment_integration()