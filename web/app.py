"""
Веб-интерфейс для системы zAI.

Этот модуль реализует веб-сервер для взаимодействия с мастер-агентом через браузер.
"""

import logging
import json
import uuid
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

from master_agent import master_agent
from config import PORT, HOST, DEBUG

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание Flask-приложения
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = str(uuid.uuid4())  # Для работы с сессиями

# Хранилище истории чатов
chat_histories = {}

@app.route('/')
def index():
    """
    Обработчик для главной страницы.
    """
    # Создаем уникальный ID сессии, если его нет
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        chat_histories[session['session_id']] = []
    
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API-эндпоинт для общения с мастер-агентом.
    """
    data = request.json
    query = data.get('message', '')
    
    if not query:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400
    
    # Получаем историю чата для этой сессии
    session_id = session.get('session_id')
    if not session_id or session_id not in chat_histories:
        session['session_id'] = str(uuid.uuid4())
        chat_histories[session['session_id']] = []
    
    history = chat_histories[session['session_id']]
    
    try:
        # Обрабатываем запрос
        response = master_agent.process_query(query, history)
        
        # Добавляем сообщения в историю
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response})
        
        # Ограничиваем историю до 50 сообщений
        if len(history) > 50:
            history = history[-50:]
        
        # Сохраняем обновленную историю
        chat_histories[session['session_id']] = history
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.exception("Error processing query")
        return jsonify({
            'error': str(e),
            'response': "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз."
        }), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """
    API-эндпоинт для очистки истории чата.
    """
    session_id = session.get('session_id')
    if session_id and session_id in chat_histories:
        chat_histories[session_id] = []
    
    return jsonify({'status': 'success', 'message': 'История чата очищена'})

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """
    API-эндпоинт для получения списка доступных инструментов.
    """
    tools = master_agent.get_registered_tools_info()
    return jsonify({'tools': tools, 'count': len(tools)})

def run_server():
    """
    Запускает веб-сервер.
    """
    app.run(host=HOST, port=PORT, debug=DEBUG)

if __name__ == "__main__":
    run_server()