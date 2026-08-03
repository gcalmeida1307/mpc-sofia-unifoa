async function loadJSON(url) {
  const response = await fetch(url);
  return response.json();
}

function getChatIdentity() {
  const profile = JSON.parse(localStorage.getItem('sofia-user-profile') || '{}');
  return profile.name && profile.name.trim() ? profile.name.trim() : 'You';
}

function renderHistory(messages, container, userLabel = 'You') {
  container.innerHTML = '';
  messages.forEach((message) => {
    const item = document.createElement('div');
    item.className = `message ${message.role}`;
    item.innerHTML = `<strong>${message.role === 'user' ? userLabel : 'SOFIA'}:</strong> ${message.text}`;
    container.appendChild(item);
  });
}

async function initDashboard() {
  try {
    const registry = await loadJSON('/core/registry');
    const knowledge = await loadJSON('/knowledge/status');
    const marketplace = await loadJSON('/marketplace/catalog');
    const mcp = await loadJSON('/mcp/tools');

    document.getElementById('registry-count').textContent = `${registry.modules.length} modules registered`;
    document.getElementById('knowledge-status').textContent = knowledge.status;
    document.getElementById('marketplace-status').textContent = `${marketplace.modules.length} modules available`;
    document.getElementById('mcp-status').textContent = `${mcp.registered_modules.length} MCP-visible modules`;

    const moduleList = document.getElementById('module-list');
    registry.modules.forEach((module) => {
      const item = document.createElement('li');
      item.textContent = module;
      moduleList.appendChild(item);
    });

    const capabilityList = document.getElementById('capability-list');
    Object.entries(registry.capabilities).forEach(([module, capabilities]) => {
      const item = document.createElement('li');
      item.innerHTML = `<strong>${module}</strong>: ${capabilities.join(', ')}`;
      capabilityList.appendChild(item);
    });

    const stackList = document.getElementById('stack-list');
    const stack = [
      { name: 'Qdrant', endpoint: 'http://localhost:6333' },
      { name: 'PostgreSQL', endpoint: 'http://localhost:5432' },
      { name: 'Redis', endpoint: 'http://localhost:6379' },
      { name: 'n8n', endpoint: 'http://localhost:5678' },
    ];

    stack.forEach((service) => {
      const card = document.createElement('div');
      card.className = 'stack-item';
      card.innerHTML = `<strong>${service.name}</strong><span>${service.endpoint}</span>`;
      stackList.appendChild(card);
    });

    const chatWindow = document.getElementById('chat-window');
    const input = document.getElementById('prompt-input');
    const askButton = document.getElementById('ask-button');
    const saveNameButton = document.getElementById('save-name-button');
    const displayNameInput = document.getElementById('display-name');
    const messages = JSON.parse(localStorage.getItem('sofia-chat') || '[]');
    let userLabel = getChatIdentity();
    displayNameInput.value = userLabel === 'You' ? '' : userLabel;
    renderHistory(messages, chatWindow, userLabel);

    saveNameButton.addEventListener('click', () => {
      const name = displayNameInput.value.trim();
      localStorage.setItem('sofia-user-profile', JSON.stringify({ name }));
      userLabel = name || 'You';
      renderHistory(messages, chatWindow, userLabel);
    });

    async function sendMessage() {
      const question = input.value.trim();
      if (!question) return;

      const nextMessages = [...messages, { role: 'user', text: question }];
      localStorage.setItem('sofia-chat', JSON.stringify(nextMessages));
      renderHistory(nextMessages, chatWindow, userLabel);
      input.value = '';

      try {
        const response = await fetch('/assistant/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question })
        });
        const raw = await response.text();
        let payload;
        try {
          payload = JSON.parse(raw);
        } catch {
          payload = { answer: `Server returned a non-JSON response (${response.status}): ${raw}` };
        }
        if (!response.ok) {
          payload.answer = payload.answer || `Request failed with status ${response.status}`;
        }
        const assistantMessage = { role: 'assistant', text: payload.answer };
        const finalMessages = [...nextMessages, assistantMessage];
        localStorage.setItem('sofia-chat', JSON.stringify(finalMessages));
        renderHistory(finalMessages, chatWindow, userLabel);
      } catch (error) {
        const errorMessage = { role: 'assistant', text: `Error: ${error.message}` };
        const finalMessages = [...nextMessages, errorMessage];
        localStorage.setItem('sofia-chat', JSON.stringify(finalMessages));
        renderHistory(finalMessages, chatWindow, userLabel);
      }
    }

    askButton.addEventListener('click', sendMessage);
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });
  } catch (error) {
    document.querySelector('.shell').innerHTML = `<div class="card error">Unable to load SOFIA dashboard: ${error.message}</div>`;
  }
}

initDashboard();
