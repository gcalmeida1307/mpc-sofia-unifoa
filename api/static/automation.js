let graphId=null;
let nodes=[];
let edges=[];
let selected=[];
let catalog=[];
let connectingSource=null;
let pendingPlacement=null;
let lastCatalogDragAt=0;
const recommendations={
  trigger:['zabbix','offline','grafana'],
  zabbix:['grafana','prometheus','loki'],
  grafana:['prometheus','loki','postgres'],
  prometheus:['loki','correlate'],
  loki:['postgres','git','correlate'],
  postgres:['correlate'],
  offline:['claude','correlate'],
  claude:['offline','correlate'],
  git:['correlate'],
  jira:['correlate'],
  correlate:['report']
};
const NODE_WIDTH=190,NODE_HEIGHT=104;
const WORKFLOW_TEMPLATES={
  network:{title:'Investigar incidente de rede',description:'Localiza alertas, correlaciona horários e explica evidências.',types:['trigger','zabbix','correlate','claude','report']},
  overnight:{title:'Resumo da madrugada',description:'Consolida alertas, métricas e logs do período noturno.',types:['trigger','zabbix','grafana','loki','correlate','report']},
  capacity:{title:'Risco de capacidade',description:'Compara métricas e banco para destacar saturação e tendência.',types:['trigger','prometheus','postgres','correlate','claude','report']},
  executive:{title:'Relatório executivo',description:'Transforma alertas e conhecimento local em resumo objetivo.',types:['trigger','zabbix','knowledge','claude','report']},
  sql:{title:'Investigar lentidão SQL',description:'Correlaciona métricas, logs, banco e eventos para explicar degradação.',types:['trigger','grafana','prometheus','loki','postgres','correlate','report']}
};

