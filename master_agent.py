"""
Определение мастер-агента для системы zAI.

Этот модуль определяет мастер-агента, который координирует работу
специализированных агентов и инструментов.
"""

import logging
import json
import asyncio
from typing import Optional, List, Dict, Any

from agents import Agent, Runner, RunConfig, set_default_openai_key, ModelSettings
from utils.helpers import safe_parse_json

from config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from prompts.master_prompt import MASTER_PROMPT
from tools.registry import get_all_tools

# Импортируем инструменты для регистрации
from tools.master_tools import get_available_tools, get_system_status, classify_user_query, lookup_information
from tools.general_tools import chat_with_model

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zai_master_agent")

# Устанавливаем API-ключ
set_default_openai_key(OPENAI_API_KEY)

class MasterAgent:
    """
    Мастер-агент системы zAI, координирующий работу специализированных агентов и инструментов.
    """
    
    def __init__(self):
        """
        Инициализация мастер-агента.
        """
        # Создаем экземпляр агента OpenAI
        self.agent = Agent(
            name="zAI Master Agent",
            instructions=MASTER_PROMPT,
            model=DEFAULT_MODEL,
            model_settings=ModelSettings(temperature=DEFAULT_TEMPERATURE),
            tools=get_all_tools()  # Получаем все инструменты из реестра
        )
        
        logger.info(f"MasterAgent initialized with {len(get_all_tools())} tools")
    
    def update_tools(self):
        """
        Обновляет набор инструментов мастер-агента.
        """
        self.agent.tools = get_all_tools()
        logger.info(f"MasterAgent tools updated. New tool count: {len(self.agent.tools)}")
    
    def process_query(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Обрабатывает запрос пользователя.
        
        Args:
            query: Запрос пользователя
            conversation_history: История разговора (опционально)
            
        Returns:
            Ответ мастер-агента
        """
        logger.info(f"Processing query: {query}")
        
        # Создаем конфигурацию для запуска
        run_config = RunConfig(
            workflow_name="zAI Master Agent Workflow",
        )
        
        try:
            # Обеспечиваем наличие event loop в текущем потоке
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # Если event loop не доступен в текущем потоке, создаем новый
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Если есть история разговора, используем ее
            if conversation_history:
                input_with_context = conversation_history + [{"role": "user", "content": query}]
                response = Runner.run_sync(
                    self.agent,
                    input_with_context,
                    run_config=run_config
                )
            else:
                response = Runner.run_sync(
                    self.agent,
                    query,
                    run_config=run_config
                )
            
            output = response.final_output
            
            # Обработка потенциальных JSON-ответов от инструментов
            try:
                # Проверяем, является ли ответ JSON-строкой с полем 'response'
                json_response = safe_parse_json(output)
                if isinstance(json_response, dict) and 'response' in json_response:
                    output = json_response['response']
                    logger.info(f"Extracted response from JSON output: {output[:100]}...")
            except:
                # Если не можем разобрать как JSON или нет ключа 'response',
                # оставляем оригинальный ответ
                pass
                    
            logger.info("Query processed successfully")
            return output
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"
    
    def get_registered_tools_info(self) -> List[Dict[str, Any]]:
        """
        Возвращает информацию о зарегистрированных инструментах.
        
        Returns:
            Список словарей с информацией об инструментах
        """
        tools = get_all_tools()
        tools_info = []
        
        for tool in tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description if hasattr(tool, "description") else "",
                "parameters": tool.parameters if hasattr(tool, "parameters") else {}
            }
            tools_info.append(tool_info)
            
        return tools_info

# Создаем синглтон мастер-агента
master_agent = MasterAgent()