// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const toolsBtn = document.getElementById('tools-btn');
const clearBtn = document.getElementById('clear-btn');
const voiceBtn = document.getElementById('voice-btn');
const voiceResponseToggle = document.getElementById('voice-response-toggle');
const toolsModal = document.getElementById('tools-modal');
const toolsList = document.getElementById('tools-list');
const closeBtn = document.querySelector('.close');

// State
let isWaitingForResponse = false;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Auto-resize textarea as content grows
    chatInput.addEventListener('input', autoResizeTextarea);
    
    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);
    
    // Send message on Enter key (but allow Shift+Enter for new line)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Show tools modal
    toolsBtn.addEventListener('click', showTools);
    
    // Clear chat history
    clearBtn.addEventListener('click', clearChatHistory);
    
    // Close modal
    closeBtn.addEventListener('click', () => {
        toolsModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === toolsModal) {
            toolsModal.style.display = 'none';
        }
    });
    
    // Voice recording handler - toggle mode
    voiceBtn.addEventListener('click', toggleRecording);
    
    // For mobile devices
    voiceBtn.addEventListener('touchstart', (e) => {
        e.preventDefault(); // Prevent default touch behavior
    });
    
    voiceBtn.addEventListener('touchend', (e) => {
        e.preventDefault();
        if (!e.cancelable) return; // Ignore if event is not cancelable
        toggleRecording();
    });
    
    // Voice response toggle
    voiceResponseToggle.addEventListener('change', toggleVoiceResponse);
    
    // Scroll to bottom on load
    scrollToBottom();
});

// Functions
function sendMessage() {
    const message = chatInput.value.trim();
    
    if (message === '' || isWaitingForResponse) return;
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Clear input
    chatInput.value = '';
    autoResizeTextarea();
    
    // Show typing indicator
    showTypingIndicator();
    
    // Set waiting flag
    isWaitingForResponse = true;
    
    // Disable input while waiting
    chatInput.disabled = true;
    sendBtn.disabled = true;
    
    // Send message to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add assistant message to chat
        if (data.error) {
            addMessageToChat('system', `Произошла ошибка: ${data.error}`);
        } else {
            addMessageToChat('assistant', data.response);
            
            // If there's audio response, play it
            if (data.audio) {
                playAudioResponse(data.audio);
            }
        }
    })
    .catch(error => {
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add error message
        addMessageToChat('system', `Произошла ошибка при отправке сообщения: ${error.message}`);
    })
    .finally(() => {
        // Reset waiting flag
        isWaitingForResponse = false;
        
        // Enable input
        chatInput.disabled = false;
        sendBtn.disabled = false;
        
        // Focus input
        chatInput.focus();
    });
}

function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Split content by newlines and create paragraph for each
    const paragraphs = content.split('\n').filter(p => p.trim() !== '');
    paragraphs.forEach(paragraph => {
        const p = document.createElement('p');
        p.textContent = paragraph;
        contentDiv.appendChild(p);
    });
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to the bottom
    scrollToBottom();
    
    return messageDiv;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing';
    typingDiv.id = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        dot.className = 'typing-dot';
        typingDiv.appendChild(dot);
    }
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function autoResizeTextarea() {
    chatInput.style.height = 'auto';
    chatInput.style.height = (chatInput.scrollHeight) + 'px';
}

function showTools() {
    // Show modal
    toolsModal.style.display = 'block';
    
    // Load tools
    fetch('/api/tools')
        .then(response => response.json())
        .then(data => {
            toolsList.innerHTML = '';
            
            if (data.tools && data.tools.length > 0) {
                data.tools.forEach(tool => {
                    const toolCard = document.createElement('div');
                    toolCard.className = 'tool-card';
                    
                    const title = document.createElement('h3');
                    title.textContent = tool.name;
                    
                    const description = document.createElement('p');
                    description.textContent = tool.description;
                    
                    toolCard.appendChild(title);
                    toolCard.appendChild(description);
                    
                    // Add parameters if any
                    if (tool.parameters && Object.keys(tool.parameters).length > 0) {
                        const paramsTitle = document.createElement('div');
                        paramsTitle.className = 'parameters-title';
                        paramsTitle.textContent = 'Параметры:';
                        toolCard.appendChild(paramsTitle);
                        
                        for (const [key, param] of Object.entries(tool.parameters)) {
                            const paramSpan = document.createElement('span');
                            paramSpan.className = 'parameter';
                            paramSpan.textContent = key;
                            paramSpan.title = param.description || '';
                            toolCard.appendChild(paramSpan);
                        }
                    }
                    
                    toolsList.appendChild(toolCard);
                });
            } else {
                toolsList.innerHTML = '<div class="loading">Нет доступных инструментов</div>';
            }
        })
        .catch(error => {
            toolsList.innerHTML = `<div class="loading">Ошибка загрузки инструментов: ${error.message}</div>`;
        });
}

