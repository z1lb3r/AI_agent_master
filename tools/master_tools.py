"""
Инструменты для мастер-агента системы zAI.

Этот модуль содержит инструменты, специфичные для мастер-агента.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

from tools.registry import register_tool, get_all_tools, get_tool_info

# Настройка логирования
logger = logging.getLogger(__name__)

@register_tool
def get_available_tools(category: Optional[str] = None) -> str:
    """
    Получает список всех доступных инструментов в системе.
    
    Args:
        category: Опциональная категория для фильтрации инструментов
    
    Returns:
        JSON-строка со списком инструментов и их описаниями
    """
    tools = get_tool_info()
    
    # Фильтрация по категории, если указана
    if category:
        tools = [tool for tool in tools if category.lower() in tool['name'].lower()]
    
    result = {
        "count": len(tools),
        "tools": tools
    }
    
    return json.dumps(result, indent=2)

@register_tool
def get_system_status() -> str:
    """
    Получает текущий статус системы zAI.
    
    Returns:
        JSON-строка с информацией о статусе системы
    """
    # В реальной системе здесь будет более сложная логика
    # для проверки статуса различных компонентов
    
    now = datetime.now()
    
    status = {
        "status": "online",
        "timestamp": now.isoformat(),
        "components": {
            "master_agent": "active",
            "investment_agent": "active",
            "tools_registry": {
                "status": "active",
                "tool_count": len(get_all_tools())
            },
            "web_interface": "active"
        },
        "system_load": {
            "cpu": "25%",
            "memory": "40%"
        }
    }
    
    return json.dumps(status, indent=2)


@register_tool
def classify_user_query(query: str) -> str:
    """
    Классифицирует запрос пользователя для определения нужного специализированного агента.
    
    Args:
        query: Запрос пользователя для классификации
    
    Returns:
        JSON-строка с результатами классификации
    """
    # В реальной системе здесь будет более сложная логика,
    # возможно с использованием NLP или ML
    
    keywords = {
        "investment": ["инвестиции", "акции", "портфель", "торговля", "биржа", "финансы", "отчет", "сделка", 
                      "доходность", "дивиденды", "фонд", "трейдинг", "опцион", "фьючерс"],
        "general": ["помощь", "информация", "вопрос", "объяснение", "рассказать", "посоветуй", "мнение", 
                    "что такое", "как сделать", "почему", "когда", "где", "кто", "зачем"],
        "direct_model": ["думаешь", "считаешь", "напиши", "сгенерируй", "придумай", "сочини", "создай текст", 
                         "твое мнение", "твоя оценка", "творческий", "креативный", "история", "стихотворение"],
        "system": ["статус", "инструменты", "функции", "возможности", "агенты", "система", "настройки"]
    }
    
    query_lower = query.lower()
    scores = {}
    
    for category, words in keywords.items():
        score = sum(1 for word in words if word in query_lower)
        scores[category] = score
    
    # Определяем категорию с наивысшим счетом
    max_category = max(scores, key=scores.get)
    max_score = scores[max_category]
    
    # Если счет слишком низкий, используем direct_model для обращения к GPT-4o
    if max_score == 0:
        max_category = "direct_model"
    
    # Рекомендуемый инструмент на основе классификации
    recommended_tool = None
    if max_category == "direct_model" or max_category == "general":
        recommended_tool = "chat_with_model"
    elif max_category == "system":
        if "статус" in query_lower:
            recommended_tool = "get_system_status"
        elif "инструменты" in query_lower or "функции" in query_lower:
            recommended_tool = "get_available_tools"
        else:
            recommended_tool = "lookup_information"
    elif max_category == "investment":
        # Здесь будет логика выбора инструмента инвестиционного агента
        recommended_tool = "Инвестиционный инструмент (будет определен позже)"
    
    result = {
        "query": query,
        "classification": max_category,
        "confidence": min(max_score / 3, 1.0),  # Нормализуем уверенность
        "scores": scores,
        "recommended_tool": recommended_tool
    }
    
    return json.dumps(result, indent=2)


@register_tool
def lookup_information(topic: str) -> str:
    """
    Ищет информацию по указанной теме.
    
    Args:
        topic: Тема для поиска информации
    
    Returns:
        JSON-строка с найденной информацией
    """
    # В реальной системе здесь будет интеграция с базой знаний или API
    
    # Пример данных
    knowledge_base = {
        "zai": {
            "title": "zAI",
            "description": "zAI - это система мастер-агента, координирующая работу специализированных AI-агентов.",
            "capabilities": ["Координация агентов", "Маршрутизация запросов", "Управление инструментами"]
        },
        "master_agent": {
            "title": "Мастер-агент",
            "description": "Мастер-агент - это центральный компонент системы zAI, который обрабатывает запросы и делегирует задачи.",
            "responsibilities": ["Анализ запросов", "Выбор инструментов", "Координация работы подчиненных агентов"]
        },
        "investment": {
            "title": "Инвестиционный анализ",
            "description": "zAI предоставляет возможности для анализа инвестиций через специализированного агента.",
            "features": ["Анализ отчетов", "Управление портфелем", "Мониторинг рынка"]
        }
    }
    
    topic_lower = topic.lower()
    results = {}
    
    for key, data in knowledge_base.items():
        if topic_lower in key or any(topic_lower in str(value).lower() for value in data.values()):
            results[key] = data
    
    if not results:
        return json.dumps({
            "topic": topic,
            "found": False,
            "message": "Информация по указанной теме не найдена."
        })
    
    return json.dumps({
        "topic": topic,
        "found": True,
        "results": results
    }, indent=2)