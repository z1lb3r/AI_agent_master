"""
Инструменты для поиска в интернете.

Этот модуль содержит инструменты для поиска информации в сети через различные API.
"""

import json
import logging
import requests
from typing import Optional

from tools.registry import register_tool
from config import SERPAPI_KEY

# Настройка логирования
logger = logging.getLogger(__name__)

@register_tool
def search_google(query: str, num_results: int = None) -> str:
    """
    Выполняет поиск в Google и возвращает результаты.
    
    Args:
        query: Поисковый запрос
        num_results: Количество результатов для возврата (не обязательно)
    
    Returns:
        JSON-строка с результатами поиска
    """
    try:
        # Установка значения по умолчанию внутри функции, а не в сигнатуре
        if num_results is None:
            num_results = 5
        
        # Ограничиваем количество результатов разумным пределом
        if num_results > 10:
            num_results = 10
        
        # Формируем URL запроса к SerpAPI
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results
        }
        
        url = "https://serpapi.com/search"
        
        # Выполняем запрос
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        
        # Получаем результаты
        results = response.json()
        
        # Извлекаем только нужные данные для более компактного ответа
        simplified_results = {
            "query": query,
            "organic_results": []
        }
        
        # Добавляем прямой ответ, если есть
        if "answer_box" in results:
            simplified_results["direct_answer"] = results["answer_box"]
        
        # Добавляем органические результаты
        if "organic_results" in results:
            for result in results["organic_results"][:num_results]:
                simplified_results["organic_results"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        # Добавляем информацию из knowledge graph, если есть
        if "knowledge_graph" in results:
            simplified_results["knowledge_graph"] = {
                "title": results["knowledge_graph"].get("title", ""),
                "description": results["knowledge_graph"].get("description", "")
            }
        
        return json.dumps(simplified_results, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"Error during Google search: {str(e)}")
        error_result = {
            "error": str(e),
            "query": query,
            "message": "Не удалось выполнить поиск в Google. Пожалуйста, проверьте подключение к интернету и API-ключ."
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)