function clearChatHistory() {
    // Confirm before clearing
    if (confirm('Вы уверены, что хотите очистить историю чата?')) {
        fetch('/api/clear-history', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Clear chat UI
                chatMessages.innerHTML = '';
                
                // Add welcome message
                const welcomeMsg = document.createElement('div');
                welcomeMsg.className = 'message system';
                
                const welcomeContent = document.createElement('div');
                welcomeContent.className = 'message-content';
                
                const p1 = document.createElement('p');
                p1.textContent = 'Добро пожаловать в систему zAI!';
                
                const p2 = document.createElement('p');
                p2.textContent = 'Я - мастер-агент, координирующий работу специализированных AI-агентов. Чем я могу вам помочь сегодня?';
                
                welcomeContent.appendChild(p1);
                welcomeContent.appendChild(p2);
                welcomeMsg.appendChild(welcomeContent);
                
                chatMessages.appendChild(welcomeMsg);
            } else {
                addMessageToChat('system', 'Не удалось очистить историю чата.');
            }
        })
        .catch(error => {
            addMessageToChat('system', `Ошибка при очистке истории: ${error.message}`);
        });
    }
}

// Toggle recording on/off
function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// Voice functions
function startRecording() {
    if (isRecording) return;
    
    // Check if MediaRecorder is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        addMessageToChat('system', 'Ваш браузер не поддерживает запись аудио. Пожалуйста, обновите браузер или используйте текстовый ввод.');
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            // Change button appearance
            voiceBtn.classList.add('recording');
            voiceBtn.querySelector('i').className = 'fas fa-stop';
            
            // Initialize MediaRecorder
            try {
                // Try to create MediaRecorder with specific options
                const options = { mimeType: 'audio/webm' };
                mediaRecorder = new MediaRecorder(stream, options);
            } catch (e) {
                console.error('Failed to create MediaRecorder with specified options, trying default', e);
                try {
                    // Try with default options
                    mediaRecorder = new MediaRecorder(stream);
                } catch (e) {
                    console.error('Failed to create MediaRecorder', e);
                    addMessageToChat('system', 'Не удалось инициализировать запись. Пожалуйста, используйте текстовый ввод.');
                    return;
                }
            }
            
            // Collect audio chunks
            audioChunks = [];
            mediaRecorder.addEventListener('dataavailable', event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            });
            
            // Request data frequently to ensure we get something
            mediaRecorder.start(100); // Get data every 100ms
            isRecording = true;
            
            // Handle recording stop
            mediaRecorder.addEventListener('stop', () => {
                // Stop all tracks in the stream
                stream.getTracks().forEach(track => track.stop());
                
                // Check if we have any audio data
                if (audioChunks.length === 0 || audioChunks.every(chunk => chunk.size === 0)) {
                    console.error('No audio data collected');
                    addMessageToChat('system', 'Не удалось записать аудио. Пожалуйста, попробуйте еще раз или используйте текстовый ввод.');
                    return;
                }
                
                // Create Blob from collected chunks
                const audioBlob = new Blob(audioChunks);
                
                // Debug
                console.log('Audio size:', audioBlob.size, 'bytes');
                console.log('Audio type:', audioBlob.type);
                
                // Show processing indicator
                showTypingIndicator();
                
                // Send audio to server
                const formData = new FormData();
                
                // Use the correct MIME type
                const mimeType = audioBlob.type || 'audio/webm';
                const extension = mimeType.includes('webm') ? 'webm' : 
                                 mimeType.includes('mp4') ? 'mp4' : 
                                 mimeType.includes('ogg') ? 'ogg' : 'webm';
                
                formData.append('audio', audioBlob, `recording.${extension}`);
                
                fetch('/api/voice-chat', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Remove loading indicator
                    removeTypingIndicator();
                    
                    // Add recognized text to chat
                    if (data.text) {
                        addMessageToChat('user', data.text);
                    }
                    
                    // Add response to chat
                    addMessageToChat('assistant', data.response);
                    
                    // If there's audio response, play it
                    if (data.audio) {
                        playAudioResponse(data.audio);
                    }
                })
                .catch(error => {
                    removeTypingIndicator();
                    addMessageToChat('system', `Ошибка обработки голосового запроса: ${error.message}`);
                });
            });
        })
        .catch(error => {
            console.error('Ошибка доступа к микрофону:', error);
            addMessageToChat('system', 'Не удалось получить доступ к микрофону. Пожалуйста, проверьте разрешения браузера.');
        });
}

function stopRecording() {
    if (!isRecording || !mediaRecorder) return;
    
    // Change button appearance
    voiceBtn.classList.remove('recording');
    voiceBtn.querySelector('i').className = 'fas fa-microphone';
    
    // Stop recording
    mediaRecorder.stop();
    isRecording = false;
}

function toggleVoiceResponse() {
    const enabled = voiceResponseToggle.checked;
    
    fetch('/api/toggle-voice-response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ enabled })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(`Голосовые ответы ${enabled ? 'включены' : 'выключены'}`);
        }
    })
    .catch(error => {
        console.error('Ошибка переключения голосовых ответов:', error);
    });
}

function playAudioResponse(base64Audio) {
    // Create container for audio player
    const audioContainer = document.createElement('div');
    audioContainer.className = 'audio-player';
    
    // Create audio element
    const audio = document.createElement('audio');
    audio.controls = true;
    
    // Set audio source
    const source = `data:audio/mp3;base64,${base64Audio}`;
    audio.src = source;
    
    // Add audio to container
    audioContainer.appendChild(audio);
    
    // Find the last message from assistant
    const messages = document.querySelectorAll('.message.assistant');
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage) {
        lastMessage.appendChild(audioContainer);
    }
    
    // Auto-play audio
    audio.play().catch(error => {
        console.error('Ошибка автоматического воспроизведения:', error);
    });
}