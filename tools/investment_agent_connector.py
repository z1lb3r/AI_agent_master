"""
Коннектор для прямого взаимодействия с инвестиционным агентом.

Этот модуль реализует интерфейс для взаимодействия мастер-агента с инвестиционным агентом
через прямой импорт вместо subprocess.
"""

import json
import logging
from typing import Dict, Any, Optional

from tools.registry import register_tool

# Настройка логирования
logger = logging.getLogger(__name__)

# Переменная для хранения состояния инициализации
_investment_agent_initialized = False

def _ensure_investment_agent():
    """
    Проверяет и обеспечивает инициализацию инвестиционного агента.
    
    Returns:
        bool: True если инициализация успешна, иначе False
    """
    global _investment_agent_initialized
    
    if _investment_agent_initialized:
        return True
    
    try:
        # Импортируем модуль инвестиционного агента
        import investment_agent
        
        # Проверяем доступность основных функций
        if not hasattr(investment_agent, 'query'):
            logger.error("Модуль investment_agent не имеет функции 'query'")
            return False
        
        logger.info("Инвестиционный агент успешно инициализирован")
        _investment_agent_initialized = True
        return True
        
    except ImportError as e:
        logger.error(f"Не удалось импортировать модуль investment_agent: {str(e)}")
        logger.error("Убедитесь, что пакет установлен с помощью 'pip install -e /path/to/investment_agent'")
        return False
    except Exception as e:
        logger.error(f"Ошибка при инициализации инвестиционного агента: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

@register_tool
def ask_investment_agent(query: str) -> str:
    """
    Напрямую отправляет запрос инвестиционному агенту и возвращает его ответ.
    
    Args:
        query: Запрос для инвестиционного агента
    
    Returns:
        Ответ инвестиционного агента в формате JSON
    """
    logger.info(f"Отправка запроса инвестиционному агенту: {query}")
    
    # Проверяем инициализацию агента
    if not _ensure_investment_agent():
        return json.dumps({
            "success": False,
            "response": "Не удалось инициализировать инвестиционного агента. Проверьте логи для получения дополнительной информации."
        })
    
    try:
        # Импортируем и вызываем функцию запроса
        import investment_agent
        result = investment_agent.query(query)
        
        # Логируем успешный ответ
        logger.info(f"Получен ответ от инвестиционного агента (первые 100 символов): {result.get('response', '')[:100]}")
        
        # Возвращаем результат
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Ошибка при взаимодействии с инвестиционным агентом: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return json.dumps({
            "success": False,
            "response": f"Произошла ошибка при обработке запроса инвестиционным агентом: {str(e)}"
        })

@register_tool
def get_investment_agent_status() -> str:
    """
    Возвращает статус инвестиционного агента.
    
    Returns:
        Статус инвестиционного агента в формате JSON
    """
    status = {
        "initialized": _investment_agent_initialized,
        "available": _ensure_investment_agent()
    }
    
    # Если агент доступен, добавляем информацию о его инструментах
    if status["available"]:
        try:
            import investment_agent
            from investment_agent.tools.registry import get_all_tools
            
            tools = get_all_tools()
            status["tools_count"] = len(tools)
            status["tools"] = [getattr(tool, 'name', str(tool)) for tool in tools]
        except Exception as e:
            status["error"] = str(e)
    
    return json.dumps(status, indent=2)

# Инициализируем агента при импорте модуля
_ensure_investment_agent()