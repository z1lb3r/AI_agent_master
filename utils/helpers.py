"""
Вспомогательные функции для системы zAI.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def format_json_response(data: Dict) -> str:
    """
    Форматирует словарь в красивую JSON-строку.
    
    Args:
        data: Словарь для форматирования
        
    Returns:
        Отформатированная JSON-строка
    """
    return json.dumps(data, ensure_ascii=False, indent=2)

def log_event(event_type: str, details: Optional[Dict] = None) -> None:
    """
    Логирует событие с деталями.
    
    Args:
        event_type: Тип события
        details: Детали события (опционально)
    """
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    logger.info(f"Event: {event_type} | {format_json_response(log_data)}")

def extract_parameters_from_query(query: str, parameter_names: List[str]) -> Dict[str, Any]:
    """
    Извлекает параметры из запроса пользователя.
    
    Args:
        query: Запрос пользователя
        parameter_names: Список имен параметров для извлечения
        
    Returns:
        Словарь с извлеченными параметрами
    """
    # Это очень примитивная реализация для демонстрации
    # В реальной системе здесь был бы более сложный алгоритм извлечения параметров
    
    result = {}
    query_lower = query.lower()
    
    for param in parameter_names:
        param_lower = param.lower()
        if param_lower in query_lower:
            # Пытаемся найти значение после имени параметра
            parts = query_lower.split(param_lower)
            if len(parts) > 1:
                # Берем первые слова после имени параметра до следующего знака препинания или конца строки
                value_part = parts[1].strip()
                # Ограничиваем до первого знака препинания или пробела
                for char in '.,;:!?"\'()[]{}':
                    value_part = value_part.split(char)[0]
                
                # Убираем начальные пробелы
                value_part = value_part.strip()
                
                if value_part:
                    result[param] = value_part
    
    return result

def safe_parse_json(json_str: str) -> Dict:
    """
    Безопасно парсит JSON-строку.
    
    Args:
        json_str: JSON-строка для парсинга
        
    Returns:
        Словарь с данными из JSON или пустой словарь в случае ошибки
    """
    try:
        if not json_str or not isinstance(json_str, str):
            return {}
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return {}