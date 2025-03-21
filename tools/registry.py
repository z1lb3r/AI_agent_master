"""
Реестр инструментов для системы zAI.

Этот модуль реализует центральный реестр инструментов, который позволяет 
регистрировать и обнаруживать функции, доступные для использования агентами.
"""

import inspect
import logging
from typing import List, Callable, Any, Dict
from agents import function_tool  # Изменяем импорт с my_agents на agents

# Настройка логирования
logger = logging.getLogger(__name__)

# Глобальный реестр инструментов
TOOL_REGISTRY = []

def register_tool(func: Callable) -> Callable:
    """
    Декоратор для регистрации функции как инструмента в реестре.
    
    Args:
        func: Функция для регистрации
        
    Returns:
        Функция-инструмент, обернутая в function_tool
    """
    # Создаем инструмент с помощью SDK
    tool_func = function_tool(func)
    
    # Регистрируем в глобальном реестре
    if tool_func not in TOOL_REGISTRY:
        TOOL_REGISTRY.append(tool_func)
        logger.info(f"Инструмент зарегистрирован: {func.__name__}")
    
    return tool_func

def get_all_tools() -> List:
    """
    Возвращает все зарегистрированные инструменты.
    
    Returns:
        Список всех зарегистрированных инструментов
    """
    return TOOL_REGISTRY

def get_tool_info() -> List[Dict]:
    """
    Возвращает информацию о всех инструментах в удобочитаемом формате.
    
    Returns:
        Список словарей с информацией об инструментах
    """
    tools_info = []
    
    for tool in TOOL_REGISTRY:
        tool_info = {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters if hasattr(tool, "parameters") else {}
        }
        tools_info.append(tool_info)
    
    return tools_info

def discover_tools_from_module(module: Any) -> None:
    """
    Обнаруживает и регистрирует функции-инструменты из указанного модуля.
    
    Args:
        module: Модуль Python для сканирования
    """
    for name, item in inspect.getmembers(module, inspect.isfunction):
        # Проверяем, что функция имеет документацию и аннотации типов
        if inspect.getdoc(item) and hasattr(item, "__annotations__"):
            # Регистрируем функцию как инструмент
            register_tool(item)
            logger.info(f"Инструмент обнаружен и зарегистрирован из модуля: {name}")

def get_tools_by_prefix(prefix: str) -> List:
    """
    Возвращает инструменты, имена которых начинаются с указанного префикса.
    
    Args:
        prefix: Префикс для фильтрации инструментов
        
    Returns:
        Список инструментов с указанным префиксом
    """
    return [tool for tool in TOOL_REGISTRY if tool.name.startswith(prefix)]

def get_tools_by_category(category: str) -> List:
    """
    Возвращает инструменты по категории (предполагается, что категория указана в метаданных).
    
    Args:
        category: Категория для фильтрации инструментов
        
    Returns:
        Список инструментов в указанной категории
    """
    return [tool for tool in TOOL_REGISTRY if getattr(tool, "category", None) == category]