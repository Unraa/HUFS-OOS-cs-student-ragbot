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

    async function addBotTypingEffectWithTable(text) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('message-wrapper', 'bot');
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message', 'markdown');
        wrapper.appendChild(messageDiv);
        chatMessages.insertBefore(wrapper, typingIndicator);

        // 1. 코드블록(표) 구간 분리
        const codeblockRegex = /```markdown([\s\S]*?)```/g;
        let lastIdx = 0, match;
        let fragments = [];

        // codeblock 외의 문단과 표를 분리해서 배열에 담기
        while ((match = codeblockRegex.exec(text)) !== null) {
            if (lastIdx < match.index) {
                // 코드블록 앞의 텍스트
                fragments.push({ type: "text", content: text.slice(lastIdx, match.index) });
            }
            // 코드블록(표) 자체
            fragments.push({ type: "table", content: "```markdown" + match[1] + "```" });
            lastIdx = codeblockRegex.lastIndex;
        }
        if (lastIdx < text.length) {
            fragments.push({ type: "text", content: text.slice(lastIdx) });
        }

        // 2. 실제 타이핑 효과 적용
        let html = '';
        for (let frag of fragments) {
            if (frag.type === "table") {
                // 표(코드블록)는 한 번에 출력
                html += marked.parse(frag.content);
                messageDiv.innerHTML = html;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                // 일반 텍스트(문단/목록)는 한글자씩 출력
                for (let i = 0; i < frag.content.length; i++) {
                    html += frag.content[i];
                    messageDiv.innerHTML = marked.parse(html);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    await new Promise(res => setTimeout(res, 13)); // 타이핑 속도 (조절 가능)
                }
            }
        }
        messageDiv.innerHTML = marked.parse(html); // 마지막 렌더링(혹시 남은 거 있을 때)
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

        const BASE_URL = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
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

            await addBotTypingEffectWithTable(data.response);

        } catch (error) {
            console.error('오류 발생:', error);
            hideTypingIndicator();

            setTimeout(() => {
                addMessage('죄송합니다. 오류가 발생했습니다. 나중에 다시 시도해주세요.', false);
            }, 500);
        }
    }

    const settingsBtn = document.getElementById('settings-button');
    const settingsPanel = document.getElementById('settings-panel');
    settingsBtn.addEventListener('click', () => {
    settingsPanel.classList.toggle('hidden');
    });

    const closeBtn = document.getElementById('close-settings');

    closeBtn.addEventListener('click', () => {
        settingsPanel.classList.add('hidden');
    });

    const fontSizeSlider = document.getElementById('font-size-slider');

    fontSizeSlider.addEventListener('input', (e) => {
        const size = e.target.value + 'px';
        chatMessages.style.fontSize = size;
    });

    const darkModeToggle = document.getElementById('dark-mode-toggle');

    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('darkmode');
        darkModeToggle.checked = true;  // 스위치도 켜진 상태로
    }


    darkModeToggle.addEventListener('change', () => {
        document.body.classList.toggle('darkmode');
        const theme = document.body.classList.contains('darkmode') ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
    });


    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
