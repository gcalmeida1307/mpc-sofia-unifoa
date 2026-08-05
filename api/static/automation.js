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
    el.className=`graph-node ${selected.includes(node.id)?'selected':''} ${connectingSource===node.id?'connecting':''}`;el.dataset.id=node.id;el.style.left=`${node.x}px`;el.style.top=`${node.y}px`;
    el.innerHTML=`<button class="node-port node-input" title="Entrada" aria-label="Conectar na entrada"></button><button class="node-remove" title="Remover">×</button><small>${escapeHtml(meta.category)}</small><strong>${escapeHtml(node.label||meta.label)}</strong><span class="connector-status ${meta.status}">${meta.status==='active'?'pronto':'configurar'}</span><button class="node-port node-output" title="Saída" aria-label="Iniciar conexão pela saída"></button>`;
    let moved=false;
    el.onclick=e=>{if(!moved&&!e.target.closest('button')){toggleNode(node.id);showSuggestions(node)}};
    el.querySelector('.node-remove').onclick=e=>{e.stopPropagation();removeNode(node.id)};
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
function renderCatalog(){byId('connector-catalog').innerHTML=catalog.map(item=>`<button class="connector-card ${item.status}" data-type="${item.type}"><span>${escapeHtml(item.label)}</span><small>${escapeHtml(item.category)} · ${item.status==='active'?'pronto':'requer configuração'}</small><em>${escapeHtml(item.description||'')}</em></button>`).join('');document.querySelectorAll('.connector-card').forEach(button=>{
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
async function saveGraph(){const payload={id:graphId,name:byId('graph-name').value,description:byId('graph-description').value,nodes,edges};const result=await sofia.api('/workflows/automation/graphs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});graphId=result.id;await loadGraphs();return result}
async function simulate(){if(!nodes.length)return alert('Adicione blocos ao fluxo.');await saveGraph();const result=await sofia.api(`/workflows/automation/graphs/${graphId}/simulate`,{method:'POST'});byId('simulation').innerHTML=`<p class="run-status ${result.status}">${result.status==='ready'?'Fluxo pronto':'Configuração necessária'}</p>`+result.timeline.map((x,i)=>`<article class="timeline-item"><b>${i+1}</b><span><strong>${escapeHtml(x.label)}</strong><small>${escapeHtml(x.connector)} · ${escapeHtml(x.status)}</small></span></article>`).join('')}
function loadSqlTemplate(){
  const sequence=['trigger','grafana','prometheus','loki','postgres','correlate','report'];
  const labels=['Pergunta: por que o SQL ficou lento?','Grafana: contexto','CPU / memória / disco','Logs e backup','Queries pesadas','Correlacionar horários','Resposta e relatório'];
  nodes=sequence.map((type,index)=>({id:createNodeId(),type,label:labels[index],x:45+(index%3)*220,y:45+Math.floor(index/3)*130}));
  edges=nodes.slice(0,-1).map((node,index)=>({id:createNodeId(),source:node.id,target:nodes[index+1].id}));
  graphId=null;persistDraft();byId('graph-name').value='Investigar lentidão SQL';byId('graph-description').value='Correlaciona métricas, logs, banco e eventos para explicar degradação SQL.';renderGraph();
}
async function loadAdmin(){const [m,r,u]=await Promise.all([sofia.api('/mcp/tools'),sofia.api('/auth/admin/access-requests'),sofia.api('/auth/admin/users')]);byId('tools').innerHTML=Object.entries(m.capabilities||{}).map(([k,v])=>`<li><strong>${escapeHtml(k)}</strong><span>${escapeHtml(v.join(', '))}</span></li>`).join('');byId('requests').innerHTML=(r.requests||[]).filter(x=>x.status==='pending').map(x=>`<article class="row"><span><strong>${escapeHtml(x.display_name)}</strong><small>${escapeHtml(x.username)} · ${escapeHtml(x.email)}</small></span><button onclick="approve(${x.id})">Aprovar</button></article>`).join('')||'<p>Sem solicitações pendentes.</p>';byId('users').innerHTML=(u.users||[]).map(x=>`<article class="row"><span><strong>${escapeHtml(x.display_name)}</strong><small>${escapeHtml(x.username)} · ${escapeHtml(x.role)} · ${escapeHtml(x.status)}</small></span><button class="ghost" onclick="revoke(${x.id})">Revogar sessões</button></article>`).join('')}
async function approve(id){const result=await sofia.api(`/auth/admin/access-requests/${id}/approve`,{method:'POST'});prompt('Acesso aprovado. Copie e entregue este token uma única vez ao usuário:',result.setup_token);location.reload()}async function revoke(id){await sofia.api(`/auth/admin/users/${id}/revoke-sessions`,{method:'POST'});alert('Sessões revogadas')}
(async()=>{await sofia.initAuth();catalog=(await sofia.api('/workflows/automation/connectors')).connectors;renderCatalog();restoreDraft();showSuggestions(nodes.at(-1));await Promise.all([loadGraphs(),loadAdmin()]);const canvas=byId('graph-canvas');canvas.onclick=event=>{if(!pendingPlacement||event.target.closest('.graph-node'))return;const rect=canvas.getBoundingClientRect();addNode(connector(pendingPlacement),{x:event.clientX-rect.left-NODE_WIDTH/2,y:event.clientY-rect.top-NODE_HEIGHT/2});pendingPlacement=null;canvas.classList.remove('placement-active');document.querySelectorAll('.connector-card').forEach(x=>x.classList.remove('placement-selected'))};canvas.ondragover=event=>{event.preventDefault();event.dataTransfer.dropEffect='copy';canvas.classList.add('drop-active')};canvas.ondragleave=()=>canvas.classList.remove('drop-active');canvas.ondrop=event=>{event.preventDefault();canvas.classList.remove('drop-active');const type=event.dataTransfer.getData('application/x-sofia-connector')||event.dataTransfer.getData('text/plain');if(!type||!catalog.some(x=>x.type===type))return;const rect=canvas.getBoundingClientRect();addNode(connector(type),{x:event.clientX-rect.left-NODE_WIDTH/2,y:event.clientY-rect.top-NODE_HEIGHT/2})};byId('sql-template').onclick=loadSqlTemplate;byId('connect-selected').onclick=connectSelected;byId('clear-graph').onclick=()=>{nodes=[];edges=[];selected=[];graphId=null;localStorage.removeItem('sofia-automation-draft');renderGraph();showSuggestions()};byId('save-graph').onclick=async()=>{await saveGraph();alert('Fluxo salvo.')};byId('simulate-graph').onclick=simulate;window.addEventListener('resize',renderGraph);renderGraph()})().catch(e=>alert(e.message));
