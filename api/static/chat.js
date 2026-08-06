(async()=>{
  await sofia.initAuth();
  const list=document.querySelector('#messages');
  const form=document.querySelector('#chat-form');
  const input=document.querySelector('#question');
  const button=form.querySelector('button');
  const suggested=new URLSearchParams(location.search).get('q');
  if(suggested)input.value=suggested;

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
    try{
      const r=await sofia.api('/ai/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
      const node=document.createElement('div');
      node.className='msg assistant';
      node.textContent=r.answer;
      list.append(node);
    }catch(err){
      const node=document.createElement('div');
      node.className='msg error';
      node.textContent=err.message;
      list.append(node);
    }finally{
      button.disabled=false;
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
