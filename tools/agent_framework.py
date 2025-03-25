"""
Фреймворк для интеграции специализированных агентов с мастер-агентом.

Этот модуль предоставляет абстрактный интерфейс и функциональность для регистрации
и взаимодействия с различными специализированными агентами.
"""

import json
import logging
import importlib
from typing import Dict, List, Any, Optional, Callable

from tools.registry import register_tool

# Настройка логирования
logger = logging.getLogger(__name__)

# Глобальный реестр агентов
AGENTS_REGISTRY = {}

class AgentInfo:
    """Класс для хранения информации о зарегистрированном агенте."""
    
    def __init__(self, name: str, module_name: str, query_func: str, 
                 description: str = "", categories: List[str] = None):
        """
        Инициализирует информацию об агенте.
        
        Args:
            name: Имя агента
            module_name: Имя модуля агента для импорта
            query_func: Имя функции для выполнения запросов к агенту
            description: Описание агента
            categories: Список категорий, с которыми работает агент
        """
        self.name = name
        self.module_name = module_name
        self.query_func = query_func
        self.description = description
        self.categories = categories or []
        self.is_initialized = False
        self.module = None
        self.func = None
        self.error = None

def register_agent(name: str, module_name: str, query_func: str, 
                  description: str = "", categories: List[str] = None) -> bool:
    """
    Регистрирует специализированного агента в системе.
    
    Args:
        name: Имя агента
        module_name: Имя модуля агента для импорта
        query_func: Имя функции для выполнения запросов к агенту
        description: Описание агента
        categories: Список категорий, с которыми работает агент
        
    Returns:
        bool: True если регистрация успешна, иначе False
    """
    global AGENTS_REGISTRY
    
    if name in AGENTS_REGISTRY:
        logger.warning(f"Агент с именем '{name}' уже зарегистрирован")
        return False
    
    # Создаем информацию об агенте
    agent_info = AgentInfo(name, module_name, query_func, description, categories)
    
    # Пытаемся инициализировать агента
    try:
        # Импортируем модуль
        agent_info.module = importlib.import_module(module_name)
        
        # Проверяем наличие функции запроса
        if hasattr(agent_info.module, query_func):
            agent_info.func = getattr(agent_info.module, query_func)
            agent_info.is_initialized = True
            logger.info(f"Агент '{name}' успешно инициализирован")
        else:
            agent_info.error = f"Функция '{query_func}' не найдена в модуле '{module_name}'"
            logger.error(agent_info.error)
    except ImportError as e:
        agent_info.error = f"Не удалось импортировать модуль '{module_name}': {str(e)}"
        logger.error(agent_info.error)
    except Exception as e:
        agent_info.error = f"Ошибка при инициализации агента '{name}': {str(e)}"
        logger.error(agent_info.error)
    
    # Регистрируем агента
    AGENTS_REGISTRY[name] = agent_info
    return agent_info.is_initialized

def query_agent(agent_name: str, query: str) -> Dict[str, Any]:
    """
    Отправляет запрос указанному агенту.
    
    Args:
        agent_name: Имя агента
        query: Запрос для агента
        
    Returns:
        Dict: Результат выполнения запроса
    """
    global AGENTS_REGISTRY
    
    # Проверяем наличие агента в реестре
    if agent_name not in AGENTS_REGISTRY:
        return {
            "success": False,
            "error": f"Агент '{agent_name}' не зарегистрирован",
            "response": f"Агент '{agent_name}' не найден. Зарегистрированные агенты: {', '.join(AGENTS_REGISTRY.keys())}"
        }
    
    agent_info = AGENTS_REGISTRY[agent_name]
    
    # Проверяем инициализацию агента
    if not agent_info.is_initialized:
        return {
            "success": False,
            "error": agent_info.error or f"Агент '{agent_name}' не инициализирован",
            "response": f"Невозможно выполнить запрос к агенту '{agent_name}': {agent_info.error or 'агент не инициализирован'}"
        }
    
    # Выполняем запрос
    try:
        # Вызываем функцию запроса
        result = agent_info.func(query)
        
        # Если результат уже словарь, возвращаем его
        if isinstance(result, dict):
            return result
        
        # Если результат - строка JSON, парсим ее
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Если не можем распарсить как JSON, оборачиваем в словарь
                return {
                    "success": True,
                    "response": result
                }
        
        # Если неизвестный тип, оборачиваем в словарь
        return {
            "success": True,
            "response": str(result)
        }
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса к агенту '{agent_name}': {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "error": str(e),
            "response": f"Произошла ошибка при выполнении запроса к агенту '{agent_name}': {str(e)}"
        }

def get_agents_info() -> List[Dict[str, Any]]:
    """
    Возвращает информацию о всех зарегистрированных агентах.
    
    Returns:
        List: Список словарей с информацией об агентах
    """
    result = []
    
    for name, info in AGENTS_REGISTRY.items():
        agent_info = {
            "name": info.name,
            "description": info.description,
            "categories": info.categories,
            "is_initialized": info.is_initialized
        }
        
        if not info.is_initialized and info.error:
            agent_info["error"] = info.error
            
        result.append(agent_info)
    
    return result

def get_agent_by_category(category: str) -> Optional[str]:
    """
    Находит первого агента, который работает с указанной категорией.
    
    Args:
        category: Категория запроса
        
    Returns:
        Optional[str]: Имя агента или None, если агент не найден
    """
    for name, info in AGENTS_REGISTRY.items():
        if info.is_initialized and category.lower() in [c.lower() for c in info.categories]:
            return name
    return None

# Инструменты для мастер-агента

@register_tool
def get_available_agents() -> str:
    """
    Возвращает список всех доступных специализированных агентов.
    
    Returns:
        Информация об агентах в формате JSON
    """
    agents = get_agents_info()
    return json.dumps({
        "count": len(agents),
        "agents": agents
    }, indent=2)

@register_tool
def ask_specialized_agent(agent_name: str, query: str) -> str:
    """
    Отправляет запрос указанному специализированному агенту.
    
    Args:
        agent_name: Имя агента для обработки запроса
        query: Запрос для агента
        
    Returns:
        Ответ агента в формате JSON
    """
    result = query_agent(agent_name, query)
    return json.dumps(result, indent=2)

# Регистрируем инвестиционного агента при импорте модуля
register_agent(
    name="investment_agent",
    module_name="investment_agent",
    query_func="query",
    description="Инвестиционный агент для анализа финансовых данных",
    categories=[
        "инвестиции", 
        "финансы", 
        "акции", 
        "отчеты", 
        "портфель"
    ]
)