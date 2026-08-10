(async()=>{
  await sofia.initAuth();
  const list=document.querySelector('#messages');
  const form=document.querySelector('#chat-form');
  const input=document.querySelector('#question');
  const button=form.querySelector('button');
  const params=new URLSearchParams(location.search),suggested=params.get('q'),autoRun=params.get('auto')==='1';
  if(suggested)input.value=suggested;
  const cEsc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

  function humanSource(value){return ({'semantic-zabbix':'Zabbix','claude-learning-pipeline':'SOFIA + IA','domain-policy':'Política de domínio'})[value]||'SOFIA'}
  function investigationEvidence(result){
    const entries=result.context?.tools?.['zabbix.investigate']?.evidence||[];
    return entries.slice(0,8).map(entry=>{const host=(entry.hosts||[]).join(', ')||'Equipamento não identificado',component=entry.entity?` · ${entry.entity}`:'',items=(entry.items||[]).slice(0,4).map(item=>`${item.name||item.key}: ${item.interpreted_value||item.current_value||'sem valor'}${item.units?` ${item.units}`:''}`).join(' · ');return `${host}${component} — ${entry.problem||'problema'}${items?` — ${items}`:''}`});
  }
  function formatAnswer(text){
    const lines=String(text||'').split(/\r?\n/),html=[];let list=null;
    const close=()=>{if(list){html.push(`</${list}>`);list=null}};
    lines.forEach(raw=>{const line=raw.trim();if(!line){close();return}const heading=line.replace(/^#{1,4}\s*/, '').replace(/\*\*/g,'');if(/^#{1,4}\s/.test(line)||/^(Conclusão|Evidências|Tendência|Impacto|Próxima ação|Limites|Como tratar|Diagnóstico|Resumo)(:|$)/i.test(heading)){close();html.push(`<h3>${cEsc(heading.replace(/:$/,''))}</h3>`);return}const match=line.match(/^[-•]\s+(.+)/)||line.match(/^\d+[.)]\s+(.+)/);if(match){const wanted=/^\d/.test(line)?'ol':'ul';if(list!==wanted){close();list=wanted;html.push(`<${list}>`)}html.push(`<li>${cEsc(match[1]).replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</li>`);return}close();html.push(`<p>${cEsc(line).replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</p>`)});close();return html.join('');
  }
  function renderEvidence(result){
    const context=result.context||{},items=[];
    if(context.related_problem_count!=null)items.push(`${context.related_problem_count} ocorrência(s) relacionada(s)`);
    if(context.unique_host_count!=null)items.push(`${context.unique_host_count} host(s) único(s)`);
    if(context.group)items.push(`Grupo: ${context.group}`);
    if(context.days)items.push(`Período: ${context.days} dia(s)`);
    const tools=(result.plan?.tools||[]).map(tool=>String(tool).split('.').at(-1)),live=investigationEvidence(result);
    const sources=(result.sources_used||[humanSource(result.source)]).map(cEsc);
    const mode=result.degraded?'Modo local/degradado':'Resposta completa';
    const operational=live.length||context.related_problem_count!=null,analysisId=`analysis-${Date.now()}`;if(operational)sessionStorage.setItem('sofia-current-analysis',JSON.stringify({id:analysisId,question:result.question||'',context,entries:result.context?.tools?.['zabbix.investigate']?.evidence||[],saved_at:new Date().toISOString()}));
    return `<footer class="answer-meta"><span>${sources.join(' + ')}</span><span>${live.length||items.length||tools.length} evidência(s)</span><span>${Math.round((Number(result.confidence)||0)*100)}% confiança</span><span>${cEsc(mode)}</span></footer>
      <div class="answer-actions">${operational?`<a href="/ui/analytics.html?analysis=current">Mostrar gráficos desta análise</a>`:''}<details><summary>Ver evidências (${live.length||items.length})</summary><ul>${live.map(item=>`<li>${cEsc(item)}</li>`).join('')||items.map(item=>`<li>${cEsc(item)}</li>`).join('')||'<li>Esta resposta não utilizou telemetria operacional.</li>'}${tools.length?`<li>Fontes consultadas: ${tools.map(cEsc).join(', ')}</li>`:''}</ul></details>${operational&&!result.deep_analysis?'<button type="button" data-deepen>Correlacionar histórico</button>':''}</div>`;
  }

  async function sendQuestion(question=null,deep=false){
    const q=(question??input.value).trim();
    if(!q||button.disabled)return;
    const userNode=document.createElement('div');
    userNode.className='msg user';
    userNode.textContent=q;
    list.append(userNode);
    input.value='';
    button.disabled=true;
    button.textContent='Enviando…';
    const progress=document.querySelector('#answer-progress'),steps=[...progress.querySelectorAll('li')];let active=0;progress.hidden=false;steps.forEach(item=>item.className='');steps[0].className='active';const progressTimer=setInterval(()=>{if(active<steps.length-1){steps[active].className='done';active+=1;steps[active].className='active'}},900);
    try{
      const r=await sofia.api('/ai/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});r.question=q;r.deep_analysis=deep;
      const node=document.createElement('article');
      node.className='msg assistant answer-card';
      const answer=document.createElement('div');answer.className='answer-text';answer.innerHTML=formatAnswer(r.answer);
      const meta=document.createElement('div');meta.innerHTML=renderEvidence(r);node.append(answer,meta);
      list.append(node);steps.forEach(item=>item.className='done');
      const deepen=node.querySelector('[data-deepen]');if(deepen)deepen.onclick=()=>sendQuestion(`Correlacione histórico e recorrência somente para este mesmo escopo e período. Responda de forma curta com conclusão, mudança observada, evidências, tendência e próxima ação: ${q}`,true);
    }catch(err){
      const node=document.createElement('div');
      node.className='msg error';
      node.textContent=err.message;
      list.append(node);
    }finally{
      clearInterval(progressTimer);setTimeout(()=>{progress.hidden=true},700);button.disabled=false;
      button.textContent='Enviar';
      input.focus();
      list.scrollTop=list.scrollHeight;
    }
  }

  form.onsubmit=async event=>{event.preventDefault();await sendQuestion()};
  input.addEventListener('keydown',event=>{
    if(event.key==='Enter'&&!event.shiftKey){
      event.preventDefault();
      form.requestSubmit();
    }
  });
  if(suggested&&autoRun){history.replaceState({},'',location.pathname);await sendQuestion(suggested)}
})().catch(console.error);
