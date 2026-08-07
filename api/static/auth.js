const sofia=(()=>{
  const token=localStorage.getItem('sofia-token'),themeKey='sofia-theme';
  function applyTheme(theme){document.documentElement.dataset.theme=theme;document.documentElement.style.colorScheme=theme;localStorage.setItem(themeKey,theme)}
  const savedTheme=localStorage.getItem(themeKey);applyTheme(savedTheme==='light'||savedTheme==='dark'?savedTheme:(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'));
  async function api(path,options={}){const headers={...(options.headers||{})};if(token)headers.Authorization=`Bearer ${token}`;const response=await fetch(path,{...options,headers});const data=await response.json().catch(()=>({}));if(response.status===401){localStorage.removeItem('sofia-token');if(!path.includes('/login'))location.href='/ui/login.html'}if(!response.ok)throw new Error(data.detail||'Falha na solicitação');return data}
  function buildNavigation(nav,user){
    const links=[
      ['Executivo','/ui/index.html',true],['Analytics','/ui/analytics.html',true],['Operações','/ui/analista.html',true],['Conversar','/ui/conversar.html',true],
      ['Inteligência','/ui/inteligencia.html',user.role==='admin'],['Conhecimento','/ui/base.html',user.role==='admin'],['Automações','/ui/automacao.html',user.role==='admin']
    ];
    nav.innerHTML=links.filter(([, ,visible])=>visible).map(([label,href])=>`<a href="${href}" class="${location.pathname===href?'active':''}">${label}</a>`).join('');
  }
  async function initAuth(){
    if(!token){location.href='/ui/login.html';return null}
    const user=await api('/auth/me'),profilePage=location.pathname.endsWith('/perfil.html');if(user.email_required&&!profilePage){location.href='/ui/perfil.html';return null}
    document.querySelectorAll('[data-admin]').forEach(element=>element.hidden=user.role!=='admin');const nav=document.querySelector('.topbar nav');if(nav)buildNavigation(nav,user);
    const identity=document.querySelector('.identity');identity.innerHTML='';const trigger=document.createElement('button');trigger.className='identity-trigger';trigger.type='button';trigger.textContent=`${user.display_name} · ${user.role}`;trigger.setAttribute('aria-expanded','false');const menu=document.createElement('div');menu.className='identity-menu';menu.hidden=true;
    const profile=document.createElement('a');profile.href='/ui/perfil.html';profile.textContent='Meu perfil';menu.append(profile);
    const theme=document.createElement('button');theme.type='button';theme.className='identity-menu-action';theme.textContent=document.documentElement.dataset.theme==='dark'?'Usar tema claro':'Usar tema escuro';theme.onclick=()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';applyTheme(next);theme.textContent=next==='dark'?'Usar tema claro':'Usar tema escuro'};menu.append(theme);
    if(user.role==='admin'){const management=document.createElement('a');management.href='/ui/gestao.html';management.textContent='Administração';menu.append(management)}
    const logout=document.createElement('button');logout.id='logout';logout.className='identity-menu-action';logout.textContent='Sair';logout.onclick=async()=>{await api('/auth/logout',{method:'POST'});localStorage.removeItem('sofia-token');location.href='/ui/login.html'};menu.append(logout);identity.append(trigger,menu);
    trigger.onclick=event=>{event.stopPropagation();menu.hidden=!menu.hidden;trigger.setAttribute('aria-expanded',String(!menu.hidden))};document.addEventListener('click',event=>{if(!identity.contains(event.target)){menu.hidden=true;trigger.setAttribute('aria-expanded','false')}});return user
  }
  return{api,initAuth}
})();
