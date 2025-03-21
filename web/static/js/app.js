// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const toolsBtn = document.getElementById('tools-btn');
const clearBtn = document.getElementById('clear-btn');
const toolsModal = document.getElementById('tools-modal');
const toolsList = document.getElementById('tools-list');
const closeBtn = document.querySelector('.close');

// State
let isWaitingForResponse = false;

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