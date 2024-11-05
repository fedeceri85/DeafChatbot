// static/script.js
const socket = io();
const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

let currentBotMessage = null;

function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'user-message';
    userDiv.innerHTML = `<strong>You:</strong> <span style="color: #FF4444; font-size: 16px;">${message}</span>`;
    chatHistory.appendChild(userDiv);
    
    // Clear input and emit message
    userInput.value = '';
    socket.emit('send_message', { message });
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

socket.on('response_chunk', data => {
    if (!currentBotMessage) {
        // Create new bot message
        currentBotMessage = document.createElement('div');
        currentBotMessage.className = 'bot-message';
        currentBotMessage.innerHTML = `<strong>Dr. Hear:</strong> <div style="text-align: justify;">${data.chunk}</div>`;
        chatHistory.appendChild(currentBotMessage);
    } else {
        // Update existing message
        currentBotMessage.innerHTML = `<strong>Dr. Hear:</strong> <div style="text-align: justify;">${data.chunk}</div>`;
    }

    // Reset on complete response
    if (data.is_complete) {
        currentBotMessage = null;
    }

    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
});

// Event listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
});

// Handle preset questions
function sendQuestion(question) {
    userInput.value = question;
    sendMessage();
}