let graphId=null;
let nodes=[];
let edges=[];
let selected=[];
let catalog=[];

const byId=id=>document.getElementById(id);
const escapeHtml=value=>String(value||'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

function connector(type){return catalog.find(item=>item.type===type)||{label:type,status:'unknown',category:'Outro'}}
function addNode(item){
  const count=nodes.length;
  nodes.push({id:crypto.randomUUID(),type:item.type,label:item.label,x:40+(count%3)*210,y:45+Math.floor(count/3)*125});
  renderGraph();
}
function toggleNode(id){selected=selected.includes(id)?selected.filter(x=>x!==id):[...selected,id].slice(-2);renderGraph()}
function removeNode(id){nodes=nodes.filter(n=>n.id!==id);edges=edges.filter(e=>e.source!==id&&e.target!==id);selected=selected.filter(x=>x!==id);renderGraph()}
function connectSelected(){if(selected.length!==2)return alert('Selecione dois blocos na ordem origem → destino.');const [source,target]=selected;if(!edges.some(e=>e.source===source&&e.target===target))edges.push({id:crypto.randomUUID(),source,target});selected=[];renderGraph()}

function renderGraph(){
  const host=byId('graph-nodes');host.innerHTML='';
  nodes.forEach(node=>{
    const meta=connector(node.type);const el=document.createElement('article');
    el.className=`graph-node ${selected.includes(node.id)?'selected':''}`;el.dataset.id=node.id;el.style.left=`${node.x}px`;el.style.top=`${node.y}px`;
    el.innerHTML=`<button class="node-remove" title="Remover">×</button><small>${escapeHtml(meta.category)}</small><strong>${escapeHtml(node.label||meta.label)}</strong><span class="connector-status ${meta.status}">${meta.status==='active'?'pronto':'configurar'}</span>`;
    el.onclick=e=>{if(!e.target.classList.contains('node-remove'))toggleNode(node.id)};
    el.querySelector('.node-remove').onclick=e=>{e.stopPropagation();removeNode(node.id)};
    let dragging=false,dx=0,dy=0;
    el.onpointerdown=e=>{if(e.target.tagName==='BUTTON')return;dragging=true;dx=e.clientX-node.x;dy=e.clientY-node.y;el.setPointerCapture(e.pointerId)};
    el.onpointermove=e=>{if(!dragging)return;const canvas=byId('graph-canvas').getBoundingClientRect();node.x=Math.max(0,Math.min(canvas.width-185,e.clientX-dx));node.y=Math.max(0,Math.min(canvas.height-90,e.clientY-dy));el.style.left=`${node.x}px`;el.style.top=`${node.y}px`;renderEdges()};
    el.onpointerup=()=>dragging=false;host.append(el);
  });renderEdges();
}
function renderEdges(){
  const svg=byId('graph-edges');svg.innerHTML='';
  edges.forEach(edge=>{const a=nodes.find(n=>n.id===edge.source),b=nodes.find(n=>n.id===edge.target);if(!a||!b)return;const x1=a.x+175,y1=a.y+42,x2=b.x,y2=b.y+42;const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d',`M ${x1} ${y1} C ${x1+70} ${y1}, ${x2-70} ${y2}, ${x2} ${y2}`);path.setAttribute('class','graph-edge');svg.append(path)})
}
function renderCatalog(){byId('connector-catalog').innerHTML=catalog.map(item=>`<button class="connector-card ${item.status}" data-type="${item.type}"><span>${escapeHtml(item.label)}</span><small>${escapeHtml(item.category)} · ${item.status==='active'?'pronto':'requer configuração'}</small></button>`).join('');document.querySelectorAll('.connector-card').forEach(button=>button.onclick=()=>addNode(connector(button.dataset.type)))}
async function loadGraphs(){const data=await sofia.api('/workflows/automation/graphs');const select=byId('saved-graphs');select.innerHTML='<option value="">Fluxos salvos</option>'+data.graphs.map(g=>`<option value="${g.id}">${escapeHtml(g.name)}</option>`).join('');select.onchange=()=>{const graph=data.graphs.find(g=>g.id===select.value);if(!graph)return;graphId=graph.id;nodes=graph.nodes||[];edges=graph.edges||[];byId('graph-name').value=graph.name;byId('graph-description').value=graph.description;renderGraph()}}
async function saveGraph(){const payload={id:graphId,name:byId('graph-name').value,description:byId('graph-description').value,nodes,edges};const result=await sofia.api('/workflows/automation/graphs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});graphId=result.id;await loadGraphs();return result}
async function simulate(){if(!nodes.length)return alert('Adicione blocos ao fluxo.');await saveGraph();const result=await sofia.api(`/workflows/automation/graphs/${graphId}/simulate`,{method:'POST'});byId('simulation').innerHTML=`<p class="run-status ${result.status}">${result.status==='ready'?'Fluxo pronto':'Configuração necessária'}</p>`+result.timeline.map((x,i)=>`<article class="timeline-item"><b>${i+1}</b><span><strong>${escapeHtml(x.label)}</strong><small>${escapeHtml(x.connector)} · ${escapeHtml(x.status)}</small></span></article>`).join('')}
async function loadAdmin(){const [m,r,u]=await Promise.all([sofia.api('/mcp/tools'),sofia.api('/auth/admin/access-requests'),sofia.api('/auth/admin/users')]);byId('tools').innerHTML=Object.entries(m.capabilities||{}).map(([k,v])=>`<li><strong>${escapeHtml(k)}</strong><span>${escapeHtml(v.join(', '))}</span></li>`).join('');byId('requests').innerHTML=(r.requests||[]).filter(x=>x.status==='pending').map(x=>`<article class="row"><span><strong>${escapeHtml(x.display_name)}</strong><small>${escapeHtml(x.username)} · ${escapeHtml(x.email)}</small></span><button onclick="approve(${x.id})">Aprovar</button></article>`).join('')||'<p>Sem solicitações pendentes.</p>';byId('users').innerHTML=(u.users||[]).map(x=>`<article class="row"><span><strong>${escapeHtml(x.display_name)}</strong><small>${escapeHtml(x.username)} · ${escapeHtml(x.role)} · ${escapeHtml(x.status)}</small></span><button class="ghost" onclick="revoke(${x.id})">Revogar sessões</button></article>`).join('')}
async function approve(id){const result=await sofia.api(`/auth/admin/access-requests/${id}/approve`,{method:'POST'});prompt('Acesso aprovado. Copie e entregue este token uma única vez ao usuário:',result.setup_token);location.reload()}async function revoke(id){await sofia.api(`/auth/admin/users/${id}/revoke-sessions`,{method:'POST'});alert('Sessões revogadas')}
(async()=>{await sofia.initAuth();catalog=(await sofia.api('/workflows/automation/connectors')).connectors;renderCatalog();await Promise.all([loadGraphs(),loadAdmin()]);byId('connect-selected').onclick=connectSelected;byId('clear-graph').onclick=()=>{nodes=[];edges=[];selected=[];graphId=null;renderGraph()};byId('save-graph').onclick=async()=>{await saveGraph();alert('Fluxo salvo.')};byId('simulate-graph').onclick=simulate;renderGraph()})().catch(e=>alert(e.message));
