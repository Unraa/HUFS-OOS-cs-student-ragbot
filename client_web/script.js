<<<<<<< HEAD

=======
<<<<<<< HEAD
>>>>>>> d5efc3c (chore: js 코드 파일 분리)
=======
>>>>>>> bc5a56123a1d01b52d2a03a447b817325c1b4f46
>>>>>>> 5240e18c0220cd3d7b9cb9c12fcf10852e845c23
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');

    function addMessage(text, isUser) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('message-wrapper');
        wrapper.classList.add(isUser ? 'user' : 'bot');

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');

        if (isUser) {
            messageDiv.textContent = text;
        } else {
            messageDiv.classList.add('markdown');
            messageDiv.innerHTML = marked.parse(text);
        }

        wrapper.appendChild(messageDiv);
        chatMessages.insertBefore(wrapper, typingIndicator);

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        messageInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) throw new Error('API 응답 오류');

            const data = await response.json();
            hideTypingIndicator();

            setTimeout(() => {
                addMessage(data.response, false);
            }, 500);

        } catch (error) {
            console.error('오류 발생:', error);
            hideTypingIndicator();

            setTimeout(() => {
                addMessage('죄송합니다. 오류가 발생했습니다. 나중에 다시 시도해주세요.', false);
            }, 500);
        }
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
