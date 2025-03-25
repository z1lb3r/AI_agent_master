"""
Коннектор для взаимодействия с инвестиционным агентом через subprocess.
"""

import json
import logging
import subprocess
import os
from typing import Dict, Any

from tools.registry import register_tool

# Настройка логирования
logger = logging.getLogger(__name__)

# Путь к директории инвестиционного агента
# В продакшене это лучше вынести в конфигурационный файл
INVESTMENT_AGENT_DIR = "/Users/zilber/Desktop/repo/ai_agent_finance"
RUN_AGENT_SCRIPT_PATH = os.path.join(INVESTMENT_AGENT_DIR, "run_agent.py")

# Увеличенный таймаут до 180 секунд (3 минуты)
SUBPROCESS_TIMEOUT = 180

@register_tool
def ask_investment_agent(query: str) -> str:
    """
    Перенаправляет запрос инвестиционному агенту через subprocess и возвращает его ответ.
    
    Args:
        query: Запрос для инвестиционного агента
    
    Returns:
        Ответ инвестиционного агента
    """
    try:
        # Проверяем существование скрипта
        if not os.path.exists(RUN_AGENT_SCRIPT_PATH):
            error_msg = f"Скрипт запуска инвестиционного агента не найден по пути: {RUN_AGENT_SCRIPT_PATH}"
            logger.error(error_msg)
            # Возвращаем ошибку в формате JSON-строки
            return json.dumps({
                "response": f"Ошибка: {error_msg}"
            })
        
        logger.info(f"Отправка запроса инвестиционному агенту: {query}")
        
        # Запускаем скрипт как подпроцесс, передавая запрос
        # Устанавливаем рабочую директорию и окружение
        env = os.environ.copy()
        
        # Запускаем процесс с увеличенным таймаутом
        process = subprocess.Popen(
            ["python", RUN_AGENT_SCRIPT_PATH, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=INVESTMENT_AGENT_DIR,
            env=env,
            text=True
        )
        
        # Получаем вывод с таймаутом
        try:
            stdout, stderr = process.communicate(timeout=SUBPROCESS_TIMEOUT)
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error("Таймаут при ожидании ответа от инвестиционного агента")
            # Возвращаем сообщение о таймауте в формате JSON-строки
            return json.dumps({
                "response": "Инвестиционный агент не ответил в течение отведенного времени. Возможно, запрос требует больше времени для обработки."
            })
        
        # Проверяем, успешно ли выполнился процесс
        if process.returncode != 0:
            error_msg = f"Ошибка при выполнении скрипта запуска агента: {stderr}"
            logger.error(error_msg)
            # Возвращаем ошибку в формате JSON-строки
            return json.dumps({
                "response": f"Ошибка: {error_msg}"
            })
        
        # Подробное логирование полученного вывода
        logger.info(f"Получен ответ от инвестиционного агента (первые 200 символов): {stdout[:200] if stdout else 'пустой ответ'}")
        
        # Проверяем, не пустой ли ответ
        if not stdout or stdout.isspace():
            logger.error("Получен пустой ответ от инвестиционного агента")
            # Возвращаем сообщение о пустом ответе в формате JSON-строки
            return json.dumps({
                "response": "Инвестиционный агент вернул пустой ответ."
            })
        
        # Пытаемся разобрать JSON-ответ
        try:
            result = json.loads(stdout)
            
            # Если инвестиционный агент вернул ошибку
            if not result.get("success", True) or "error" in result:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Инвестиционный агент вернул ошибку: {error_msg}")
                # Возвращаем ошибку в формате JSON-строки
                return json.dumps({
                    "response": f"Инвестиционный агент сообщил об ошибке: {error_msg}"
                })
            
            # Получаем ответ в виде текста
            response_text = result.get("response", "")
            
            # ВАЖНО: Всегда возвращаем ответ в формате JSON-строки
            return json.dumps({
                "response": response_text
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON-ответа: {str(e)}")
            logger.error(f"Полученный ответ (первые 500 символов): {stdout[:500]}")
            
            # Возможно, агент вернул текстовый ответ, а не JSON
            # Оборачиваем его в JSON и возвращаем
            try:
                # Проверяем формат ответа
                if stdout.strip().startswith('{'):
                    # Если ответ похож на JSON, но не валидный, возвращаем ошибку
                    return json.dumps({
                        "response": f"Некорректный формат ответа от инвестиционного агента."
                    })
                else:
                    # Иначе просто оборачиваем текст в JSON
                    return json.dumps({
                        "response": stdout
                    })
            except Exception:
                # В случае любых ошибок, возвращаем безопасное сообщение
                return json.dumps({
                    "response": "Произошла ошибка при обработке ответа от инвестиционного агента."
                })
        
    except Exception as e:
        logger.error(f"Ошибка при обращении к инвестиционному агенту: {str(e)}")
        import traceback
        logger.error(f"Трассировка ошибки: {traceback.format_exc()}")
        # Возвращаем сообщение об ошибке в формате JSON-строки
        return json.dumps({
            "response": f"Не удалось получить ответ от инвестиционного агента: {str(e)}"
        })