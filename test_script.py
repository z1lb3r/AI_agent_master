#!/usr/bin/env python
"""
Скрипт для тестирования прямой интеграции инвестиционного агента с мастер-агентом.

Этот скрипт проверяет правильность импорта и работы инвестиционного агента
без использования subprocess.
"""

import sys
import os
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("integration_test")

def test_direct_import():
    """
    Тестирует прямой импорт инвестиционного агента как модуля.
    """
    logger.info("Тестирование прямого импорта инвестиционного агента...")
    
    try:
        # Импорт модуля инвестиционного агента
        import investment_agent
        
        # Проверка наличия основных функций
        assert hasattr(investment_agent, 'query'), "Функция 'query' не найдена"
        assert hasattr(investment_agent, 'get_agent'), "Функция 'get_agent' не найдена"
        assert hasattr(investment_agent, 'initialize_tools'), "Функция 'initialize_tools' не найдена"
        
        logger.info("Импорт успешен. Функции API найдены.")
        
        # Тестирование запроса
        test_query = "Что такое P/E ratio?"
        logger.info(f"Отправка тестового запроса: '{test_query}'")
        
        result = investment_agent.query(test_query)
        
        # Проверка структуры ответа
        assert isinstance(result, dict), "Результат должен быть словарем"
        assert "success" in result, "Поле 'success' не найдено в результате"
        assert "response" in result, "Поле 'response' не найдено в результате"
        
        logger.info(f"Запрос успешно обработан. Получен ответ (первые 100 символов): {result['response'][:100]}")
        return True
        
    except ImportError as e:
        logger.error(f"Ошибка импорта: {str(e)}")
        logger.error("Убедитесь, что пакет investment_agent установлен с помощью 'pip install -e /path/to/investment_agent'")
        return False
    except AssertionError as e:
        logger.error(f"Ошибка проверки: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_agent_framework():
    """
    Тестирует интеграцию через agent_framework.
    """
    logger.info("Тестирование интеграции через agent_framework...")
    
    try:
        # Импорт модуля фреймворка агентов
        from tools.agent_framework import get_agents_info, query_agent
        
        # Получение информации о зарегистрированных агентах
        agents_info = get_agents_info()
        
        # Проверка наличия инвестиционного агента
        assert any(agent['name'] == 'investment_agent' for agent in agents_info), "Инвестиционный агент не зарегистрирован"
        
        # Получение информации об инвестиционном агенте
        investment_agent_info = next(agent for agent in agents_info if agent['name'] == 'investment_agent')
        
        # Проверка инициализации
        assert investment_agent_info['is_initialized'], f"Инвестиционный агент не инициализирован. Ошибка: {investment_agent_info.get('error', 'Неизвестная ошибка')}"
        
        logger.info("Инвестиционный агент успешно зарегистрирован и инициализирован в фреймворке.")
        
        # Тестирование запроса через фреймворк
        test_query = "Как рассчитывается EBITDA?"
        logger.info(f"Отправка тестового запроса через фреймворк: '{test_query}'")
        
        result = query_agent('investment_agent', test_query)
        
        # Проверка структуры ответа
        assert isinstance(result, dict), "Результат должен быть словарем"
        assert "success" in result, "Поле 'success' не найдено в результате"
        assert "response" in result, "Поле 'response' не найдено в результате"
        
        logger.info(f"Запрос через фреймворк успешно обработан. Получен ответ (первые 100 символов): {result['response'][:100]}")
        return True
        
    except ImportError as e:
        logger.error(f"Ошибка импорта: {str(e)}")
        logger.error("Убедитесь, что модуль tools.agent_framework доступен")
        return False
    except AssertionError as e:
        logger.error(f"Ошибка проверки: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """
    Основная функция тестирования.
    """
    logger.info("Начало тестирования интеграции инвестиционного агента...")
    
    # Тестирование прямого импорта
    direct_import_success = test_direct_import()
    
    # Тестирование через фреймворк
    try:
        framework_success = test_agent_framework()
    except Exception:
        framework_success = False
        logger.error("Тестирование через фреймворк не удалось. Возможно, модуль не установлен.")
    
    # Вывод результатов
    logger.info("\n" + "=" * 60)
    logger.info("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    logger.info("=" * 60)
    logger.info(f"Прямой импорт: {'УСПЕШНО' if direct_import_success else 'ОШИБКА'}")
    logger.info(f"Через фреймворк: {'УСПЕШНО' if framework_success else 'ОШИБКА'}")
    logger.info("=" * 60)
    
    if direct_import_success and framework_success:
        logger.info("ИНТЕГРАЦИЯ УСПЕШНА! Все тесты пройдены.")
        return 0
    else:
        logger.error("ОШИБКА ИНТЕГРАЦИИ! Некоторые тесты не пройдены.")
        return 1

if __name__ == "__main__":
    sys.exit(main())