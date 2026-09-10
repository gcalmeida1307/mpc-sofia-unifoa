import { useEffect, useRef, type FormEvent, type KeyboardEvent } from "react"

type ChatModule = {
  id: string
  name: string
  color: string
  docs: string
  greeting: string
}
type Provider = "auto" | "openai" | "gemini" | "claude" | "ollama"
type Language = "pt-BR" | "en" | "es"
type ResponseStyle = "concise" | "structured" | "detailed"
type SendOptions = {
  retry?: boolean
  retryOf?: number
  retryAttempt?: number
  silentUser?: boolean
}
type LearningInfo = {
  message?: string | null
  training_scheduled?: boolean
}
type AgentStage = {
  id: string
  stage: string
  status: string
  agent: string
  detail?: string
}
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
  task_route?: string
  retrieval_required?: boolean
  agent_trace?: AgentStage[]
  error?: boolean
}

const MAX_RETRY_ATTEMPTS = 3

const pipelineStages = [
  ["perceive", "ENTRADA", "entende a pergunta", "♙"],
  ["route", "ROTEAMENTO", "identifica o domínio", "◈"],
  ["retrieve", "EVIDÊNCIAS", "busca no RAG", "▥"],
  ["reason", "SÍNTESE", "responde e valida", "▤"],
  ["output", "ENTREGA", "fontes e limites", "▱"],
] as const

const statusLabels: Record<string, string> = {
  complete: "concluído",
  running: "executando",
  blocked: "bloqueado",
  repaired: "reparado localmente",
  rejected: "rejeitado",
  approval_required: "aguarda autorização",
}

function Pipeline({
  trace,
  provider,
  sourceCount,
  verified,
}: {
  trace?: AgentStage[]
  provider?: string
  sourceCount?: number
  verified?: boolean
}) {
  const traceById = new Map((trace ?? []).map((stage) => [stage.id, stage]))

  return (
    <section className="pipeline-shell" aria-label="Fluxo da resposta">
      <div className="pipeline">
        {pipelineStages.map(([id, title, detail, icon], index) => {
          const current = traceById.get(id)
          const status =
            current?.status ?? (id === "perceive" ? "complete" : "idle")
          const statusClass =
            status === "complete" || status === "repaired"
              ? "done"
              : status === "running"
                ? "running"
                : status === "blocked" || status === "rejected"
                  ? "blocked"
                  : "idle"
          return (
            <span className={`pipeline-node ${statusClass}`} key={id}>
              <i aria-hidden="true">{icon}</i>
              <b>{title}</b>
              <small title={current?.detail ?? detail}>
                {current ? (statusLabels[status] ?? status) : detail}
              </small>
              {index < pipelineStages.length - 1 && (
                <em aria-hidden="true">→</em>
              )}
            </span>
          )
        })}
      </div>
      <div className="pipeline-signal" aria-live="polite">
        <span className="pipeline-signal-dot" aria-hidden="true" />
        <b>{trace?.length ? "Fluxo concluído" : "Pronto para consultar"}</b>
        <span>
          {sourceCount
            ? `${sourceCount} fonte(s) local(is) consultada(s)`
            : "A resposta será baseada no conhecimento do módulo"}
        </span>
        {provider && <span>motor: {provider}</span>}
        {verified && <span>✓ resposta verificada</span>}
      </div>
    </section>
  )
}

function StageSummary({ trace }: { trace: AgentStage[] }) {
  const visibleStages = trace.filter((stage) => stage.status !== "pending")
  if (visibleStages.length === 0) return null
  return (
    <div className="trace-summary">
      {visibleStages.map((stage) => (
        <span key={`${stage.id}-${stage.status}`}>
          {stage.stage} · {statusLabels[stage.status] ?? stage.status}
        </span>
      ))}
    </div>
  )
}

function AnswerDetails({
  item,
  provider,
}: {
  item: ChatItem
  provider: Provider
}) {
  const hasDocumentRoute = item.retrieval_required !== false
  const hasDetails = Boolean(
    hasDocumentRoute &&
      (item.sources?.length || item.agent_trace?.length || item.provider || item.verified),
  )
  if (!hasDetails) return null

  return (
    <details className="answer-details">
      <summary>Como a Sofia chegou a esta resposta</summary>
      <div className="answer-details-content">
        {item.sources && item.sources.length > 0 && (
          <div>
            <strong>Fontes consultadas</strong>
            <ul>
              {item.sources.map((source) => (
                <li key={source}>{source}</li>
              ))}
            </ul>
          </div>
        )}
        <div className="answer-facts">
          <span>Domínio: conhecimento local do módulo</span>
          <span>Motor: {item.provider ?? provider}</span>
          {item.verified && <span>Validação: evidência conferida</span>}
        </div>
        {hasDocumentRoute && item.agent_trace && <StageSummary trace={item.agent_trace} />}
      </div>
    </details>
  )
}

