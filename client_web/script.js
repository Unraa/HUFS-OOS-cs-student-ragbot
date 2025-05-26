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

    function addBotTypingEffect(text) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('message-wrapper', 'bot');

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message', 'markdown');
        wrapper.appendChild(messageDiv);

        chatMessages.insertBefore(wrapper, typingIndicator);

        let idx = 0;
        function typing() {
            if (idx <= text.length) {
                messageDiv.innerHTML = marked.parse(text.slice(0, idx) + '▌');
                chatMessages.scrollTop = chatMessages.scrollHeight;
                idx++;
                setTimeout(typing, 12); // 속도 조절
            } else {
                messageDiv.innerHTML = marked.parse(text);
            }
        }
        typing();
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

        const BASE_URL = location.hostname === "localhost"
        ? "http://localhost:8000"
        : "https://hufscomchatbot.duckdns.org";

        try {
            const response = await fetch(`${BASE_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) throw new Error('API 응답 오류');

            const data = await response.json();
            hideTypingIndicator();

            addBotTypingEffect(data.response);

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
