async function loadJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${url} failed (${response.status}): ${text.slice(0, 180)}`);
  }
  return response.json();
}

async function safeLoad(url, fallback) {
  try {
    return await loadJSON(url);
  } catch (error) {
    console.warn('SOFIA UI load warning:', error.message);
    return fallback;
  }
}

function initScrollMenu() {
  const links = Array.from(document.querySelectorAll('#main-menu a[data-menu]'));
  const sections = Array.from(document.querySelectorAll('[data-section]'));
  if (!links.length || !sections.length) return;

  const linkById = new Map(links.map((link) => [link.dataset.menu, link]));

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
      if (!visible.length) return;

      const id = visible[0].target.getAttribute('data-section');
      links.forEach((link) => link.classList.remove('active'));
      const activeLink = linkById.get(id);
      if (activeLink) activeLink.classList.add('active');
    },
    { rootMargin: '-25% 0px -55% 0px', threshold: [0.2, 0.4, 0.6] }
  );

  sections.forEach((section) => observer.observe(section));
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
    const registry = await safeLoad('/core/registry', { modules: [], capabilities: {} });
    const knowledge = await safeLoad('/knowledge/status', { status: 'unavailable' });
    const marketplace = await safeLoad('/marketplace/catalog', { modules: [] });
    const mcp = await safeLoad('/mcp/tools', { registered_modules: [] });
    const aiPanel = await safeLoad('/engine/ai/panel?hours=24', {
      kpis: {},
      intelligence: { ai: {}, hypothesis: {}, learning: {} },
      group_trends_30d: [],
      recent_audits: [],
      recent_investigations: []
    });
    const agents = await safeLoad('/engine/agents/status', { agents: [] });

    document.getElementById('registry-count').textContent = `${(registry.modules || []).length} modules registered`;
    document.getElementById('knowledge-status').textContent = knowledge.status;
    document.getElementById('marketplace-status').textContent = `${(marketplace.modules || []).length} modules available`;
    document.getElementById('mcp-status').textContent = `${(mcp.registered_modules || []).length} MCP-visible modules`;

    const moduleList = document.getElementById('module-list');
    (registry.modules || []).forEach((module) => {
      const item = document.createElement('li');
      item.textContent = module;
      moduleList.appendChild(item);
    });

    if ((registry.modules || []).length === 0) {
      const item = document.createElement('li');
      item.textContent = 'No modules loaded yet.';
      moduleList.appendChild(item);
    }

    const capabilityList = document.getElementById('capability-list');
    Object.entries(registry.capabilities || {}).forEach(([module, capabilities]) => {
      const item = document.createElement('li');
      item.innerHTML = `<strong>${module}</strong>: ${capabilities.join(', ')}`;
      capabilityList.appendChild(item);
    });

    if (Object.keys(registry.capabilities || {}).length === 0) {
      const item = document.createElement('li');
      item.textContent = 'Capabilities unavailable.';
      capabilityList.appendChild(item);
    }

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

    const marketplaceGrid = document.getElementById('marketplace-grid');
    (marketplace.modules || []).forEach((module) => {
      const card = document.createElement('article');
      card.className = 'marketplace-item';
      card.innerHTML = `
        <h4>${module.name}</h4>
        <span class="marketplace-tag">${module.category}</span>
      `;
      marketplaceGrid.appendChild(card);
    });

    if ((marketplace.modules || []).length === 0) {
      const card = document.createElement('article');
      card.className = 'marketplace-item';
      card.innerHTML = `<h4>Marketplace unavailable</h4><span class="marketplace-tag">retry later</span>`;
      marketplaceGrid.appendChild(card);
    }

    const aiMetricsList = document.getElementById('ai-metrics-list');
    const kpis = aiPanel.kpis || {};
    const intelligence = aiPanel.intelligence || {};
    const hypothesis = intelligence.hypothesis || {};
    const learning = intelligence.learning || {};
    [
      `Perguntas: ${kpis.total_questions ?? 0}`,
      `Latencia media: ${kpis.avg_latency_ms ?? 0} ms`,
      `Confidence media: ${kpis.avg_confidence ?? 0}`,
      `Uso de LLM: ${Math.round((kpis.llm_usage_rate ?? 0) * 100)}%`,
      `Aprovacao do Critic: ${Math.round((kpis.critic_approval_rate ?? 0) * 100)}%`,
      `Runs de hipoteses: ${hypothesis.total_runs ?? 0}`,
      `Hipotese confirmada: ${Math.round((hypothesis.confirmed_rate ?? 0) * 100)}%`,
      `Ciclos de aprendizado: ${learning.total_cycles ?? 0}`,
      `Reuso de aprendizado: ${Math.round((learning.reuse_rate ?? 0) * 100)}%`,
      `Tokens in/out: ${kpis.total_tokens_in ?? 0} / ${kpis.total_tokens_out ?? 0}`,
      `Custo estimado USD: ${(kpis.estimated_cost_usd ?? 0).toFixed ? kpis.estimated_cost_usd.toFixed(6) : kpis.estimated_cost_usd}`,
    ].forEach((itemText) => {
      const item = document.createElement('li');
      item.textContent = itemText;
      aiMetricsList.appendChild(item);
    });

    const aiGroupTrendsList = document.getElementById('ai-group-trends-list');
    (aiPanel.group_trends_30d || []).forEach((trend) => {
      const item = document.createElement('li');
      item.textContent = `${trend.group}: ${trend.occurrences} ocorrencias (${trend.unique_hosts} hosts)`;
      aiGroupTrendsList.appendChild(item);
    });

    if ((aiPanel.group_trends_30d || []).length === 0) {
      const item = document.createElement('li');
      item.textContent = 'No trend data yet.';
      aiGroupTrendsList.appendChild(item);
    }

    const aiAuditList = document.getElementById('ai-audit-list');
    (aiPanel.recent_audits || []).slice(0, 12).forEach((audit) => {
      const item = document.createElement('li');
      item.textContent = `${audit.tool} | success=${audit.success} | ${audit.duration}s`;
      aiAuditList.appendChild(item);
    });

    if ((aiPanel.recent_audits || []).length === 0) {
      const item = document.createElement('li');
      item.textContent = 'No audit records yet.';
      aiAuditList.appendChild(item);
    }

    const investigationsList = document.getElementById('ai-investigations-list');
    (aiPanel.recent_investigations || []).slice(0, 8).forEach((itemData) => {
      const item = document.createElement('li');
      const selectedHypothesis = itemData.hypothesis?.selected_hypothesis || 'n/a';
      item.textContent = `[${itemData.severity}] ${itemData.watcher} - ${selectedHypothesis}`;
      investigationsList.appendChild(item);
    });

    if ((aiPanel.recent_investigations || []).length === 0) {
      const item = document.createElement('li');
      item.textContent = 'No autonomous investigations yet.';
      investigationsList.appendChild(item);
    }

    const agentsList = document.getElementById('ai-agents-list');
    (agents.agents || []).forEach((agent) => {
      const item = document.createElement('li');
      item.textContent = `${agent.name} | budget=${agent.tool_budget?.max_tools ?? 0} tools`;
      agentsList.appendChild(item);
    });

    if ((agents.agents || []).length === 0) {
      const item = document.createElement('li');
      item.textContent = 'No specialist agents registered.';
      agentsList.appendChild(item);
    }

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

    initScrollMenu();
  } catch (error) {
    const shell = document.querySelector('.shell');
    if (shell) {
      const warning = document.createElement('div');
      warning.className = 'card error';
      warning.textContent = `Dashboard loaded with partial data: ${error.message}`;
      shell.prepend(warning);
    }
  }
}

initDashboard();
