import { useEffect, useRef } from "react"

type ChatModule = { id: string; name: string; color: string; docs: string; greeting: string }
type Provider = "auto" | "openai" | "gemini" | "claude" | "ollama"
type Language = "pt-BR" | "en" | "es"
type ResponseStyle = "concise" | "structured" | "detailed"
type SendOptions = { retry?: boolean; retryOf?: number; retryAttempt?: number; silentUser?: boolean }
type LearningInfo = { message?: string | null; training_scheduled?: boolean }
type ChatItem = {
  role: "user" | "assistant"
  text: string
  sources?: string[]
  provider?: string
  verified?: boolean
  analytics_id?: number
  feedback?: "good" | "medium" | "bad"
  retry_question?: string
  retry_attempt?: number
  learning?: LearningInfo
  privacy?: { external_context_redacted?: boolean; note?: string }
  attachment?: string
  agent_trace?: Array<{ id: string; stage: string; status: string; agent: string; detail?: string }>
}

const MAX_RETRY_ATTEMPTS = 3

function Pipeline({
  trace,
  provider,
  sourceCount,
  verified,
}: {
  trace?: ChatItem["agent_trace"]
  provider?: string
  sourceCount?: number
  verified?: boolean
}) {
  const stages = [
    ["perceive", "USUÁRIO", "prompt", "♙"],
    ["route", "CORE / PLANNER", "percebe · roteia · planeja", "◈"],
    ["retrieve", "RAG + MCP", "busca evidência local", "▥"],
    ["reason", "LLM / CRITIC", "responde · valida", "▤"],
    ["output", "OUTPUT", "resposta", "▱"],
  ] as const
  const traceById = new Map((trace ?? []).map((stage) => [stage.id, stage]))
  const statusLabel: Record<string, string> = { complete: "concluído", running: "executando", blocked: "bloqueado", repaired: "reparado localmente", rejected: "rejeitado" }
  return (
    <div className="pipeline-shell">
      <div className="pipeline" aria-label="Fluxo real da resposta">
        {stages.map(([id, title, fallbackDetail, icon], index) => {
          const current = traceById.get(id)
          const status = current?.status ?? (id === "perceive" ? "complete" : "idle")
          const statusClass = status === "complete" || status === "repaired" ? "done" : status === "running" ? "running" : status === "blocked" || status === "rejected" ? "blocked" : "idle"
          const node = <span className={`pipeline-node ${statusClass}`} key={id} title={current?.detail ?? fallbackDetail}><i>{icon}</i><b>{title}</b><small>{current ? statusLabel[status] ?? status : fallbackDetail}</small></span>
          return index < stages.length - 1 ? [node, <em key={`arrow-${index}`}>→</em>] : [node]
        }).flat()}
      </div>
      <div className="pipeline-signal" aria-live="polite"><span className="pipeline-signal-dot" /><b>{trace?.length ? "Pipeline concluído" : "Pipeline pronto"}</b><span>{sourceCount ? `${sourceCount} fonte(s) local(is) consultada(s)` : "Aguardando uma pergunta para consultar o RAG"}</span><span>IA: {provider ?? "aguardando"}</span><span>{verified ? "✓ resposta verificada" : "Rede neural e Monte Carlo disponíveis em Análise"}</span></div>
    </div>
  )
}

