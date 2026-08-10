const sofia=(()=>{
  const token=localStorage.getItem('sofia-token'),themeKey='sofia-theme';
  function applyTheme(theme){document.documentElement.dataset.theme=theme;document.documentElement.style.colorScheme=theme;localStorage.setItem(themeKey,theme)}
  const savedTheme=localStorage.getItem(themeKey);applyTheme(savedTheme==='light'||savedTheme==='dark'?savedTheme:(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'));
  async function api(path,options={}){const headers={...(options.headers||{})};if(token)headers.Authorization=`Bearer ${token}`;const response=await fetch(path,{...options,headers});const data=await response.json().catch(()=>({}));if(response.status===401){localStorage.removeItem('sofia-token');if(!path.includes('/login'))location.href='/ui/login.html'}if(!response.ok)throw new Error(data.detail||'Falha na solicitação');return data}
  function buildNavigation(nav,user){
    const links=[
      ['Visão geral','Executivo','⌂','/ui/index.html',true],
      ['Visão geral','Painéis','▦','/ui/dashboards.html',true],
      ['Operações','Analytics','▥','/ui/analytics.html',true],['Operações','Ambiente','⌁','/ui/analista.html',true],
      ['Inteligência','Conversar','✦','/ui/conversar.html',true],['Inteligência','Diário e agentes','◉','/ui/inteligencia.html',user.role==='admin'],
      ['Conhecimento','Fontes e RAGs','▤','/ui/base.html',user.role==='admin'],
      ['Automação','Fluxos','⌘','/ui/automacao.html',user.role==='admin'],
      ['Administração','Gestão','⚙','/ui/gestao.html',user.role==='admin']
    ];
    const visible=links.filter(([, , , ,show])=>show),groups=[...new Set(visible.map(item=>item[0]))];
    nav.innerHTML=groups.map(group=>`<section class="nav-group"><small>${group}</small>${visible.filter(item=>item[0]===group).map(([,label,icon,href])=>`<a href="${href}" title="${label}" class="${location.pathname===href?'active':''}"><i aria-hidden="true">${icon}</i><span>${label}</span></a>`).join('')}</section>`).join('');
    let mobile=document.querySelector('.mobile-nav');if(!mobile){mobile=document.createElement('nav');mobile.className='mobile-nav';mobile.setAttribute('aria-label','Navegação rápida');document.body.append(mobile)}
    const quick=visible.filter(item=>['/ui/index.html','/ui/dashboards.html','/ui/analista.html','/ui/conversar.html'].includes(item[3]));
    mobile.innerHTML=quick.map(([,label,icon,href])=>`<a href="${href}" class="${location.pathname===href?'active':''}"><i>${icon}</i><span>${label}</span></a>`).join('')+'<button type="button" data-mobile-more><i>☰</i><span>Mais</span></button>';
    mobile.querySelector('[data-mobile-more]').onclick=()=>document.body.classList.toggle('nav-open');
  }
  async function initAuth(){
    if('scrollRestoration' in history)history.scrollRestoration='manual';window.scrollTo(0,0);
    if(!token){location.href='/ui/login.html';return null}
    const user=await api('/auth/me'),profilePage=location.pathname.endsWith('/perfil.html');if(user.email_required&&!profilePage){location.href='/ui/perfil.html';return null}
    document.querySelectorAll('[data-admin]').forEach(element=>element.hidden=user.role!=='admin');const nav=document.querySelector('.topbar nav');if(nav){buildNavigation(nav,user);document.body.classList.remove('nav-collapsed','nav-open');localStorage.removeItem('sofia-nav-collapsed');let toggle=document.querySelector('.nav-toggle');if(!toggle){toggle=document.createElement('button');toggle.type='button';toggle.className='nav-toggle';toggle.setAttribute('aria-label','Abrir navegação');toggle.setAttribute('aria-expanded','false');toggle.innerHTML='<span></span><span></span><span></span>';document.querySelector('.topbar .brand').after(toggle)}const setMenu=open=>{document.body.classList.toggle('nav-open',open);toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Fechar navegação':'Abrir navegação')};toggle.onclick=event=>{event.stopPropagation();setMenu(!document.body.classList.contains('nav-open'))};nav.onclick=event=>{if(event.target.closest('a'))setMenu(false)};document.addEventListener('keydown',event=>{if(event.key==='Escape')setMenu(false)});document.addEventListener('click',event=>{if(document.body.classList.contains('nav-open')&&!nav.contains(event.target)&&event.target!==toggle)setMenu(false)})}
    const identity=document.querySelector('.identity');identity.innerHTML='';const trigger=document.createElement('button');trigger.className='identity-trigger';trigger.type='button';trigger.textContent=`${user.display_name} · ${user.role}`;trigger.setAttribute('aria-expanded','false');const menu=document.createElement('div');menu.className='identity-menu';menu.hidden=true;
    const profile=document.createElement('a');profile.href='/ui/perfil.html';profile.textContent='Meu perfil';menu.append(profile);
    const theme=document.createElement('button');theme.type='button';theme.className='identity-menu-action';theme.textContent=document.documentElement.dataset.theme==='dark'?'Usar tema claro':'Usar tema escuro';theme.onclick=()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';applyTheme(next);theme.textContent=next==='dark'?'Usar tema claro':'Usar tema escuro'};menu.append(theme);
    if(user.role==='admin'){const management=document.createElement('a');management.href='/ui/gestao.html';management.textContent='Administração';menu.append(management)}
    const logout=document.createElement('button');logout.id='logout';logout.className='identity-menu-action';logout.textContent='Sair';logout.onclick=async()=>{await api('/auth/logout',{method:'POST'});localStorage.removeItem('sofia-token');location.href='/ui/login.html'};menu.append(logout);identity.append(trigger,menu);
    trigger.onclick=event=>{event.stopPropagation();menu.hidden=!menu.hidden;trigger.setAttribute('aria-expanded',String(!menu.hidden))};document.addEventListener('click',event=>{if(!identity.contains(event.target)){menu.hidden=true;trigger.setAttribute('aria-expanded','false')}});return user
  }
  return{api,initAuth}
})();