function AssistantMessage({
  item,
  mod,
  provider,
  sendFeedback,
  retry,
}: {
  item: ChatItem
  mod: ChatModule
  provider: Provider
  sendFeedback: (
    analyticsId: number,
    feedback: "good" | "medium" | "bad",
  ) => void
  retry: (question: string, analyticsId: number | undefined, attempt: number) => void
}) {
  const canRetry =
    Boolean(item.retry_question) &&
    (item.error || item.feedback === "bad") &&
    (item.retry_attempt ?? 0) < MAX_RETRY_ATTEMPTS

  return (
    <article className="ai-row">
      <div
        className="chat-avatar"
        style={{ background: mod.color }}
        aria-hidden="true"
      >
        S
      </div>
      <div className="message-column">
        <div className="bubble answer-bubble">
          <p className="answer-text">{item.text}</p>
          {item.learning?.message && (
            <small className="learning-note">
              ✦ {item.learning.message}
              {item.learning.training_scheduled &&
                " O treinamento deste módulo foi colocado na fila."}
            </small>
          )}
          {item.privacy?.external_context_redacted && item.privacy.note && (
            <small className="privacy-note">🔒 {item.privacy.note}</small>
          )}
          <AnswerDetails item={item} provider={provider} />
        </div>
        <div className="message-meta">
          <span>{item.provider ?? provider}</span>
          {(item.analytics_id || canRetry) && (
            <div className="message-feedback" aria-label="Avaliar resposta">
              {item.analytics_id && (
                <>
                  <button
                    type="button"
                    className={item.feedback === "good" ? "active" : ""}
                    onClick={() => sendFeedback(item.analytics_id!, "good")}
                  >
                    ✓ Útil
                  </button>
                  <button
                    type="button"
                    className={item.feedback === "bad" ? "active bad" : ""}
                    onClick={() => sendFeedback(item.analytics_id!, "bad")}
                  >
                    Não útil
                  </button>
                </>
              )}
              {canRetry && (
                <button
                  type="button"
                  className="retry-answer"
                  onClick={() =>
                    retry(
                      item.retry_question!,
                      item.analytics_id,
                      (item.retry_attempt ?? 0) + 1,
                    )
                  }
                >
                  {item.error ? "Tentar novamente" : "Tentar outra resposta"}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </article>
  )
}

export default function Chat({
  mod,
  provider,
  responseStyle,
  setResponseStyle,
  language,
  setLanguage,
  patientId,
  setPatientId,
  message,
  setMessage,
  attachment,
  setAttachment,
  chat,
  busy,
  send,
  sendFeedback,
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
  sendFeedback: (
    analyticsId: number,
    feedback: "good" | "medium" | "bad",
  ) => void
}) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const lastAssistant = [...chat]
    .reverse()
    .find((item) => item.role === "assistant")

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [chat.length, busy])

  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return
    textarea.style.height = "auto"
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`
  }, [message])

  const submit = (event: FormEvent) => {
    event.preventDefault()
    void send()
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      void send()
    }
  }

  return (
    <div className="chat-page">
      <div className="rag-bar">
        <span aria-hidden="true" />
        <strong>RAG {mod.name}</strong>
        <small>{mod.docs} documentos · conhecimento local</small>
        <div className="chat-options">
          <label>
            Idioma
            <select
              className="language-select"
              value={language}
              onChange={(event) => setLanguage(event.target.value as Language)}
              disabled={busy}
            >
              <option value="pt-BR">Português-BR</option>
              <option value="en">English</option>
              <option value="es">Español</option>
            </select>
          </label>
          <label>
            Formato
            <select
              className="language-select"
              value={responseStyle}
              onChange={(event) =>
                setResponseStyle(event.target.value as ResponseStyle)
              }
              disabled={busy}
            >
              <option value="concise">Resumo direto</option>
              <option value="structured">Análise estruturada</option>
              <option value="detailed">Detalhada</option>
            </select>
          </label>
        </div>
      </div>

      {mod.id === "medicina" && (
        <div className="clinical-context">
          <span>FHIR R4</span>
          <label>
            <span className="sr-only">ID do paciente</span>
            <input
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              placeholder="ID do paciente (opcional para contexto clínico)"
              disabled={busy}
            />
          </label>
          <small>Contexto clínico externo bloqueado por padrão.</small>
        </div>
      )}

      {(!lastAssistant || lastAssistant.retrieval_required !== false) && (
        <Pipeline
          trace={lastAssistant?.agent_trace}
          provider={lastAssistant?.provider}
          sourceCount={lastAssistant?.sources?.length}
          verified={lastAssistant?.verified}
        />
      )}

      <div
        className="chat-messages"
        role="log"
        aria-live="polite"
        aria-label="Conversa com a Sofia"
      >
        <article className="ai-row">
          <div
            className="chat-avatar"
            style={{ background: mod.color }}
            aria-hidden="true"
          >
            S
          </div>
          <div className="message-column">
            <div className="bubble">
              <p className="answer-text">
                Olá! Sou a Sofia no módulo {mod.name}. {mod.greeting}
              </p>
            </div>
            <small className="message-context">
              Contexto local ativo · resposta em{" "}
              {language === "pt-BR"
                ? "português-BR"
                : language === "en"
                  ? "inglês"
                  : "espanhol"}
            </small>
          </div>
        </article>

        {chat.map((item, index) =>
          item.role === "user" ? (
            <article className="user-row" key={`${item.role}-${index}`}>
              <div className="message-column user-message-column">
                <div className="bubble">
                  {item.attachment && (
                    <span className="attachment-chip">
                      📎 {item.attachment}
                    </span>
                  )}
                  <p className="answer-text">{item.text}</p>
                </div>
                <small className="message-context">Você</small>
              </div>
            </article>
          ) : (
            <AssistantMessage
              key={`${item.role}-${index}`}
              item={item}
              mod={mod}
              provider={provider}
              sendFeedback={sendFeedback}
              retry={(question, analyticsId, attempt) =>
                void send(question, {
                  retry: true,
                  retryOf: analyticsId,
                  retryAttempt: attempt,
                  silentUser: true,
                })
              }
            />
          ),
        )}

        {busy && (
          <article className="ai-row" aria-live="polite">
            <div
              className="chat-avatar is-thinking"
              style={{ background: mod.color }}
              aria-hidden="true"
            >
              S
            </div>
            <div className="message-column">
              <div className="bubble loading-bubble">
                <span className="loading-dots" aria-hidden="true">
                  <i />
                  <i />
                  <i />
                </span>
                Consultando o conhecimento de {mod.name}…
              </div>
              <small className="message-context">
                RAG local · validação em andamento
              </small>
            </div>
          </article>
        )}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      <div className="chat-footer">
        <div className="suggestions" aria-label="Sugestões de consulta">
          <button
            type="button"
            disabled={busy}
            onClick={() => setMessage("Quais documentos estão disponíveis?")}
          >
            Documentos
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => setMessage("Resuma o conhecimento disponível")}
          >
            Resumo da base
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() =>
              setMessage("Execute uma análise baseada nos arquivos")
            }
          >
            Análise
          </button>
        </div>
        {attachment && (
          <div className="selected-attachment" role="status">
            <span>📎 {attachment.name}</span>
            <button
              type="button"
              onClick={() => setAttachment(null)}
              aria-label="Remover arquivo anexado"
            >
              ×
            </button>
          </div>
        )}
        <form className="composer" onSubmit={submit}>
          <button
            type="button"
            className="attach-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={busy}
            aria-label="Anexar documento ou imagem"
            title="Anexar documento ou imagem"
          >
            📎
          </button>
          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".pdf,.docx,.txt,.md,.csv,.json,.xml,.yaml,.yml,.log,.xlsx,.png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff"
            onChange={(event) => {
              setAttachment(event.target.files?.[0] ?? null)
              event.target.value = ""
            }}
          />
          <label className="composer-input">
            <span className="sr-only">Mensagem para o módulo {mod.name}</span>
            <textarea
              ref={textareaRef}
              disabled={busy}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder={
                busy
                  ? "Processando sua consulta…"
                  : `Pergunte ao módulo ${mod.name}…`
              }
            />
            <small>Enter envia · Shift+Enter cria uma nova linha</small>
          </label>
          <button
            className="send-button"
            type="submit"
            disabled={busy || (!message.trim() && !attachment)}
            aria-label="Enviar pergunta"
            title="Enviar pergunta"
          >
            {busy ? "…" : "➤"}
          </button>
        </form>
      </div>
    </div>
  )
}
