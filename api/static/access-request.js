const message = document.querySelector('#message');
const username = document.querySelector('#access-user');
const displayName = document.querySelector('#access-name');
const email = document.querySelector('#access-email');
let autoValue = '';
let timer;

username.pattern = '[a-z][a-z0-9]*\\.[a-z][a-z0-9]*';
username.title = 'Use nome.sobrenome, sem espaços, acentos ou caracteres especiais';
const suggestions = document.createElement('div');
suggestions.className = 'username-options';
username.closest('label').append(suggestions);

async function post(body) {
  const response = await fetch('/auth/access-requests', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || 'Não foi possível enviar a solicitação.');
  return data;
}

async function loadOptions() {
  if (!displayName.value.trim() || !email.validity.valid) return;
  const params = new URLSearchParams({display_name: displayName.value.trim(), email: email.value.trim(), username: username.value.trim()});
  const response = await fetch(`/auth/access-requests/username-options?${params}`);
  if (!response.ok) return;
  const data = await response.json();
  if ((!username.value || username.value === autoValue) && data.suggestions[0]) {
    username.value = data.suggestions[0];
    autoValue = data.suggestions[0];
  }
  const state = data.normalized ? `<span class="availability ${data.available ? 'yes' : 'no'}">${data.available ? '✓ Disponível' : 'Indisponível'}</span>` : '';
  suggestions.innerHTML = `${state}${data.suggestions.length ? '<small>Sugestões disponíveis:</small>' : ''}<div>${data.suggestions.map(value => `<button type="button" data-username="${value}">${value}</button>`).join('')}</div>`;
  suggestions.querySelectorAll('[data-username]').forEach(button => button.onclick = () => {
    username.value = button.dataset.username; autoValue = button.dataset.username; loadOptions();
  });
}

function scheduleOptions() { clearTimeout(timer); timer = setTimeout(loadOptions, 250); }
displayName.addEventListener('input', scheduleOptions);
email.addEventListener('input', scheduleOptions);
username.addEventListener('input', () => { if (username.value !== autoValue) autoValue = ''; scheduleOptions(); });

document.querySelector('#access-form').onsubmit = async event => {
  event.preventDefault();
  const button = event.submitter; button.disabled = true; message.className = 'auth-message'; message.textContent = 'Enviando solicitação…';
  try {
    await post({username: username.value.trim(), display_name: displayName.value.trim(), email: email.value.trim(), reason: document.querySelector('#access-reason').value.trim()});
    event.currentTarget.hidden = true; document.querySelector('#request-success').hidden = false; message.textContent = '';
  } catch (error) { message.className = 'auth-message error'; message.textContent = error.message; await loadOptions(); }
  finally { button.disabled = false; }
};
