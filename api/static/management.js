const mgEsc = value => String(value || '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

let mgCurrentUser = null;

function mgRenderAudit(entries) {
  document.querySelector('#management-audit-body').innerHTML = (entries || []).slice(0,5).map(entry => `
    <tr><td>${new Date(entry.created_at).toLocaleString()}</td><td>${mgEsc(entry.username || 'sistema')}</td>
    <td>${mgEsc(entry.action)}</td><td><span class="audit-result ${entry.success ? 'success' : 'failure'}">${entry.success ? 'Sucesso' : 'Falha'}</span></td>
    <td>${mgEsc(entry.ip_address || 'local')}</td></tr>`).join('') || '<tr><td colspan="5">Nenhum evento registrado.</td></tr>';
}

function mgStatus(user) {
  if (user.status === 'revoked') return '<span class="user-status revoked">Desabilitado</span>';
  if (user.status === 'pending') return '<span class="user-status pending">Aguardando primeiro acesso</span>';
  if (user.password_reset_required) return '<span class="user-status pending">Redefinição pendente</span>';
  return '<span class="user-status active">Acesso ativo</span>';
}

function mgUserCard(user) {
  const isSelf = user.id === mgCurrentUser.id;
  const disabled = user.status === 'revoked';
  const primaryAction = user.status === 'pending'
    ? `<button class="ghost" data-activation="${user.id}">Reenviar ativação</button>`
    : disabled ? `<button class="ghost" data-enable="${user.id}">Reativar usuário</button>`
      : `<button class="ghost" data-reset="${user.id}">Exigir nova senha</button>
         ${isSelf ? '' : `<button class="ghost danger" data-recover="${user.id}">Reconfigurar acesso</button>`}`;
  return `<article class="management-user ${disabled ? 'is-disabled' : ''}">
    <div class="user-summary"><strong>${mgEsc(user.display_name)}</strong>
      <small><b>Login:</b> ${mgEsc(user.username)}</small><small>${mgEsc(user.email || 'E-mail pendente')}</small>${mgStatus(user)}</div>
    <div class="user-role"><label>Perfil<select data-role="${user.id}" ${(isSelf || disabled) ? 'disabled' : ''}>
      <option value="user" ${user.role === 'user' ? 'selected' : ''}>Usuário</option>
      <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Administrador</option></select></label></div>
    <div class="user-actions">${primaryAction}
      ${disabled ? '' : `<button class="ghost" data-revoke="${user.id}">Revogar sessões</button>`}
      ${isSelf || disabled ? '' : `<button class="ghost danger" data-disable="${user.id}">Desabilitar</button>`}</div>
  </article>`;
}

async function mgLoad() {
  const [requests, users, audit] = await Promise.all([
    sofia.api('/auth/admin/access-requests'), sofia.api('/auth/admin/users'), sofia.api('/auth/admin/audit?limit=5')
  ]);
  mgRenderAudit(audit.entries);
  document.querySelector('#management-requests').innerHTML = (requests.requests || []).filter(x => x.status === 'pending').map(x => `
    <article class="access-request"><div><strong>${mgEsc(x.display_name)}</strong><small>${mgEsc(x.username)}</small>
    <small>${mgEsc(x.email)}</small><p>${mgEsc(x.reason || 'Sem justificativa informada.')}</p></div>
    <button data-approve="${x.id}">Aprovar</button></article>`).join('') || '<p class="empty-state">Sem solicitações pendentes.</p>';
  document.querySelector('#management-users').innerHTML = (users.users || []).map(mgUserCard).join('');

  document.querySelectorAll('[data-approve]').forEach(button => button.onclick = async () => {
    const result = await sofia.api(`/auth/admin/access-requests/${button.dataset.approve}/approve`, {method: 'POST'});
    if (result.email_sent) alert('Acesso aprovado. O código de ativação foi enviado ao e-mail do usuário.');
    else prompt('SMTP indisponível ou envio falhou. Entregue este código por canal seguro:', result.setup_token);
    await mgLoad();
  });
  document.querySelectorAll('[data-role]').forEach(select => select.onchange = async () => {
    if (!confirm(`Alterar o perfil para ${select.options[select.selectedIndex].text} e revogar as sessões?`)) return mgLoad();
    try { await sofia.api(`/auth/admin/users/${select.dataset.role}/role`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({role: select.value})}); }
    catch (error) { alert(error.message); }
    await mgLoad();
  });
  document.querySelectorAll('[data-activation]').forEach(button => button.onclick = async () => {
    if (!confirm('Invalidar o código anterior e gerar uma nova ativação?')) return;
    const result = await sofia.api(`/auth/admin/users/${button.dataset.activation}/resend-activation`, {method: 'POST'});
    if (result.email_sent) alert('Novo código enviado ao e-mail do usuário.');
    else prompt('SMTP indisponível ou envio falhou. Entregue este código por canal seguro:', result.setup_token);
    await mgLoad();
  });
  document.querySelectorAll('[data-recover]').forEach(button => button.onclick = async () => {
    if (!confirm('Revogar sessões, invalidar senha e TOTP e obrigar um novo primeiro acesso?')) return;
    const result = await sofia.api(`/auth/admin/users/${button.dataset.recover}/recover-access`, {method: 'POST'});
    if (result.email_sent) alert('Acesso reconfigurado. O novo código foi enviado ao e-mail do usuário.');
    else prompt('Acesso reconfigurado. Entregue este código único por canal seguro:', result.setup_token);
    await mgLoad();
  });
  document.querySelectorAll('[data-reset]').forEach(button => button.onclick = async () => {
    if (!confirm('Revogar sessões e gerar uma redefinição temporária?')) return;
    const result = await sofia.api(`/auth/admin/users/${button.dataset.reset}/require-password-reset`, {method: 'POST'});
    if (result.email_sent) alert('As instruções foram enviadas ao e-mail do usuário.');
    else prompt('SMTP indisponível. Entregue este token por canal seguro:', result.reset_token);
    await mgLoad();
  });
  document.querySelectorAll('[data-revoke]').forEach(button => button.onclick = async () => {
    await sofia.api(`/auth/admin/users/${button.dataset.revoke}/revoke-sessions`, {method: 'POST'});
    alert('Sessões revogadas.');
  });
  document.querySelectorAll('[data-disable]').forEach(button => button.onclick = async () => {
    if (!confirm('Desabilitar este usuário? Os dados e a auditoria serão preservados, mas o acesso e as sessões serão bloqueados.')) return;
    await sofia.api(`/auth/admin/users/${button.dataset.disable}/disable`, {method: 'POST'});
    await mgLoad();
  });
  document.querySelectorAll('[data-enable]').forEach(button => button.onclick = async () => {
    if (!confirm('Reativar este usuário?')) return;
    await sofia.api(`/auth/admin/users/${button.dataset.enable}/enable`, {method: 'POST'});
    await mgLoad();
  });
}

(async () => {
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.scrollTo(0, 0);
  mgCurrentUser = await sofia.initAuth();
  if (!mgCurrentUser || mgCurrentUser.role !== 'admin') return location.replace('/ui/index.html');
  document.body.classList.add('authorized');
  await mgLoad();
})().catch(error => alert(error.message));
