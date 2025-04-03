
import requests
import json

# Настройки для тестирования
BOT_DB_API_URL = "http://localhost:5001/api"
BOT_DB_API_KEY = "yNkP8Qz2XbTr5Vw7JsLm3GfHd9AeC6B1"  # Используйте ваш API-ключ

# Функция для тестирования получения схемы
def test_get_schema():
    try:
        response = requests.get(
            f"{BOT_DB_API_URL}/schema",
            headers={"X-API-Key": BOT_DB_API_KEY}
        )
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting schema: {str(e)}")
        return {"error": str(e)}

# Функция для тестирования запроса к БД
def test_query(query, params=None):
    try:
        response = requests.post(
            f"{BOT_DB_API_URL}/query",
            json={"query": query, "params": params or []},
            headers={"X-API-Key": BOT_DB_API_KEY}
        )
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return {"error": str(e)}

# Выполняем тесты
print("Testing Schema API:")
schema_result = test_get_schema()
print(json.dumps(schema_result, indent=2))
print("-" * 50)

print("Testing Query API:")
query_result = test_query("SELECT COUNT(*) as total_users FROM users")
print(json.dumps(query_result, indent=2))