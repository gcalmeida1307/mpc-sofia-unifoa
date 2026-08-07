const kEsc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

(async()=>{
  await sofia.initAuth();
  const sourceList=document.querySelector('#sources'),layout=document.querySelector('.layout');
  const summary=document.createElement('section');summary.className='knowledge-summary';summary.innerHTML='<article class="panel"><span>Fontes cadastradas</span><strong id="knowledge-source-count">—</strong><small>Sites e provedores</small></article><article class="panel"><span>Formatos aceitos</span><strong>10+</strong><small>PDF, DOCX, Markdown e mais</small></article><article class="panel"><span>Pesquisa</span><strong>Híbrida</strong><small>Local + vetorial + Qdrant</small></article><article class="panel"><span>Estado</span><strong id="knowledge-state">—</strong><small>Base offline</small></article>';layout.before(summary);
  async function load(){
    const [providers,index]=await Promise.all([sofia.api('/knowledge/providers'),sofia.api('/knowledge/index')]);const items=providers.sources||providers.providers||[];
    document.querySelector('#knowledge-source-count').textContent=items.length;document.querySelector('#knowledge-state').textContent=index.status==='indexing-ready'?'Pronta':'Verificando';
    sourceList.innerHTML=items.map(item=>`<li class="knowledge-source"><span><strong>${kEsc(item.label||item.name)}</strong><small>${kEsc(item.url)}</small></span><em class="${item.enabled===false?'disabled':'active'}">${item.enabled===false?'Pausada':'Ativa'}</em></li>`).join('')||'<li class="empty-state">Nenhuma fonte cadastrada. Adicione a primeira fonte ao lado.</li>';
  }
  await load();
  document.querySelector('#refresh').onclick=async event=>{event.currentTarget.disabled=true;event.currentTarget.textContent='Atualizando…';try{await sofia.api('/knowledge/providers/refresh',{method:'POST'});await load()}finally{event.currentTarget.disabled=false;event.currentTarget.textContent='Atualizar fontes'}};
  document.querySelector('#source-form').onsubmit=async event=>{event.preventDefault();const name=document.querySelector('#label').value,url=document.querySelector('#url').value;await sofia.api('/knowledge/providers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,label:name,url,enabled:true})});event.currentTarget.reset();await load()};
  document.querySelector('#upload-form').onsubmit=async event=>{event.preventDefault();const input=document.querySelector('#file'),data=new FormData();data.append('file',input.files[0]);data.append('source',input.files[0].name);data.append('metadata','{}');await sofia.api('/knowledge/upload',{method:'POST',body:data});event.currentTarget.reset();alert('Documento recebido e encaminhado para indexação.')};
})().catch(error=>alert(error.message));
