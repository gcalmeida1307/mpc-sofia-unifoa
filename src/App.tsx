import { useEffect, useMemo, useState, type ChangeEvent, type DragEvent } from 'react'
import { knowledgeModules } from './knowledge'

type Page = 'dashboard' | 'chat' | 'modules' | 'upload' | 'neural'
type Provider = 'gemini' | 'claude' | 'ollama'
type Module = typeof knowledgeModules[number]
type ChatItem = { role: 'user' | 'assistant'; text: string; sources?: string[] }
const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8787'
const nav = [{ id: 'dashboard' as Page, label: 'Dashboard', icon: '▦' }, { id: 'chat' as Page, label: 'Chat Sofia', icon: '▱' }, { id: 'modules' as Page, label: 'Módulos RAG', icon: '▱' }, { id: 'upload' as Page, label: 'Upload', icon: '↥' }, { id: 'neural' as Page, label: 'Rede Neural', icon: '♧' }]

function App() {
  const [items, setItems] = useState<Module[]>(knowledgeModules)
  const [moduleId, setModuleId] = useState(knowledgeModules[0]?.id ?? '')
  const [page, setPage] = useState<Page>('dashboard')
  const [dark, setDark] = useState(true)
  const [provider, setProvider] = useState<Provider>('gemini')
  const [message, setMessage] = useState('')
  const [chat, setChat] = useState<ChatItem[]>([])
  const [apiOnline, setApiOnline] = useState(false)
  const mod = useMemo(() => items.find(item => item.id === moduleId) ?? items[0], [items, moduleId])

  const refresh = () => fetch(`${API}/api/modules`).then(response => response.ok ? response.json() : Promise.reject()).then((data: Array<Record<string, string | number>>) => { setItems(data.map(item => ({ ...knowledgeModules.find(local => local.id === item.id), id: String(item.id), name: String(item.name), category: String(item.category), docs: Number(item.documents).toLocaleString('pt-BR'), queries: '-', accuracy: '-', greeting: knowledgeModules.find(local => local.id === item.id)?.greeting ?? 'Consulte os documentos deste módulo.' } as Module))); setApiOnline(true) }).catch(() => setApiOnline(false))
  useEffect(() => { refresh() }, [])
  useEffect(() => { setChat([]) }, [moduleId])
  if (!mod) return <div className="app dark"><div className="page-body"><h1>Adicione módulos em knowledge</h1></div></div>
  const selectModule = (id: string) => { setModuleId(id); setPage('dashboard') }
  const send = async () => { const text = message.trim(); if (!text) return; setMessage(''); setChat(prev => [...prev, { role: 'user', text }]); try { const response = await fetch(`${API}/api/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ module_id: mod.id, provider, message: text, history: chat.map(item => ({ role: item.role, content: item.text })) }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail ?? 'Falha no provider'); setChat(prev => [...prev, { role: 'assistant', text: data.answer, sources: data.sources }]) } catch (error) { setChat(prev => [...prev, { role: 'assistant', text: `Não foi possível obter resposta: ${(error as Error).message}. Verifique o servidor local, a chave do provider ou o Ollama.` }]) } }
  return <div className={dark ? 'app dark' : 'app'} style={{ '--accent': mod.color } as React.CSSProperties}><aside className="sidebar"><div className="logo"><div className="logo-mark">S</div><div><strong>S.O.F.I.A.</strong><span>Plataforma de IA</span></div></div><div className="side-heading">MÓDULOS RAG</div><div className="module-list">{items.map(item => <button key={item.id} className={item.id === mod.id ? 'module-option selected' : 'module-option'} onClick={() => selectModule(item.id)} style={item.id === mod.id ? { '--module-color': item.color } as React.CSSProperties : undefined}><span>{item.icon}</span><b>{item.name}</b><small>{item.docs}</small><i /></button>)}</div><div className="side-divider"/><div className="side-heading">NAVEGAÇÃO</div><nav>{nav.map(item => <button key={item.id} className={page === item.id ? 'nav-item selected' : 'nav-item'} onClick={() => setPage(item.id)}><span>{item.icon}</span>{item.label}<i /></button>)}</nav><div className="side-footer"><div className="online"><i style={{ background: apiOnline ? '#22c55e' : '#f59e0b' }}/>{apiOnline ? 'Servidor MCP online' : 'MCP offline — inicie API'}</div><button className="theme-button" onClick={() => setDark(value => !value)}>☼ &nbsp; {dark ? 'Modo claro' : 'Modo escuro'}</button><div className="profile"><div>AD</div><span><b>Admin</b><small>admin@sofia.ai</small></span></div></div></aside><main className="content"><header className="topbar"><div className="crumb"><span style={{ color: mod.color }}>{mod.icon} &nbsp;{mod.name}</span><b>{pageLabel(page)}</b></div><div className="top-right"><span className="precision">● &nbsp;{mod.accuracy === '-' ? 'sem métricas' : `${mod.accuracy} precisão`}</span><select className="provider-select" value={provider} onChange={event => setProvider(event.target.value as Provider)}><option value="gemini">Gemini</option><option value="claude">Claude</option><option value="ollama">Ollama</option></select><div className="top-avatar" style={{ background: mod.color }}>S</div></div></header>{page === 'dashboard' && <Dashboard mod={mod} online={apiOnline}/>} {page === 'chat' && <Chat mod={mod} provider={provider} message={message} setMessage={setMessage} chat={chat} send={send}/>} {page === 'modules' && <Modules items={items} selected={mod.id} selectModule={selectModule}/>} {page === 'upload' && <Upload mod={mod} onUploaded={refresh}/>} {page === 'neural' && <Neural mod={mod}/>}</main></div>
}
function pageLabel(page: Page) { return ({ dashboard: 'Dashboard', chat: 'Chat Sofia', modules: 'Módulos RAG', upload: 'Upload', neural: 'Rede Neural' } as Record<Page, string>)[page] }
function Dashboard({ mod, online }: { mod: Module; online: boolean }) { const docs = mod.docs; const empty = docs === '0'; const stats = [['Documentos indexados', docs, empty ? 'knowledge vazio' : 'fonte local'], ['Consultas realizadas', mod.queries, 'backend MCP'], ['Precisão média', mod.accuracy, 'sem dado fictício'], ['Tempo de resposta', online ? 'API online' : 'API offline', 'runtime local']]; return <div className="dashboard"><section className="welcome"><h1>Bom dia, módulo <em>{mod.name}</em></h1><p>S.O.F.I.A. — conhecimento consultado diretamente da pasta <code>knowledge/{mod.id}</code>.</p><div className="chips"><span>{mod.category}</span><span>{docs} documentos</span><span>{empty ? 'Aguardando documentos' : 'RAG ativo'}</span></div></section><div className="stats">{stats.map(([label, value, change], index) => <div className="stat" key={label}><div className="stat-top"><small>{label}</small><i>{['▯', 'ϟ', '✓', '▦'][index]}</i></div><strong>{value}</strong><span>{change}</span></div>)}</div><div className="dashboard-grid"><section className="chart-card"><h3>Atividade do módulo</h3><small>Sem dados simulados</small><div className="empty-chart">{empty ? 'Adicione documentos em Upload para começar a indexação.' : 'As métricas de consultas serão alimentadas pelo backend.'}</div></section><section className="recent"><h3>Fonte do conhecimento</h3><div className="source-box"><b>knowledge/{mod.id}</b><small>{docs} arquivos indexáveis encontrados</small><small>PDF · DOCX · TXT · MD · CSV · JSON</small></div></section></div></div> }
function Chat({ mod, provider, message, setMessage, chat, send }: { mod: Module; provider: Provider; message: string; setMessage: (v: string) => void; chat: ChatItem[]; send: () => void }) { return <div className="chat-page"><div className="rag-bar"><span/> RAG {mod.name} — {mod.docs} documentos <b>{provider.toUpperCase()} · resposta real</b></div><div className="chat-messages"><div className="ai-row"><div className="chat-avatar" style={{ background: mod.color }}>S</div><div><div className="bubble">Olá! Sou a Sofia no módulo {mod.name}. {mod.greeting}</div><small>contexto local ativo</small></div></div>{chat.map((item, index) => item.role === 'user' ? <div className="user-row" key={index}><div className="bubble">{item.text}</div><small>você</small></div> : <div className="ai-row" key={index}><div className="chat-avatar" style={{ background: mod.color }}>S</div><div><div className="bubble">{item.text}{item.sources && item.sources.length > 0 && <small className="sources">Fontes: {item.sources.join(', ')}</small>}</div><small>{provider}</small></div></div>)}</div><div className="suggestions"><button onClick={() => setMessage('Quais documentos estão disponíveis?')}>Listar documentos</button><button onClick={() => setMessage('Resuma o conhecimento disponível')}>Resumir conhecimento</button><button onClick={() => setMessage('Execute uma análise baseada nos arquivos')}>Análise</button></div><div className="composer"><input value={message} onChange={event => setMessage(event.target.value)} onKeyDown={event => event.key === 'Enter' && send()} placeholder={`Pergunte ao módulo ${mod.name}...`}/><button onClick={send}>➤</button></div></div> }
function Modules({ items, selected, selectModule }: { items: Module[]; selected: string; selectModule: (id: string) => void }) { return <div className="page-body"><h1>Módulos <em>RAG</em></h1><p className="page-subtitle">Domínios carregados diretamente da pasta knowledge.</p><div className="rag-grid">{items.map(item => <button key={item.id} className={item.id === selected ? 'rag-card active' : 'rag-card'} onClick={() => selectModule(item.id)} style={{ '--module-color': item.color } as React.CSSProperties}><div className="rag-icon">{item.icon}</div><h3>{item.name}</h3><small>{item.category}</small><p>{item.docs} documentos indexados</p><footer><span>knowledge/{item.id}</span><b>{item.docs}</b></footer></button>)}</div></div> }
function Upload({ mod, onUploaded }: { mod: Module; onUploaded: () => void }) {
  const [status, setStatus] = useState('')
  const [dragging, setDragging] = useState(false)
  const uploadFile = async (file?: File) => {
    if (!file) return
    setStatus('Enviando...')
    const form = new FormData()
    form.append('file', file)
    try {
      const response = await fetch(`${API}/api/modules/${mod.id}/upload`, { method: 'POST', body: form })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? 'Falha no upload')
      setStatus(`${data.file} salvo em knowledge/${mod.id}/textos`)
      onUploaded()
    } catch (error) {
      setStatus(`Falha: ${(error as Error).message}`)
    }
  }
  const drop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault()
    setDragging(false)
    void uploadFile(event.dataTransfer.files[0])
  }
  return <div className="page-body narrow"><h1>Upload de <em>Documentos</em></h1><p className="page-subtitle">O arquivo será salvo no módulo <b style={{ color: mod.color }}>knowledge/{mod.id}</b>.</p><label className={dragging ? 'drop-zone is-dragging' : 'drop-zone'} onDragEnter={() => setDragging(true)} onDragOver={event => event.preventDefault()} onDragLeave={() => setDragging(false)} onDrop={drop}>⇧<strong>Arraste arquivos aqui ou clique para selecionar</strong><small>PDF · DOCX · TXT · MD · CSV · JSON — máx. 50 MB</small><input type="file" hidden accept=".pdf,.docx,.txt,.md,.csv,.json" onChange={event => void uploadFile(event.target.files?.[0])}/></label>{status && <div className="upload-status" role="status">{status}</div>}</div>
}
function Neural({ mod }: { mod: Module }) { return <div className="page-body"><h1>Rede Neural <em>S.O.F.I.A.</em></h1><p className="page-subtitle">Inferência numérica real via ferramenta MCP neural_infer.</p><div className="neural-card"><div className="network">{[3, 3, 3, 1].map((count, layer) => <div className="layer" key={layer}>{Array.from({ length: count }, (_, node) => <i key={node} style={{ background: mod.color }}/>)}</div>)}</div><div className="layer-labels"><span>ENTRADA</span><span>OCULTA 1</span><span>OCULTA 2</span><span>SAÍDA</span></div><small className="mcp-note">Ferramentas disponíveis: tensor_multiply · random_generate · neural_infer · monte_carlo_estimate</small></div></div> }
export default App
