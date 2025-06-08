"""
Веб-интерфейс для системы zAI.

Этот модуль реализует веб-сервер для взаимодействия с мастер-агентом через браузер.
"""

import logging
import json
import uuid
import os
import tempfile
import base64
from flask import Flask, render_template, request, jsonify, session, send_file
from datetime import datetime
from openai import OpenAI

from master_agent import master_agent
from config import PORT, HOST, DEBUG, OPENAI_API_KEY

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zai_web")

# Создаем клиента OpenAI для работы с API
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Создание Flask-приложения
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = str(uuid.uuid4())  # Для работы с сессиями

# Хранилище истории чатов
chat_histories = {}

# Настройки голосовых ответов для пользователей
voice_responses_enabled = {}  # Словарь для хранения настроек пользователей

@app.route('/')
def index():
    """
    Обработчик для главной страницы.
    """
    # Создаем уникальный ID сессии, если его нет
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        chat_histories[session['session_id']] = []
        voice_responses_enabled[session['session_id']] = False
    
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API-эндпоинт для общения с мастер-агентом через текст.
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
        voice_responses_enabled[session['session_id']] = False
    
    history = chat_histories[session['session_id']]
    
    try:
        # Обрабатываем запрос
        response = master_agent.process_query(query, history)
        
        result = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        # Проверяем, нужно ли создавать голосовой ответ
        if voice_responses_enabled.get(session_id, False):
            try:
                audio_response = openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=response
                )
                
                # Сохраняем аудио во временный файл
                audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                audio_temp.close()
                
                # Сохраняем аудио в файл
                audio_response.stream_to_file(audio_temp.name)
                
                # Читаем файл и кодируем в base64
                with open(audio_temp.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                result['audio'] = base64.b64encode(audio_data).decode('utf-8')
                
                # Удаляем временный файл
                os.unlink(audio_temp.name)
            except Exception as e:
                logger.error(f"Error generating speech: {str(e)}")
                # Продолжаем без аудио в случае ошибки
        
        # Добавляем сообщения в историю
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response})
        
        # Ограничиваем историю до 50 сообщений
        if len(history) > 50:
            history = history[-50:]
        
        # Сохраняем обновленную историю
        chat_histories[session['session_id']] = history
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Error processing query")
        return jsonify({
            'error': str(e),
            'response': "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз."
        }), 500

@app.route('/api/voice-chat', methods=['POST'])
def voice_chat():
    """
    API-эндпоинт для обработки голосовых запросов.
    """
    # Проверяем наличие аудиофайла
    if 'audio' not in request.files:
        return jsonify({'error': 'Аудиофайл не найден'}), 400
    
    audio_file = request.files['audio']
    
    # Получаем информацию о формате файла
    content_type = audio_file.content_type or 'audio/webm'
    logger.info(f"Получен аудиофайл типа: {content_type}")
    
    # Сохраняем временный файл сначала с временным расширением
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # Проверяем размер файла
        file_size = os.path.getsize(temp_file.name)
        logger.info(f"Размер аудиофайла: {file_size} байт")
        
        if file_size == 0:
            os.unlink(temp_file.name)
            return jsonify({'error': 'Аудиофайл пуст'}), 400
        
        # Выводим информацию о заголовках файла (первые 20 байт)
        with open(temp_file.name, 'rb') as f:
            header_bytes = f.read(20)
            logger.info(f"Заголовок файла (hex): {header_bytes.hex()}")
        
        # Определяем тип файла системой
        import subprocess
        try:
            file_type = subprocess.check_output(['file', '-b', '--mime-type', temp_file.name]).decode('utf-8').strip()
            logger.info(f"Определенный системой тип файла: {file_type}")
            
            # Выбираем правильное расширение на основе определенного типа
            correct_ext = '.tmp'  # По умолчанию
            if 'mp4' in file_type:
                correct_ext = '.mp4'
            elif 'webm' in file_type:
                correct_ext = '.webm'
            elif 'ogg' in file_type:
                correct_ext = '.ogg'
            elif 'wav' in file_type:
                correct_ext = '.wav'
            elif 'mpeg' in file_type or 'mp3' in file_type:
                correct_ext = '.mp3'
            
            # Создаем новый файл с правильным расширением
            correct_temp_file = temp_file.name.replace('.tmp', correct_ext)
            os.rename(temp_file.name, correct_temp_file)
            temp_file_name = correct_temp_file
            logger.info(f"Файл сохранен с расширением: {correct_ext}")
        except Exception as e:
            logger.info(f"Не удалось определить тип файла: {str(e)}")
            temp_file_name = temp_file.name
        
        # Транскрибируем аудио в текст
        with open(temp_file_name, 'rb') as audio:
            try:
                transcript = openai_client.audio.transcriptions.create(
                    file=audio,
                    model="whisper-1"
                )
                logger.info("Транскрипция успешно выполнена")
            except Exception as e:
                logger.error(f"Ошибка при транскрипции: {str(e)}")
                # Пробуем указать формат файла явно
                try:
                    with open(temp_file_name, 'rb') as audio:
                        transcript = openai_client.audio.transcriptions.create(
                            file=audio,
                            model="whisper-1",
                            response_format="text"
                        )
                    logger.info("Транскрипция успешно выполнена со второй попытки")
                except Exception as e2:
                    logger.error(f"Вторая попытка транскрипции также не удалась: {str(e2)}")
                    raise e2
        
        query = transcript.text
        logger.info(f"Транскрибированный текст: {query}")
        
        # Получаем историю чата для этой сессии
        session_id = session.get('session_id')
        if not session_id or session_id not in chat_histories:
            session['session_id'] = str(uuid.uuid4())
            chat_histories[session['session_id']] = []
            voice_responses_enabled[session['session_id']] = False
        
        history = chat_histories[session['session_id']]
        
        # Обрабатываем запрос через мастер-агента
        response_text = master_agent.process_query(query, history)
        
        result = {
            'text': query,
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Проверяем, нужно ли создавать голосовой ответ
        if voice_responses_enabled.get(session_id, False):
            audio_response = openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=response_text
            )
            
            # Сохраняем аудио во временный файл
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            audio_temp.close()
            
            # Сохраняем аудио в файл
            audio_response.stream_to_file(audio_temp.name)
            
            # Читаем файл и кодируем в base64
            with open(audio_temp.name, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            result['audio'] = base64.b64encode(audio_data).decode('utf-8')
            
            # Удаляем временный файл
            os.unlink(audio_temp.name)
        
        # Добавляем сообщения в историю
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response_text})
        
        # Ограничиваем историю до 50 сообщений
        if len(history) > 50:
            history = history[-50:]
        
        # Сохраняем обновленную историю
        chat_histories[session['session_id']] = history
        
        # Удаляем временный файл
        if os.path.exists(temp_file_name):
            os.unlink(temp_file_name)
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Error processing voice query")
        # Удаляем временный файл в случае ошибки
        if 'temp_file_name' in locals() and os.path.exists(temp_file_name):
            os.unlink(temp_file_name)
        elif os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        
        return jsonify({
            'error': str(e),
            'response': "Извините, произошла ошибка при обработке вашего голосового запроса. Пожалуйста, попробуйте еще раз."
        }), 500

@app.route('/api/toggle-voice-response', methods=['POST'])
def toggle_voice_response():
    """
    API-эндпоинт для включения/выключения голосовых ответов.
    """
    data = request.json
    enabled = data.get('enabled', False)
    
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
    
    voice_responses_enabled[session_id] = enabled
    
    return jsonify({
        'status': 'success', 
        'voice_responses_enabled': enabled
    })

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