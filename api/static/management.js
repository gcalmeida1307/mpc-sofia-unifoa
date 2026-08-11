const mgEsc = value => String(value || '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

let mgCurrentUser = null;
let mgDomainRoles = [];
const mgAccessStyle=document.createElement('link');mgAccessStyle.rel='stylesheet';mgAccessStyle.href='/ui/management-access.css?v=20260811';document.head.append(mgAccessStyle);

function mgCapabilityLabel(value){const labels={read:'Consultar dados',analyze:'Executar análises',manage:'Administrar a área',execute:'Executar ações',monitoring:'Consultar monitoramento',summary:'Ver resumo'};return String(value||'').split('.').slice(1).map(part=>labels[part]||part.replaceAll('_',' ')).join(' · ')}

function mgEnsureAccessDialog(){let dialog=document.querySelector('#domain-access-dialog');if(dialog)return dialog;dialog=document.createElement('dialog');dialog.id='domain-access-dialog';dialog.className='domain-access-dialog';dialog.innerHTML=`<form method="dialog"><header><div><p class="eyebrow">Permissões por domínio</p><h2 id="access-dialog-title">Acesso por área</h2><p>Escolha uma área, o papel e, se necessário, limite o acesso a uma unidade.</p></div><button type="button" class="ghost" data-close-access aria-label="Fechar">×</button></header><section id="current-domain-access" class="current-domain-access"></section><div id="domain-role-list" class="domain-role-list"></div><label class="domain-scope">Escopo ou unidade <input id="domain-unit-scope" maxlength="120" placeholder="Ex.: Unidade Centro (opcional)"><small>Deixe vazio para permitir todo o domínio.</small></label><footer><button type="button" class="ghost" data-close-access>Cancelar</button><button type="submit" id="save-domain-access">Salvar acesso</button></footer><p id="domain-access-message" class="auth-message" role="status"></p></form>`;document.body.append(dialog);dialog.querySelectorAll('[data-close-access]').forEach(button=>button.onclick=()=>dialog.close());return dialog}

function mgOpenDomainAccess(user){const dialog=mgEnsureAccessDialog(),rolesByDomain=Object.groupBy?Object.groupBy(mgDomainRoles,item=>item.domain_id):mgDomainRoles.reduce((groups,item)=>((groups[item.domain_id]||=[]).push(item),groups),{});dialog.querySelector('#access-dialog-title').textContent=`Acesso de ${user.display_name}`;dialog.querySelector('#current-domain-access').innerHTML=(user.domains||[]).map(item=>`<span><strong>${mgEsc(item.domain_id)}</strong>${mgEsc(item.role_name)}${item.unit_scope?` · ${mgEsc(item.unit_scope)}`:''}</span>`).join('')||'<span>Nenhuma área atribuída.</span>';dialog.querySelector('#domain-role-list').innerHTML=Object.entries(rolesByDomain).map(([domain,roles])=>`<fieldset><legend>${mgEsc(domain)}</legend>${roles.map(role=>`<label class="domain-role-option"><input type="radio" name="domain-role" value="${mgEsc(domain)}::${mgEsc(role.role)}"><span><strong>${mgEsc(role.display_name)}</strong><small>${role.parent_role?`Herda de ${mgEsc(role.parent_role)} · `:''}${(role.capabilities||[]).map(mgCapabilityLabel).join(' · ')}</small></span></label>`).join('')}</fieldset>`).join('');dialog.querySelector('#domain-unit-scope').value='';dialog.querySelector('#domain-access-message').textContent='';dialog.querySelector('form').onsubmit=async event=>{event.preventDefault();const selected=dialog.querySelector('input[name="domain-role"]:checked'),message=dialog.querySelector('#domain-access-message'),save=dialog.querySelector('#save-domain-access');if(!selected){message.className='auth-message error';message.textContent='Selecione um papel para continuar.';return}const [domain_id,role]=selected.value.split('::'),unit_scope=dialog.querySelector('#domain-unit-scope').value.trim()||null;save.disabled=true;save.textContent='Salvando…';try{await sofia.api(`/auth/admin/users/${user.id}/domain-membership`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({domain_id,role,unit_scope})});message.className='auth-message success';message.textContent='Acesso atualizado. As sessões anteriores foram revogadas.';setTimeout(async()=>{dialog.close();await mgLoad()},650)}catch(error){message.className='auth-message error';message.textContent=error.message}finally{save.disabled=false;save.textContent='Salvar acesso'}};dialog.showModal()}

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
    <div class="user-actions">${primaryAction}<button class="ghost" data-domain-access="${user.id}">Acesso por área</button>
      ${disabled ? '' : `<button class="ghost" data-revoke="${user.id}">Revogar sessões</button>`}
      ${isSelf || disabled ? '' : `<button class="ghost danger" data-disable="${user.id}">Desabilitar</button>`}</div>
  </article>`;
}

async function mgLoad() {
  const [requests, users, audit, domainRoles] = await Promise.all([
    sofia.api('/auth/admin/access-requests'), sofia.api('/auth/admin/users'), sofia.api('/auth/admin/audit?limit=5'),sofia.api('/auth/admin/domain-roles')
  ]);
  mgDomainRoles=domainRoles.roles||[];
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
  document.querySelectorAll('[data-domain-access]').forEach(button=>button.onclick=()=>{const user=(users.users||[]).find(item=>item.id===Number(button.dataset.domainAccess));if(!user||!mgDomainRoles.length)return alert('Nenhum papel de domínio disponível.');mgOpenDomainAccess(user)});
}

(async () => {
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.scrollTo(0, 0);
  mgCurrentUser = await sofia.initAuth();
  if (!mgCurrentUser || mgCurrentUser.role !== 'admin') return location.replace('/ui/index.html');
  document.body.classList.add('authorized');
  await mgLoad();
})().catch(error => alert(error.message));
