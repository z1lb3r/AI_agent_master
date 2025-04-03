"""
Инструменты для взаимодействия с базой данных телеграм-бота.
"""

import json
import logging
import requests
from typing import Optional, Dict

from tools.registry import register_tool

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация для доступа к API бота
BOT_DB_API_URL = "http://194.87.250.225:5001/api"  
BOT_DB_API_KEY = "yNkP8Qz2XbTr5Vw7JsLm3GfHd9AeC6B1"  # API-ключ

@register_tool
def query_bot_database(query: str) -> str:
    """
    Выполняет SELECT-запрос к базе данных телеграм-бота.
    
    Args:
        query: SQL-запрос (только SELECT)
    
    Returns:
        JSON-строка с результатами запроса
    """
    if not query.strip().upper().startswith('SELECT'):
        return json.dumps({
            "error": "Only SELECT queries are allowed with this function",
            "results": []
        }, ensure_ascii=False)
    
    try:
        response = requests.post(
            f"{BOT_DB_API_URL}/query",
            json={"query": query, "params": []},
            headers={"X-API-Key": BOT_DB_API_KEY}
        )
        
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"Error querying bot database: {str(e)}")
        return json.dumps({
            "error": str(e),
            "results": []
        }, ensure_ascii=False)

@register_tool
def execute_bot_database(query: str) -> str:
    """
    Выполняет модифицирующий запрос (INSERT, UPDATE, DELETE) к базе данных телеграм-бота.
    
    Args:
        query: SQL-запрос (INSERT, UPDATE, DELETE)
    
    Returns:
        JSON-строка с результатом выполнения запроса
    """
    if query.strip().upper().startswith('SELECT'):
        return json.dumps({
            "error": "SELECT queries should use query_bot_database function",
            "success": False
        }, ensure_ascii=False)
    
    try:
        response = requests.post(
            f"{BOT_DB_API_URL}/execute",
            json={"query": query, "params": []},
            headers={"X-API-Key": BOT_DB_API_KEY}
        )
        
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"Error executing command on bot database: {str(e)}")
        return json.dumps({
            "error": str(e),
            "success": False
        }, ensure_ascii=False)

@register_tool
def get_bot_database_schema() -> str:
    """
    Получает схему базы данных телеграм-бота.
    
    Returns:
        JSON-строка со схемой базы данных
    """
    try:
        response = requests.get(
            f"{BOT_DB_API_URL}/schema",
            headers={"X-API-Key": BOT_DB_API_KEY}
        )
        
        response.raise_for_status()
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"Error getting bot database schema: {str(e)}")
        return json.dumps({
            "error": str(e),
            "schema": {}
        }, ensure_ascii=False)

# Прямые функции для тестирования (без декораторов)
def direct_query_bot_database(query: str):
    """
    Прямая функция для тестирования запросов.
    """
    try:
        response = requests.post(
            f"{BOT_DB_API_URL}/query",
            json={"query": query, "params": []},
            headers={"X-API-Key": BOT_DB_API_KEY}
        )
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error in direct query: {str(e)}")
        return {"error": str(e)}

def direct_get_schema():
    """
    Прямая функция для тестирования получения схемы.
    """
    try:
        response = requests.get(
            f"{BOT_DB_API_URL}/schema",
            headers={"X-API-Key": BOT_DB_API_KEY}
        )
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error in direct schema query: {str(e)}")
        return {"error": str(e)}