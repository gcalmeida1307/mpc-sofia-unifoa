(async()=>{
  await sofia.initAuth();
  const list=document.querySelector('#messages'),form=document.querySelector('#chat-form'),input=document.querySelector('#question'),button=form.querySelector('button');
  const analysisPanel=document.querySelector('#conversation-analysis'),analysisContent=document.querySelector('#analysis-content');
  const params=new URLSearchParams(location.search),suggested=params.get('q'),autoRun=params.get('auto')==='1';
  const storageKey='sofia-chat-history';
  if(suggested)input.value=suggested;
  const cEsc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const entriesOf=result=>result.context?.tools?.['zabbix.investigate']?.evidence||result.analysis_entries||[];

  function humanSource(value){return ({'semantic-zabbix':'Zabbix','claude-learning-pipeline':'SOFIA + IA','domain-policy':'Política de domínio'})[value]||'SOFIA'}
  function formatAnswer(text){
    const lines=String(text||'').split(/\r?\n/),html=[];let listType=null;
    const close=()=>{if(listType){html.push(`</${listType}>`);listType=null}};
    lines.forEach(raw=>{const line=raw.trim();if(!line){close();return}const heading=line.replace(/^#{1,4}\s*/,'').replace(/\*\*/g,'');if(/^#{1,4}\s/.test(line)||/^(Conclusão|Evidências|Tendência|Impacto|Próxima ação|Limites|Como tratar|Diagnóstico|Resumo)(:|$)/i.test(heading)){close();html.push(`<h3>${cEsc(heading.replace(/:$/,''))}</h3>`);return}const match=line.match(/^[-•]\s+(.+)/)||line.match(/^\d+[.)]\s+(.+)/);if(match){const wanted=/^\d/.test(line)?'ol':'ul';if(listType!==wanted){close();listType=wanted;html.push(`<${listType}>`)}html.push(`<li>${cEsc(match[1]).replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</li>`);return}close();html.push(`<p>${cEsc(line).replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</p>`)});close();return html.join('');
  }
  function compactResult(result){
    const entries=entriesOf(result).slice(0,8).map(entry=>({problem:entry.problem,severity:entry.severity,started_at:entry.started_at,entity:entry.entity,hosts:(entry.hosts||[]).slice(0,4),groups:(entry.groups||[]).slice(0,4),recurrence:entry.recurrence,data_coverage:entry.data_coverage,items:(entry.items||[]).slice(0,5).map(item=>({name:item.name,key:item.key,current_value:item.current_value,interpreted_value:item.interpreted_value,units:item.units,last_collected_at:item.last_collected_at,history_summary:item.history_summary}))}));
    return {answer:result.answer,question:result.question,confidence:result.confidence,degraded:result.degraded,source:result.source,sources_used:result.sources_used,plan:{tools:result.plan?.tools||[]},context:{related_problem_count:result.context?.related_problem_count,unique_host_count:result.context?.unique_host_count,group:result.context?.group,days:result.context?.days},analysis_entries:entries};
  }
  function loadHistory(){try{return JSON.parse(sessionStorage.getItem(storageKey)||'[]')}catch{return []}}
  function persist(question,result){const turns=loadHistory();turns.push({question,result:compactResult(result)});sessionStorage.setItem(storageKey,JSON.stringify(turns.slice(-6)))}
  function renderMeta(result){
    const context=result.context||{},entries=entriesOf(result),tools=(result.plan?.tools||[]).map(tool=>String(tool).split('.').at(-1));
    const evidenceCount=entries.length||[context.related_problem_count,context.unique_host_count,context.group,context.days].filter(value=>value!=null).length;
    const sources=(result.sources_used||[humanSource(result.source)]).map(cEsc),mode=result.degraded?'Modo local/degradado':'Resposta completa';
    const operational=entries.length||context.related_problem_count!=null;
    return `<footer class="answer-meta"><span>${sources.join(' + ')}</span><span>${evidenceCount} evidência(s)</span><span>${Math.round((Number(result.confidence)||0)*100)}% confiança</span><span>${cEsc(mode)}</span></footer>${operational?'<div class="answer-actions"><button type="button" data-open-analysis>Abrir análise visual</button></div>':tools.length?`<div class="answer-actions"><span>Fontes consultadas: ${tools.map(cEsc).join(', ')}</span></div>`:''}`;
  }
  function evidenceText(entry){const host=(entry.hosts||[]).join(', ')||'Equipamento não identificado',component=entry.entity?` · componente ${entry.entity}`:'';const items=(entry.items||[]).slice(0,4).map(item=>`${item.name||item.key}: ${item.interpreted_value||item.current_value||'sem valor'}${item.units?` ${item.units}`:''}`).join(' · ');return `${host}${component} — ${entry.problem||'problema'}${items?` — ${items}`:''}`}
  async function openAnalysis(result){
    const entries=entriesOf(result),context=result.context||{},hosts=[...new Set(entries.flatMap(entry=>entry.hosts||[]))],components=[...new Set(entries.map(entry=>entry.entity).filter(Boolean))];
    const hostCounts={};entries.forEach(entry=>(entry.hosts||['Não identificado']).forEach(host=>hostCounts[host]=(hostCounts[host]||0)+1));const max=Math.max(1,...Object.values(hostCounts));
    const bars=Object.entries(hostCounts).sort((a,b)=>b[1]-a[1]).map(([host,count])=>`<div class="analysis-host-row"><span>${cEsc(host)}</span><i><b style="width:${count/max*100}%"></b></i><strong>${count}</strong></div>`).join('');
    const timeline=entries.filter(entry=>entry.started_at).sort((a,b)=>String(a.started_at).localeCompare(String(b.started_at))).map(entry=>`<li><time>${new Date(entry.started_at).toLocaleString('pt-BR')}</time><span><strong>${cEsc((entry.hosts||[]).join(', ')||'Equipamento')}</strong><small>${cEsc(entry.problem||'Ocorrência')}</small></span></li>`).join('');
    document.querySelector('#analysis-title').textContent=result.question||'Análise correlacionada';
    analysisContent.innerHTML=`<section class="analysis-summary"><article><strong>${entries.length||context.related_problem_count||0}</strong><span>Evidências</span></article><article><strong>${hosts.length||context.unique_host_count||0}</strong><span>Equipamentos</span></article><article><strong>${components.length}</strong><span>Componentes</span></article></section><section id="behavior-patterns" class="behavior-patterns"><p>Comparando com o comportamento histórico…</p></section><section class="analysis-visual"><article><h3>Ocorrências por equipamento</h3>${bars||'<p class="empty-state">A consulta retornou contadores, mas não expôs equipamentos detalhados.</p>'}</article><article><h3>Linha do tempo</h3><ol>${timeline||'<li class="empty-state">Não há horários detalhados nesta resposta.</li>'}</ol></article></section><details class="analysis-evidence" open><summary>Evidências comprovadas (${entries.length})</summary><ul>${entries.map(entry=>`<li>${cEsc(evidenceText(entry))}</li>`).join('')||'<li>Não existem itens detalhados nesta resposta. Execute uma investigação do Zabbix para coletar trigger, item e histórico.</li>'}</ul></details><button type="button" id="correlate-analysis" class="analysis-primary">Correlacionar histórico deste escopo</button>`;
    analysisPanel.hidden=false;document.querySelector('.conversation-workspace').classList.add('analysis-open');document.querySelector('#correlate-analysis').onclick=()=>{analysisPanel.hidden=true;document.querySelector('.conversation-workspace').classList.remove('analysis-open');sendQuestion(`Correlacione histórico e recorrência somente para este mesmo escopo e período. Responda com conclusão, mudança observada, evidências, tendência e próxima ação: ${result.question}`,true)};
    try{const response=await sofia.api('/infra/patterns'),patterns=(response.patterns||[]).filter(pattern=>!hosts.length||hosts.includes(pattern.host));document.querySelector('#behavior-patterns').innerHTML=patterns.length?`<header><span><p class="eyebrow">Padrões aprendidos</p><h3>Comportamento recorrente identificado</h3></span></header>${patterns.slice(0,4).map(pattern=>`<article><strong>${cEsc(pattern.classification)}</strong><p>${cEsc(pattern.summary)}</p><div><span>${Math.round(pattern.confidence*100)}% confiança</span><span>${pattern.observed_days} dias observados</span><span>${Math.round(pattern.night_down_rate*100)}% fora do expediente</span></div><small>${cEsc(pattern.recommended_action)}</small></article>`).join('')}`:'<p>Nenhum padrão recorrente comprovado para estes equipamentos. A SOFIA continuará formando o baseline.</p>'}catch{document.querySelector('#behavior-patterns').innerHTML='<p>O padrão histórico não está disponível para este perfil ou ainda está em formação.</p>'}
  }
  function appendTurn(question,result,save=true){
    const userNode=document.createElement('div');userNode.className='msg user';userNode.textContent=question;list.append(userNode);
    const node=document.createElement('article');node.className='msg assistant answer-card';node.innerHTML=`<div class="answer-text">${formatAnswer(result.answer)}</div><div>${renderMeta(result)}</div>`;list.append(node);
    const action=node.querySelector('[data-open-analysis]');if(action)action.onclick=()=>openAnalysis({...result,question});if(save)persist(question,{...result,question});
  }
  loadHistory().forEach(turn=>appendTurn(turn.question,turn.result,false));

  async function sendQuestion(question=null,deep=false){
    const q=(question??input.value).trim();if(!q||button.disabled)return;input.value='';button.disabled=true;button.textContent='Investigando…';
    const progress=document.querySelector('#answer-progress'),steps=[...progress.querySelectorAll('li')];let active=0;progress.hidden=false;steps.forEach(item=>item.className='');steps[0].className='active';const timer=setInterval(()=>{if(active<steps.length-1){steps[active].className='done';steps[++active].className='active'}},900);
    try{const result=await sofia.api('/ai/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});result.deep_analysis=deep;appendTurn(q,result);steps.forEach(item=>item.className='done')}catch(error){const node=document.createElement('div');node.className='msg error';node.textContent=error.message;list.append(node)}finally{clearInterval(timer);setTimeout(()=>progress.hidden=true,500);button.disabled=false;button.textContent='Enviar';input.focus();list.scrollTop=list.scrollHeight}
  }
  document.querySelector('#close-analysis').onclick=()=>{analysisPanel.hidden=true;document.querySelector('.conversation-workspace').classList.remove('analysis-open')};
  form.onsubmit=async event=>{event.preventDefault();await sendQuestion()};input.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();form.requestSubmit()}});
  if(suggested&&autoRun){history.replaceState({},'',location.pathname);await sendQuestion(suggested)}
})().catch(console.error);
