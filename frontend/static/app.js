// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const terminalPanel = document.getElementById('terminal-panel');
    const toggleTermBtn = document.getElementById('toggle-term');
    const specList = document.getElementById('spec-list'); // Note: Id changed in index.html, but I used fingerprint-list for hashes
    const fingerprintList = document.getElementById('fingerprint-list');
    const modelSelect = document.getElementById('model-select');

    console.log('App elements loaded:', { messagesContainer, userInput, sendBtn, terminalPanel, toggleTermBtn, modelSelect });

    // State for chat history
    let chatHistory = [];
    let isSending = false;

    // Initialize UI
    fetchSpecs();
    fetchFingerprints();
    renderHistory();

    // Toggle Terminal
    toggleTermBtn.addEventListener('click', () => {
        const isHidden = terminalPanel.style.display === 'none' || terminalPanel.style.display === '';
        terminalPanel.style.display = isHidden ? 'block' : 'none';
        toggleTermBtn.innerText = isHidden ? 'Hide Terminal Console' : 'Show Terminal Console';
    });

    // Auto-resize textarea
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Fetch OpenSpec files from backend
    async function fetchSpecs() {
        try {
            const response = await fetch('/api/specs');
            if (!response.ok) throw new Error('Specs fetch failed');
            const data = await response.json();
            const list = document.getElementById('spec-list'); // It might be missing if I replaced it
            if (list) {
                list.innerHTML = '';
                data.forEach(spec => {
                    const div = document.createElement('div');
                    div.className = 'spec-item';
                    div.innerText = spec;
                    list.appendChild(div);
                });
            }
        } catch (err) {
            console.error('Failed to load project specs:', err);
        }
    }

    // Fetch Neural Fingerprints
    async function fetchFingerprints() {
        try {
            const response = await fetch('/api/engram/fingerprint');
            if (!response.ok) throw new Error('Fingerprint fetch failed');
            const data = await response.json();
            if (fingerprintList) {
                fingerprintList.innerHTML = '';
                Object.entries(data).forEach(([path, info]) => {
                    const div = document.createElement('div');
                    div.className = 'spec-item';
                    div.style.fontSize = '0.75rem';
                    div.style.fontFamily = "'JetBrains Mono', monospace";
                    div.innerHTML = `<span style="color: var(--accent-primary)">#${info.token_id}</span> ${info.label}`;
                    fingerprintList.appendChild(div);
                });
            }
        } catch (err) {
            console.error('Failed to load neural fingerprints:', err);
        }
    }

    // Handle Send
    async function handleSend() {
        if (isSending) return;
        const text = userInput.value.trim();
        if (!text) return;

        isSending = true;
        sendBtn.disabled = true;
        sendBtn.style.opacity = '0.5';

        const selectedModel = modelSelect ? modelSelect.value : 'liquid/lfm2.5-1.2b';
        console.log('handleSend called with:', text, 'Model:', selectedModel);

        // Add user message to history
        chatHistory.push({ role: 'user', content: text });
        renderHistory();

        userInput.value = '';
        userInput.style.height = 'auto';

        // Handle commands (e.g., /run [cmd] or /[cmd])
        if (text.startsWith('/')) {
            const cmd = text.startsWith('/run ') ? text.substring(5) : text.substring(1);
            appendToTerminal(`Executing via OpenCode: ${cmd}`, 'cmd');

            try {
                const response = await fetch('/opencode/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await response.json();

                if (data.error) throw new Error(data.error);

                const output = data.stdout || data.stderr || "Success (no output)";
                appendToTerminal(output, 'out');

                // Add execution result to chat
                const resultMsg = `I have executed the command: \`${cmd}\`\n\n\`\`\`bash\n${output}\n\`\`\``;
                chatHistory.push({ role: 'assistant', content: resultMsg });
                renderHistory();
            } catch (err) {
                appendToTerminal(`Error: ${err.message}`, 'out');
                chatHistory.push({ role: 'assistant', content: `Failed to execute OpenCode command: ${err.message}` });
                renderHistory();
            }
            return;
        }

        // Add loading state
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant loading';
        loadingDiv.id = loadingId;
        loadingDiv.innerText = `Thinking with ${selectedModel === 'liquid/lfm2.5-1.2b' ? 'Liquid' : 'GLM'}...`;
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch('/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: selectedModel,
                    messages: chatHistory,
                    max_tokens: 1000
                })
            });

            const data = await response.json();

            // Remove loading
            const loader = document.getElementById(loadingId);
            if (loader) loader.remove();

            if (response.ok && data.choices && data.choices[0]) {
                const content = data.choices[0].message.content;
                chatHistory.push({ role: 'assistant', content: content });
                renderHistory();
            } else {
                const errorMsg = data.detail || (data.error ? data.error.message : 'Unknown AI server error');
                throw new Error(errorMsg);
            }
        } catch (err) {
            console.error('Chat error:', err);
            const loader = document.getElementById(loadingId);
            if (loader) {
                loader.innerHTML = `
                    <div style="color: #ff5555; padding: 10px; border-radius: 8px; background: rgba(255,85,85,0.1); border: 1px solid rgba(255,85,85,0.3);">
                        <b>Connection Error:</b> ${err.message}<br>
                        <small style="display: block; margin-top: 5px; opacity: 0.8;">
                            Troubleshooting:<br>
                            1. Is <b>${selectedModel}</b> loaded in LM Studio?<br>
                            2. Is the LM Studio server running on port 1234?<br>
                            3. Try switching the model in the sidebar.
                        </small>
                    </div>`;
                loader.classList.remove('loading');
            }
        } finally {
            isSending = false;
            sendBtn.disabled = false;
            sendBtn.style.opacity = '1';
        }
    }

    function renderHistory() {
        messagesContainer.innerHTML = '';
        chatHistory.forEach(msg => {
            const div = document.createElement('div');
            div.className = `message ${msg.role}`;
            // Use marked (loaded in index.html) to parse markdown
            if (typeof marked !== 'undefined') {
                div.innerHTML = marked.parse(msg.content);
            } else {
                div.innerText = msg.content;
            }
            messagesContainer.appendChild(div);
        });
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function appendToTerminal(text, type) {
        const line = document.createElement('div');
        line.className = `terminal-line ${type}`;
        line.innerText = type === 'cmd' ? `> ${text}` : text;
        terminalPanel.appendChild(line);
        terminalPanel.scrollTop = terminalPanel.scrollHeight;
    }

    // Handle Send button click
    sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        handleSend();
    });

    // Handle Enter key in textarea
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
});