export default function Chat({
  mod, provider, responseStyle, setResponseStyle, language, setLanguage, patientId, setPatientId,
  message, setMessage, attachment, setAttachment, chat, busy, send, sendFeedback,
}: {
  mod: ChatModule
  provider: Provider
  responseStyle: ResponseStyle
  setResponseStyle: (value: ResponseStyle) => void
  language: Language
  setLanguage: (value: Language) => void
  patientId: string
  setPatientId: (value: string) => void
  message: string
  setMessage: (value: string) => void
  attachment: File | null
  setAttachment: (file: File | null) => void
  chat: ChatItem[]
  busy: boolean
  send: (overrideMessage?: string, options?: SendOptions) => Promise<void>
  sendFeedback: (analyticsId: number, feedback: "good" | "medium" | "bad") => void
}) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const lastAssistant = [...chat].reverse().find((item) => item.role === "assistant")
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" }) }, [chat.length, busy])
  return (
    <div className="chat-page">
      <div className="rag-bar"><span /> RAG {mod.name} — {mod.docs} documentos <div className="chat-options"><label>Idioma<select className="language-select" value={language} onChange={(event) => setLanguage(event.target.value as Language)} disabled={busy}><option value="pt-BR">Português-BR</option><option value="en">English</option><option value="es">Español</option></select></label><label>Resposta<select className="language-select" value={responseStyle} onChange={(event) => setResponseStyle(event.target.value as ResponseStyle)} disabled={busy}><option value="concise">Resumo direto</option><option value="structured">Análise estruturada</option><option value="detailed">Detalhada</option></select></label><b>{provider === "auto" ? "AUTO · fallback seguro" : provider.toUpperCase()} · RAG local</b></div></div>
      {mod.id === "medicina" && <div className="clinical-context"><span>FHIR R4</span><input value={patientId} onChange={(event) => setPatientId(event.target.value)} placeholder="ID do paciente (opcional para contexto clínico)" disabled={busy} /><small>contexto local · provider externo bloqueado por padrão</small></div>}
      <Pipeline trace={lastAssistant?.agent_trace} provider={lastAssistant?.provider} sourceCount={lastAssistant?.sources?.length} verified={lastAssistant?.verified} />
      <div className="chat-messages" role="log" aria-live="polite">
        <div className="ai-row"><div className="chat-avatar" style={{ background: mod.color }}>S</div><div><div className="bubble">Olá! Sou a Sofia no módulo {mod.name}. {mod.greeting}</div><small>contexto local ativo · resposta em {language === "pt-BR" ? "português-BR" : language === "en" ? "inglês" : "espanhol"}</small></div></div>
        {chat.map((item, index) => item.role === "user" ? <div className="user-row" key={index}><div className="bubble">{item.attachment && <span className="attachment-chip">📎 {item.attachment}</span>}<span className="answer-text">{item.text}</span></div><small>você</small></div> : <div className="ai-row" key={index}><div className="chat-avatar" style={{ background: mod.color }}>S</div><div><div className="bubble"><span className="answer-text">{item.text}</span>{item.learning?.message && <small className="learning-note">✦ {item.learning.message}{item.learning.training_scheduled && " O treinamento deste módulo foi colocado na fila."}</small>}{item.privacy?.external_context_redacted && item.privacy.note && <small className="privacy-note">🔒 {item.privacy.note}</small>}{item.sources && item.sources.length > 0 && <small className="sources">Fontes: {item.sources.join(", ")}</small>}</div><div className="message-meta">{item.agent_trace && item.agent_trace.length > 0 && <small className="agent-trace">Fluxo: {item.agent_trace.filter((stage) => stage.status !== "pending").map((stage) => { const labels: Record<string, string> = { complete: "ok", blocked: "bloqueado", rejected: "rejeitado", approval_required: "aguarda autorização" }; return `${stage.stage} · ${labels[stage.status] ?? stage.status}` }).join(" → ")}</small>}<small className="message-provider">{item.provider ?? provider}</small>{item.analytics_id && <span className="message-feedback" aria-label="Avaliar resposta"><button type="button" className={item.feedback === "good" ? "active" : ""} onClick={() => sendFeedback(item.analytics_id!, "good")}>✓ Útil</button><button type="button" className={item.feedback === "bad" ? "active bad" : ""} onClick={() => sendFeedback(item.analytics_id!, "bad")}>Não útil</button>{item.feedback === "bad" && item.retry_question && (item.retry_attempt ?? 0) < MAX_RETRY_ATTEMPTS && <button type="button" className="retry-answer" onClick={() => void send(item.retry_question, { retry: true, retryOf: item.analytics_id, retryAttempt: (item.retry_attempt ?? 0) + 1, silentUser: true })}>Tentar outra resposta</button>}</span>}</div></div></div>)}
        {busy && <div className="ai-row"><div className="chat-avatar" style={{ background: mod.color }}>S</div><div><div className="bubble">Consultando documentos locais e gerando resumo...</div><small>busca semântica + MCP + RAG em andamento</small></div></div>}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>
      <div className="suggestions"><button disabled={busy} onClick={() => setMessage("Quais documentos estão disponíveis?")}>Listar documentos</button><button disabled={busy} onClick={() => setMessage("Resuma o conhecimento disponível")}>Resumir conhecimento</button><button disabled={busy} onClick={() => setMessage("Execute uma análise baseada nos arquivos")}>Análise</button></div>
      {attachment && <div className="selected-attachment"><span>📎 {attachment.name}</span><button type="button" onClick={() => setAttachment(null)} aria-label="Remover arquivo anexado">×</button></div>}
      <div className="composer"><button type="button" className="attach-button" onClick={() => fileInputRef.current?.click()} disabled={busy} aria-label="Anexar arquivo de texto ou imagem" title="Anexar arquivo de texto ou imagem">📎</button><textarea disabled={busy} value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void send() } }} rows={1} placeholder={busy ? "Processando sua pergunta..." : `Pergunte ao módulo ${mod.name}...`} /><input ref={fileInputRef} type="file" hidden accept=".pdf,.docx,.txt,.md,.csv,.json,.xml,.yaml,.yml,.log,.xlsx,.png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff" onChange={(event) => { setAttachment(event.target.files?.[0] ?? null); event.target.value = "" }} /><button type="button" disabled={busy || (!message.trim() && !attachment)} onClick={() => void send()} aria-label="Enviar prompt" title="Enviar prompt">{busy ? "…" : "➤"}</button></div>
    </div>
  )
}
