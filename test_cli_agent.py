#!/usr/bin/env python
"""
Скрипт для тестирования CLI-интерфейса инвестиционного агента.

Этот скрипт позволяет быстро проверить работу CLI-интерфейса инвестиционного агента
без необходимости запуска всего мастер-агента.

Использование:
    python test_cli_agent.py
"""

import os
import subprocess
import json
import sys

# Путь к директории инвестиционного агента
INVESTMENT_AGENT_DIR = "/Users/zilber/Desktop/repo/ai_agent_finance"
CLI_SCRIPT_PATH = os.path.join(INVESTMENT_AGENT_DIR, "cli_agent.py")

def test_cli_agent(query: str):
    """
    Тестирует CLI-интерфейс инвестиционного агента.
    
    Args:
        query: Запрос для отправки агенту
    """
    print(f"Отправка запроса: {query}")
    print("-" * 50)
    
    try:
        # Запускаем CLI-скрипт как подпроцесс
        process = subprocess.Popen(
            ["python", CLI_SCRIPT_PATH, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=INVESTMENT_AGENT_DIR,
            text=True
        )
        
        # Получаем вывод
        stdout, stderr = process.communicate(timeout=30)
        
        # Проверяем статус выполнения
        if process.returncode != 0:
            print(f"Ошибка при выполнении CLI-скрипта (код {process.returncode}):")
            print(stderr)
            return
        
        # Выводим сырой ответ
        print("Сырой ответ:")
        print(stdout)
        print("-" * 50)
        
        # Пытаемся разобрать JSON
        try:
            result = json.loads(stdout)
            print("Разобранный JSON:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError as e:
            print(f"Ошибка при разборе JSON: {str(e)}")
        
    except subprocess.TimeoutExpired:
        print("Таймаут при ожидании ответа от инвестиционного агента")
    except Exception as e:
        print(f"Ошибка при тестировании: {str(e)}")

def main():
    """
    Основная функция скрипта.
    """
    # Проверяем существование CLI-скрипта
    if not os.path.exists(CLI_SCRIPT_PATH):
        print(f"Ошибка: CLI-скрипт не найден по пути {CLI_SCRIPT_PATH}")
        sys.exit(1)
    
    # Запрашиваем пользовательский ввод
    query = input("Введите запрос для инвестиционного агента: ")
    
    # Тестируем CLI-агента
    test_cli_agent(query)

if __name__ == "__main__":
    main()