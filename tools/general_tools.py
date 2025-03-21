"""
Общие инструменты для взаимодействия с языковыми моделями.

Этот модуль содержит инструменты для прямого взаимодействия с моделями OpenAI.
"""

import json
import logging
from typing import Optional, List, Dict, Any

from tools.registry import register_tool
from config import OPENAI_API_KEY

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    logger.error("OpenAI package not installed. Please install it with pip install openai")
    raise

@register_tool
def chat_with_model(query: str, model: Optional[str] = None, temperature: Optional[float] = None) -> str:
    """
    Отправляет запрос непосредственно языковой модели и возвращает её ответ.
    
    Args:
        query: Запрос пользователя
        model: Модель для использования (по умолчанию gpt-4o)
        temperature: Температура генерации (от 0 до 1, по умолчанию 0.7)
    
    Returns:
        JSON-строка с ответом модели
    """
    try:
        # Устанавливаем значения по умолчанию
        model = "gpt-4o" if model is None else model
        temperature = 0.7 if temperature is None else temperature
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Вы - полезный ассистент, который дает точные и информативные ответы."},
                {"role": "user", "content": query}
            ],
            temperature=temperature
        )
        
        result = {
            "model": model,
            "response": response.choices[0].message.content,
            "usage": {
                "total_tokens": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"Error communicating with OpenAI API: {str(e)}")
        error_result = {
            "error": str(e),
            "model": model,
            "query": query,
            "response": f"Произошла ошибка при обращении к API OpenAI: {str(e)}. Пожалуйста, проверьте API-ключ и подключение к интернету."
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)