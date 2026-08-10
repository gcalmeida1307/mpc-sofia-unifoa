(async()=>{
  await sofia.initAuth();
  const list=document.querySelector('#messages');
  const form=document.querySelector('#chat-form');
  const input=document.querySelector('#question');
  const button=form.querySelector('button');
  const suggested=new URLSearchParams(location.search).get('q');
  if(suggested)input.value=suggested;
  const cEsc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

  function humanSource(value){return ({'semantic-zabbix':'Zabbix','claude-learning-pipeline':'SOFIA + IA','domain-policy':'Política de domínio'})[value]||'SOFIA'}
  function renderEvidence(result){
    const context=result.context||{},items=[];
    if(context.related_problem_count!=null)items.push(`${context.related_problem_count} ocorrência(s) relacionada(s)`);
    if(context.unique_host_count!=null)items.push(`${context.unique_host_count} host(s) único(s)`);
    if(context.group)items.push(`Grupo: ${context.group}`);
    if(context.days)items.push(`Período: ${context.days} dia(s)`);
    const tools=(result.plan?.tools||[]).map(tool=>String(tool).split('.').at(-1));
    const sources=(result.sources_used||[humanSource(result.source)]).map(cEsc);
    const mode=result.degraded?'Modo local/degradado':'Resposta completa';
    return `<footer class="answer-meta"><span>${sources.join(' + ')}</span><span>${items.length||tools.length} evidência(s)</span><span>${Math.round((Number(result.confidence)||0)*100)}% confiança</span><span>${cEsc(mode)}</span></footer>
      <div class="answer-actions"><a href="/ui/analytics.html">Mostrar gráficos</a><details><summary>Ver evidências</summary><ul>${items.map(item=>`<li>${cEsc(item)}</li>`).join('')||'<li>Resposta conceitual, sem telemetria operacional.</li>'}${tools.length?`<li>Consultas: ${tools.map(cEsc).join(', ')}</li>`:''}</ul></details><button type="button" data-deepen>Executar análise detalhada</button></div>`;
  }

  async function sendQuestion(){
    const q=input.value.trim();
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
      const r=await sofia.api('/ai/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
      const node=document.createElement('article');
      node.className='msg assistant answer-card';
      const answer=document.createElement('div');answer.className='answer-text';answer.textContent=r.answer;
      const meta=document.createElement('div');meta.innerHTML=renderEvidence(r);node.append(answer,meta);
      list.append(node);steps.forEach(item=>item.className='done');
      node.querySelector('[data-deepen]').onclick=()=>{input.value=`Aprofunde esta análise com evidências, histórico, recorrência e próximos passos seguros: ${q}`;input.focus()};
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
})().catch(console.error);