const byId=id=>document.getElementById(id);
function createNodeId(){
  if(globalThis.crypto&&typeof globalThis.crypto.randomUUID==='function')return globalThis.crypto.randomUUID();
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,char=>{
    const value=Math.floor(Math.random()*16);
    return (char==='x'?value:(value&3)|8).toString(16);
  });
}
function persistDraft(){localStorage.setItem('sofia-automation-draft',JSON.stringify({graphId,nodes,edges,name:byId('graph-name')?.value||'',description:byId('graph-description')?.value||''}))}
function restoreDraft(){try{const draft=JSON.parse(localStorage.getItem('sofia-automation-draft')||'null');if(!draft)return;graphId=draft.graphId||null;nodes=Array.isArray(draft.nodes)?draft.nodes:[];edges=Array.isArray(draft.edges)?draft.edges:[];if(draft.name)byId('graph-name').value=draft.name;if(draft.description)byId('graph-description').value=draft.description}catch{localStorage.removeItem('sofia-automation-draft')}}
const escapeHtml=value=>String(value||'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

function connector(type){return catalog.find(item=>item.type===type)||{label:type,status:'unknown',category:'Outro'}}
function buildTemplate(key){
  const template=WORKFLOW_TEMPLATES[key];if(!template)return;
  nodes=template.types.filter(type=>catalog.some(item=>item.type===type)).map((type,index)=>({id:createNodeId(),type,label:connector(type).label,x:45+(index%3)*220,y:45+Math.floor(index/3)*130,config:{}}));
  edges=nodes.slice(0,-1).map((node,index)=>({id:createNodeId(),source:node.id,target:nodes[index+1].id}));
  graphId=null;byId('graph-name').value=template.title;byId('graph-description').value=template.description;persistDraft();renderGraph();showSuggestions(nodes.at(-1));
}
function ensureAutomationExperience(){
  if(!byId('automation-templates')){const section=document.createElement('section');section.id='automation-templates';section.className='automation-templates';section.innerHTML=`<header><span><p class="eyebrow">Comece rápido</p><h2>Templates de investigação</h2><small>Escolha um objetivo e personalize os blocos.</small></span></header><div>${Object.entries(WORKFLOW_TEMPLATES).map(([key,item])=>`<button type="button" data-template="${key}"><i>✦</i><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.description)}</small></span><b>Usar</b></button>`).join('')}</div>`;document.querySelector('.automation-toolbar').before(section);section.querySelectorAll('[data-template]').forEach(button=>button.onclick=()=>buildTemplate(button.dataset.template))}
  if(!byId('node-drawer')){const drawer=document.createElement('aside');drawer.id='node-drawer';drawer.className='node-drawer';drawer.hidden=true;drawer.innerHTML='<div class="drawer-backdrop" data-close-drawer></div><section><header><span><small>CONFIGURAR BLOCO</small><h2 id="drawer-title">Bloco</h2></span><button class="ghost" type="button" data-close-drawer aria-label="Fechar">×</button></header><p id="drawer-description"></p><form id="node-config-form"></form></section>';document.body.append(drawer);drawer.querySelectorAll('[data-close-drawer]').forEach(button=>button.onclick=()=>{drawer.hidden=true})}
}
function openNodeSettings(id){
  const node=nodes.find(item=>item.id===id);if(!node)return;const meta=connector(node.type),drawer=byId('node-drawer'),config=node.config||{};byId('drawer-title').textContent=meta.label;byId('drawer-description').textContent=meta.description||'Defina como este bloco participa do fluxo.';
  const zabbix=node.type==='zabbix',form=byId('node-config-form');form.innerHTML=`<label>Nome no fluxo<input name="label" value="${escapeHtml(node.label||meta.label)}" required></label>${zabbix?`<label>Operação<select name="operation"><option value="problems">Problemas ativos</option><option value="history" ${config.operation==='history'?'selected':''}>Histórico de triggers</option><option value="hosts" ${config.operation==='hosts'?'selected':''}>Hosts e disponibilidade</option></select></label><label>Grupo ou escopo<input name="scope" value="${escapeHtml(config.scope||'Todos os grupos autorizados')}" placeholder="Ex.: Switches"></label><label>Período<select name="period"><option value="active">Agora</option><option value="24h" ${config.period==='24h'?'selected':''}>Últimas 24 horas</option><option value="7d" ${config.period==='7d'?'selected':''}>Últimos 7 dias</option></select></label><label>Severidade mínima<select name="severity"><option>Informação</option><option ${config.severity==='Aviso'?'selected':''}>Aviso</option><option ${config.severity==='Médio'?'selected':''}>Médio</option><option ${config.severity==='Alto'?'selected':''}>Alto</option></select></label>`:`<label>Objetivo do bloco<textarea name="objective" placeholder="Descreva o resultado esperado">${escapeHtml(config.objective||'')}</textarea></label>`}<div class="drawer-status"><i class="status-light ${meta.status==='active'?'online':'offline'}"></i><span><strong>${meta.status==='active'?'Conector disponível':'Configuração externa necessária'}</strong><small>${escapeHtml(meta.category)}</small></span></div><button>Salvar configuração</button>`;
  form.onsubmit=event=>{event.preventDefault();const values=Object.fromEntries(new FormData(form));node.label=String(values.label||meta.label);delete values.label;node.config=values;persistDraft();renderGraph();drawer.hidden=true};drawer.hidden=false;form.querySelector('input,select,textarea')?.focus();
}
queueMicrotask(ensureAutomationExperience);
function canvasBounds(){
  const canvas=byId('graph-canvas');
  return {width:Math.max(0,canvas.clientWidth-NODE_WIDTH-8),height:Math.max(0,canvas.clientHeight-NODE_HEIGHT-8)};
}
function clampPosition(x,y){const b=canvasBounds();return{x:Math.max(8,Math.min(b.width,x)),y:Math.max(8,Math.min(b.height,y))}}
function addNode(item,position=null,sourceId=null){
  pendingPlacement=null;byId('graph-canvas')?.classList.remove('placement-active');document.querySelectorAll('.connector-card').forEach(x=>x.classList.remove('placement-selected'));
  const count=nodes.length;
  const pos=clampPosition(position?.x??40+(count%4)*210,position?.y??45+Math.floor(count/4)*125);
  const node={id:createNodeId(),type:item.type,label:item.label,x:pos.x,y:pos.y};
  nodes.push(node);
  if(sourceId&&!edges.some(e=>e.source===sourceId&&e.target===node.id))edges.push({id:createNodeId(),source:sourceId,target:node.id});
  connectingSource=null;persistDraft();renderGraph();showSuggestions(node);return node;
}
function toggleNode(id){selected=selected.includes(id)?selected.filter(x=>x!==id):[...selected,id].slice(-2);renderGraph()}
function removeNode(id){nodes=nodes.filter(n=>n.id!==id);edges=edges.filter(e=>e.source!==id&&e.target!==id);selected=selected.filter(x=>x!==id);if(connectingSource===id)connectingSource=null;persistDraft();renderGraph();showSuggestions()}
function makeConnection(source,target){
  if(!source||!target||source===target)return;
  if(!edges.some(e=>e.source===source&&e.target===target))edges.push({id:createNodeId(),source,target});
  connectingSource=null;selected=[];persistDraft();renderGraph();showSuggestions(nodes.find(n=>n.id===target));
}
function connectSelected(){if(selected.length!==2)return alert('Selecione dois blocos na ordem origem → destino.');makeConnection(selected[0],selected[1])}
function showSuggestions(node){
  const host=byId('connection-suggestions');if(!host)return;
  if(!node){host.innerHTML='<small>Adicione um bloco para ver sugestões de conexão.</small>';return}
  const types=(recommendations[node.type]||[]).filter(type=>catalog.some(item=>item.type===type));
  host.innerHTML=types.length?'<small>Conectar depois de <b>'+escapeHtml(node.label)+'</b>:</small>'+types.map(type=>'<button class="suggestion-chip" data-type="'+type+'">+ '+escapeHtml(connector(type).label)+'</button>').join(''):'<small>Este bloco normalmente encerra o fluxo.</small>';
  host.querySelectorAll('.suggestion-chip').forEach(button=>button.onclick=()=>addNode(connector(button.dataset.type),{x:node.x+220,y:node.y},node.id));
}
function renderGraph(){
  const host=byId('graph-nodes');host.innerHTML='';
  const empty=byId('canvas-empty');if(empty){empty.hidden=nodes.length>0;empty.textContent='Arraste um bloco para começar'}
  nodes.forEach(node=>{
    Object.assign(node,clampPosition(node.x,node.y));
    const meta=connector(node.type),el=document.createElement('article');
    el.className=`graph-node ${selected.includes(node.id)?'selected':''} ${connectingSource===node.id?'connecting':''} ${node.runtime||''}`;el.dataset.id=node.id;el.style.left=`${node.x}px`;el.style.top=`${node.y}px`;
    el.innerHTML=`<button class="node-port node-input" title="Entrada" aria-label="Conectar na entrada"></button><button class="node-remove" title="Remover">×</button><button class="node-config" title="Configurar bloco" aria-label="Configurar bloco">⚙</button><small>${escapeHtml(meta.category)}</small><strong>${escapeHtml(node.label||meta.label)}</strong><span class="connector-status ${meta.status}">${meta.status==='active'?'pronto':'configurar'}</span><button class="node-port node-output" title="Saída" aria-label="Iniciar conexão pela saída"></button>`;
    let moved=false;
    el.onclick=e=>{if(!moved&&!e.target.closest('button')){toggleNode(node.id);showSuggestions(node)}};
    el.querySelector('.node-remove').onclick=e=>{e.stopPropagation();removeNode(node.id)};
    el.querySelector('.node-config').onclick=e=>{e.stopPropagation();openNodeSettings(node.id)};
    el.querySelector('.node-output').onclick=e=>{e.stopPropagation();connectingSource=node.id;selected=[];renderGraph();showSuggestions(node)};
    el.querySelector('.node-input').onclick=e=>{e.stopPropagation();if(connectingSource)makeConnection(connectingSource,node.id);else alert('Primeiro clique na saída do bloco de origem.')};
    let dragging=false,dx=0,dy=0;
    el.onpointerdown=e=>{if(e.target.closest('button'))return;const rect=byId('graph-canvas').getBoundingClientRect();dragging=true;moved=false;dx=e.clientX-rect.left-node.x;dy=e.clientY-rect.top-node.y;el.setPointerCapture(e.pointerId)};
    el.onpointermove=e=>{if(!dragging)return;moved=true;const rect=byId('graph-canvas').getBoundingClientRect(),pos=clampPosition(e.clientX-rect.left-dx,e.clientY-rect.top-dy);node.x=pos.x;node.y=pos.y;el.style.left=`${node.x}px`;el.style.top=`${node.y}px`;renderEdges()};
    el.onpointerup=()=>{if(dragging){dragging=false;persistDraft()}};
    el.onpointercancel=()=>{dragging=false};
    host.append(el);
  });renderEdges();
}
function renderEdges(){
  const svg=byId('graph-edges');svg.innerHTML='';
  edges.forEach(edge=>{const a=nodes.find(n=>n.id===edge.source),b=nodes.find(n=>n.id===edge.target);if(!a||!b)return;const x1=a.x+NODE_WIDTH,y1=a.y+NODE_HEIGHT/2,x2=b.x,y2=b.y+NODE_HEIGHT/2;const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d',`M ${x1} ${y1} C ${x1+70} ${y1}, ${x2-70} ${y2}, ${x2} ${y2}`);path.setAttribute('class','graph-edge');svg.append(path)})
}
function renderCatalog(){const laneFor=category=>category==='Entrada'||category==='Observabilidade'?'Entradas':category==='Saída'?'Saídas':'Processamento',lanes=['Entradas','Processamento','Saídas'];byId('connector-catalog').innerHTML=lanes.map(lane=>`<section class="connector-lane"><header><b>${lane==='Entradas'?'1':lane==='Processamento'?'2':'3'}</b><span><strong>${lane}</strong><small>${lane==='Entradas'?'Onde os dados começam':lane==='Processamento'?'Como a SOFIA analisa':'O que será entregue'}</small></span></header><div>${catalog.filter(item=>laneFor(item.category)===lane).map(item=>`<button class="connector-card ${item.status}" data-type="${item.type}"><span>${escapeHtml(item.label)}</span><small>${escapeHtml(item.category)} · ${item.status==='active'?'pronto':'requer configuração'}</small><em>${escapeHtml(item.description||'')}</em></button>`).join('')}</div></section>`).join('');document.querySelectorAll('.connector-card').forEach(button=>{
  button.draggable=false;
  button.onclick=()=>{if(Date.now()-lastCatalogDragAt<800)return;pendingPlacement=button.dataset.type;document.querySelectorAll('.connector-card').forEach(x=>x.classList.toggle('placement-selected',x===button));const empty=byId('canvas-empty');empty.hidden=false;empty.textContent='Clique aqui para posicionar '+button.querySelector('span').textContent;byId('graph-canvas').classList.add('placement-active')};
  button.ondragstart=event=>{event.dataTransfer.setData('text/plain',button.dataset.type);event.dataTransfer.effectAllowed='copy';button.classList.add('dragging')};
  button.ondragend=()=>button.classList.remove('dragging');
  button.onpointerdown=start=>{
    if(start.button!==0)return;
    const origin={x:start.clientX,y:start.clientY};let active=false,ghost=null,draggedNode=null;
    const move=event=>{
      if(event.pointerId!==start.pointerId)return;
      if(Math.hypot(event.clientX-origin.x,event.clientY-origin.y)<6&&!active)return;
      if(!active){active=true;lastCatalogDragAt=Date.now();button.classList.add('dragging');ghost=button.cloneNode(true);ghost.className='connector-drag-ghost';document.body.append(ghost)}
      event.preventDefault();ghost.style.left=event.clientX+'px';ghost.style.top=event.clientY+'px';
      const canvas=byId('graph-canvas'),rect=canvas.getBoundingClientRect(),inside=event.clientX>=rect.left&&event.clientX<=rect.right&&event.clientY>=rect.top&&event.clientY<=rect.bottom;canvas.classList.toggle('drop-active',inside);
      if(inside&&!draggedNode)draggedNode=addNode(connector(button.dataset.type),{x:event.clientX-rect.left-NODE_WIDTH/2,y:event.clientY-rect.top-NODE_HEIGHT/2});
      else if(inside&&draggedNode){const pos=clampPosition(event.clientX-rect.left-NODE_WIDTH/2,event.clientY-rect.top-NODE_HEIGHT/2);Object.assign(draggedNode,pos);const element=document.querySelector(`.graph-node[data-id="${draggedNode.id}"]`);if(element){element.style.left=draggedNode.x+'px';element.style.top=draggedNode.y+'px';renderEdges()}}
    };
    const finish=event=>{
      if(event.pointerId!==start.pointerId)return;
      document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',finish,true);document.removeEventListener('pointercancel',finish,true);
      button.classList.remove('dragging');byId('graph-canvas').classList.remove('drop-active');ghost?.remove();
      if(active){event.preventDefault();lastCatalogDragAt=Date.now();const rect=byId('graph-canvas').getBoundingClientRect();if(!draggedNode&&event.clientX>=rect.left&&event.clientX<=rect.right&&event.clientY>=rect.top&&event.clientY<=rect.bottom)draggedNode=addNode(connector(button.dataset.type),{x:event.clientX-rect.left-NODE_WIDTH/2,y:event.clientY-rect.top-NODE_HEIGHT/2});if(draggedNode)persistDraft()}
    };
    document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',finish,true);document.addEventListener('pointercancel',finish,true);
  };
})}
async function loadGraphs(){const data=await sofia.api('/workflows/automation/graphs');const select=byId('saved-graphs');select.innerHTML='<option value="">Fluxos salvos</option>'+data.graphs.map(g=>`<option value="${g.id}">${escapeHtml(g.name)}</option>`).join('');select.onchange=()=>{const graph=data.graphs.find(g=>g.id===select.value);if(!graph)return;graphId=graph.id;nodes=graph.nodes||[];edges=graph.edges||[];byId('graph-name').value=graph.name;byId('graph-description').value=graph.description;renderGraph();showSuggestions(nodes.at(-1))}}
async function saveGraph(){const payload={id:graphId,name:byId('graph-name').value,description:byId('graph-description').value,nodes:nodes.map(({runtime,...node})=>node),edges};const result=await sofia.api('/workflows/automation/graphs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});graphId=result.id;await loadGraphs();return result}
function renderTimeline(result){byId('simulation').innerHTML=`<p class="run-status ${result.status}">${result.status==='ready'||result.status==='completed'?'Fluxo pronto':result.status==='partial'?'Fluxo executado parcialmente':'Configuração necessária'}</p>`+result.timeline.map((x,i)=>`<article class="timeline-item"><b>${i+1}</b><span><strong>${escapeHtml(x.label)}</strong><small>${escapeHtml(x.connector)} · ${escapeHtml(x.status)}</small></span></article>`).join('')}
async function simulate(){if(!nodes.length)return alert('Adicione blocos ao fluxo.');await saveGraph();const result=await sofia.api(`/workflows/automation/graphs/${graphId}/simulate`,{method:'POST'});renderTimeline(result)}
async function executeGraph(){
  if(!nodes.length)return alert('Adicione blocos ao fluxo.');
  const input=byId('execution-input').value.trim();if(!input)return alert('Informe a pergunta ou evento que inicia o fluxo.');
  const button=byId('execute-graph');button.disabled=true;button.textContent='Executando…';byId('execution-result').innerHTML='<p>Consultando os módulos do fluxo…</p>';
  let visualIndex=0;nodes.forEach((node,index)=>node.runtime=index===0?'running':'queued');renderGraph();const visualTimer=setInterval(()=>{if(visualIndex<nodes.length-1){nodes[visualIndex].runtime='completed';visualIndex+=1;nodes[visualIndex].runtime='running';renderGraph()}},650);
  try{
    await saveGraph();
    const result=await sofia.api(`/workflows/automation/graphs/${graphId}/execute`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({input})});
    nodes.forEach((node,index)=>node.runtime=result.timeline?.[index]?.status==='failed'?'failed':'completed');renderGraph();
    renderTimeline(result);
    const zabbix=(result.outputs||[]).find(item=>item.connector==='zabbix');
    const analysis=renderOperationalAnalysis(zabbix?.data||{});
    const details=(result.outputs||[]).map(item=>`<details class="execution-step"><summary><strong>${escapeHtml(item.label)}</strong><span class="step-status ${escapeHtml(item.status)}">${escapeHtml(item.status)}</span></summary><pre>${escapeHtml(item.summary)}</pre></details>`).join('');
    byId('execution-result').innerHTML=`${analysis}<article class="final-report"><small>Relatório final</small><pre>${escapeHtml(result.report||'Fluxo concluído sem relatório textual.')}</pre></article>${details}`;
  }catch(error){nodes.forEach((node,index)=>node.runtime=index===visualIndex?'failed':node.runtime);renderGraph();byId('execution-result').innerHTML=`<p class="error">${escapeHtml(error.message)}</p>`}
  finally{clearInterval(visualTimer);button.disabled=false;button.textContent='Executar fluxo'}
}
function formatDuration(seconds){if(seconds==null)return 'horário indisponível';const days=Math.floor(seconds/86400),hours=Math.floor(seconds%86400/3600),minutes=Math.floor(seconds%3600/60);return [days&&days+'d',hours&&hours+'h',minutes+'min'].filter(Boolean).join(' ')}
function renderBars(items,empty='Sem dados para este recorte.'){
  if(!items?.length)return `<p class="analysis-empty">${escapeHtml(empty)}</p>`;
  const max=Math.max(...items.map(item=>Number(item.value)||0),1);
  return `<div class="chart-bars">${items.map(item=>`<div class="chart-row"><span title="${escapeHtml(item.label)}">${escapeHtml(item.label)}</span><i><b style="width:${Math.max(4,(Number(item.value)||0)/max*100)}%"></b></i><strong>${Number(item.value)||0}</strong></div>`).join('')}</div>`;
}
function renderOperationalAnalysis(data){
  if(!data.event_timeline&&!data.behavior)return '';
  const historical=data.query_scope==='historical_triggers';
  const severity=data.severity_distribution||[],total=severity.reduce((sum,item)=>sum+(Number(item.value)||0),0)||1;
  let cursor=0;const colors=['#2de2b7','#59a8ff','#f7b267','#ff6b7c','#9b8cff','#91a4bd'];
  const stops=severity.map((item,index)=>{const start=cursor;cursor+=Number(item.value)/total*100;return `${colors[index%colors.length]} ${start}% ${cursor}%`}).join(',');
  const donut=severity.length?`<div class="donut" style="background:conic-gradient(${stops})"><span>${total}<small>${historical?'triggers':'alertas'}</small></span></div>`:'<p class="analysis-empty">Sem eventos.</p>';
  const distribution=data.host_distribution?.length?data.host_distribution:data.group_distribution;
  const distributionTitle=data.host_distribution?.length?'Ocorrências por host':'Grupos afetados';
  const timeline=(data.event_timeline||[]).map(event=>{const occurred=event.status==='occurred';return `<li><time>${event.started_at?new Date(event.started_at).toLocaleString('pt-BR'):'Sem horário'}</time><span><strong>${escapeHtml((event.hosts||[]).join(', ')||'Host não identificado')}</strong><small>${escapeHtml(event.name)}${occurred?'':' · ativo há '+escapeHtml(formatDuration(event.age_seconds))}</small></span><b>${occurred?'OCORRÊNCIA':'ATIVO'}</b></li>`}).join('')||'<p class="analysis-empty">Sem eventos no recorte.</p>';
  const behavior=data.behavior||{},series=(behavior.problem_series||[]).slice(-12);
  return `<section class="operational-analysis"><header><span><small>ANÁLISE OPERACIONAL</small><h3>${historical?'Histórico do período':'Antes, agora e comportamento'}</h3></span><span class="analysis-badge">${historical?data.days+' dias':behavior.status==='baseline_ready'?'Baseline disponível':'Coletando baseline'}</span></header><div class="analysis-grid"><article><h4>Severidade</h4>${donut}<div class="chart-legend">${severity.map((item,index)=>`<span><i style="background:${colors[index%colors.length]}"></i>${escapeHtml(item.label)}: ${item.value}</span>`).join('')}</div></article><article><h4>${distributionTitle}</h4>${renderBars(distribution)}</article><article class="history-chart"><h4>Volume observado</h4>${renderBars(series.map((item,index)=>({label:index===series.length-1?'Agora':new Date(item.generated_at).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}),value:item.problems})),'A coleta ainda não possui amostras.')}</article></div><article class="behavior-card"><strong>Aprendizado comportamental</strong><p>${behavior.snapshot_count||0} snapshots e ${behavior.insight_count||0} padrões persistidos. Coleta a cada ${behavior.interval_seconds||0}s. Método atual: ${escapeHtml(behavior.method||'não informado')}.</p><small>Isso aprende recorrências e tendências; não altera pesos de um modelo neural automaticamente.</small></article><ol class="event-timeline">${timeline}</ol></section>`;
}
function loadSqlTemplate(){
  buildTemplate('sql');
}
async function loadAdmin(){if(!byId('tools'))return;const [m,r,u]=await Promise.all([sofia.api('/mcp/tools'),sofia.api('/auth/admin/access-requests'),sofia.api('/auth/admin/users')]);byId('tools').innerHTML=Object.entries(m.capabilities||{}).map(([k,v])=>`<li><strong>${escapeHtml(k)}</strong><span>${escapeHtml(v.join(', '))}</span></li>`).join('');byId('requests').innerHTML=(r.requests||[]).filter(x=>x.status==='pending').map(x=>`<article class="row"><span><strong>${escapeHtml(x.display_name)}</strong><small>${escapeHtml(x.username)} · ${escapeHtml(x.email)}</small></span><button onclick="approve(${x.id})">Aprovar</button></article>`).join('')||'<p>Sem solicitações pendentes.</p>';byId('users').innerHTML=(u.users||[]).map(x=>`<article class="row"><span><strong>${escapeHtml(x.display_name)}</strong><small>${escapeHtml(x.username)} · ${escapeHtml(x.role)} · ${escapeHtml(x.status)}</small></span><button class="ghost" onclick="revoke(${x.id})">Revogar sessões</button></article>`).join('')}
async function approve(id){const result=await sofia.api(`/auth/admin/access-requests/${id}/approve`,{method:'POST'});prompt('Acesso aprovado. Copie e entregue este token uma única vez ao usuário:',result.setup_token);location.reload()}async function revoke(id){await sofia.api(`/auth/admin/users/${id}/revoke-sessions`,{method:'POST'});alert('Sessões revogadas')}
(async()=>{await sofia.initAuth();catalog=(await sofia.api('/workflows/automation/connectors')).connectors;renderCatalog();restoreDraft();showSuggestions(nodes.at(-1));await Promise.all([loadGraphs(),loadAdmin()]);const canvas=byId('graph-canvas');canvas.onclick=event=>{if(!pendingPlacement||event.target.closest('.graph-node'))return;const rect=canvas.getBoundingClientRect();addNode(connector(pendingPlacement),{x:event.clientX-rect.left-NODE_WIDTH/2,y:event.clientY-rect.top-NODE_HEIGHT/2});pendingPlacement=null;canvas.classList.remove('placement-active');document.querySelectorAll('.connector-card').forEach(x=>x.classList.remove('placement-selected'))};canvas.ondragover=event=>{event.preventDefault();event.dataTransfer.dropEffect='copy';canvas.classList.add('drop-active')};canvas.ondragleave=()=>canvas.classList.remove('drop-active');canvas.ondrop=event=>{event.preventDefault();canvas.classList.remove('drop-active');const type=event.dataTransfer.getData('application/x-sofia-connector')||event.dataTransfer.getData('text/plain');if(!type||!catalog.some(x=>x.type===type))return;const rect=canvas.getBoundingClientRect();addNode(connector(type),{x:event.clientX-rect.left-NODE_WIDTH/2,y:event.clientY-rect.top-NODE_HEIGHT/2})};byId('sql-template').onclick=loadSqlTemplate;byId('connect-selected').onclick=connectSelected;byId('clear-graph').onclick=()=>{nodes=[];edges=[];selected=[];graphId=null;localStorage.removeItem('sofia-automation-draft');renderGraph();showSuggestions()};byId('save-graph').onclick=async()=>{await saveGraph();alert('Fluxo salvo.')};byId('simulate-graph').onclick=simulate;byId('execute-graph').onclick=executeGraph;window.addEventListener('resize',renderGraph);renderGraph()})().catch(e=>alert(e.message));
