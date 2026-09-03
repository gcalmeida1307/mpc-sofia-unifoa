import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
} from "react"
import { knowledgeModules } from "./knowledge"
import PipelineExplorer from "./features/pipeline/PipelineExplorer"
import ChatView from "./features/chat/Chat"

type Page = "dashboard" | "chat" | "modules" | "upload" | "neural" | "connections" | "pipeline" | "access"
type Provider = "auto" | "openai" | "gemini" | "claude" | "ollama"
type Language = "pt-BR" | "en" | "es"
type Module = typeof knowledgeModules[number]
type ResponseStyle = "concise" | "structured" | "detailed"
type LearningInfo = {
  is_retry?: boolean
  attempt?: number
  message?: string | null
  retry_of?: number | null
  provider_mode?: string
  offline_material?: {
    stored: boolean
    source_count: number
    sources: string[]
    note: string
  }
  external_provider_used?: boolean
  needs_improvement?: boolean
  training_scheduled?: boolean
  learning_event_stored?: boolean
  offline_sources?: string[]
  external_research_status?: string
  external_research_stored?: number
}
type AnswerPrivacy = {
  external_context_redacted?: boolean
  redacted_fields?: number
  note?: string
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
  privacy?: AnswerPrivacy
  attachment?: string
  agent_trace?: Array<{
    id: string
    stage: string
    status: string
    agent: string
    detail?: string
  }>
}
type AuthUser = {
  user_code: string
  email: string
  name: string
  role: string
  scopes: string[]
  must_change_password: boolean
  two_factor_enabled?: boolean
  active?: boolean
  last_login_at?: string | null
  last_seen_at?: string | null
  blocked_at?: string | null
  blocked_reason?: string | null
}
type AccessRequest = {
  id: number
  request_code: string
  requested_module?: string
  email: string
  name: string
  requested_scopes: string[]
  status: string
  created_at: string
}
type AdminUser = AuthUser & {
  session_count: number
  tokens: Array<{
    fingerprint: string
    created_at: string
    last_seen_at?: string | null
    last_rotated_at?: string | null
    expires_at: number
    rotation_seconds: number
  }>
}
type Capabilities = {
  ocr?: { available: boolean; engine: string; language?: string }
  links?: { storage: string; postgres_configured: boolean }
  providers?: Record<Provider, boolean>
  openai_store_responses?: boolean
  models?: { ollama?: string; openai?: string; gemini?: string; claude?: string }
  privacy?: {
    mode: string
    external_data_allowed: boolean
    external_clinical_allowed: boolean
    audit_log: boolean
    audit_retention_days: number
    data_minimization: boolean
    external_redaction?: boolean
    redaction_scope?: string
    note: string
  }
  integrations?: {
    storage?: string
    dlq_pending?: number
    jobs?: { total: number; running: number; failed: number }
    connectors?: {
      tasy?: { configured: boolean; status: string; transport?: string }
    }
  }
  training?: {
    sequential: boolean
    queued_modules: string[]
    active_modules: string[]
  }
  mcp?: { transport_http: string; transport_stdio: boolean }
  agents?: {
    core: boolean
    planner: boolean
    critic: boolean
    memory: boolean
    vision: string
    execution: string
  }
  expansion?: {
    enabled: boolean
    admin_only: boolean
    status_endpoint: string
    queue_persistent: boolean
    bounded_pages_per_topic: number
    module_sequential_training: boolean
  }
}
type ExpansionStatus = {
  settings?: {
    enabled?: boolean
    paused?: boolean
    interval_seconds?: number
    max_pages_per_topic?: number
    max_topics_per_cycle?: number
  }
  queue_pending: number
  topics: Array<{
    module_id: string
    topic_key: string
    main_topic: string
    query_count: number
    expansion_state: string
    priority: number
  }>
  sources_by_status: Record<string, number>
  documents_by_status: Record<string, number>
  processing_errors: number
  storage_bytes: number
  last_cycle?: { finished_at?: string; status?: string; pages_new?: number; errors?: number } | null
}
type ThemeAnalytics = {
  period_days: number
  module_id?: string | null
  total_queries: number
  top_themes: Array<{
    module_id: string
    theme: string
    intent: string
    consultations: number
    last_consulted_at?: string | null
    source_uses: number
    verified_consultations: number
    good_answers: number
    medium_answers: number
    bad_answers: number
    quality_score: number | null
    evaluated_answers: number
    needs_improvement: boolean
  }>
  feedback_summary?: {
    good_answers: number
    medium_answers: number
    bad_answers: number
    evaluated_answers: number
    quality_score: number | null
    needs_improvement: boolean
  }
  by_user?: Array<{
    user_code: string
    consultations: number
    themes: number
  }>
  storage?: string
  stores_raw_content: boolean
}
type SendOptions = {
  retry?: boolean
  retryOf?: number
  retryAttempt?: number
  silentUser?: boolean
}

const API =
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" &&
  !["127.0.0.1", "localhost"].includes(window.location.hostname)
    ? `${window.location.protocol}//${window.location.hostname}:8787`
    : "http://127.0.0.1:8787")
const MAX_RETRY_ATTEMPTS = 3
const nav = [
  { id: "dashboard" as Page, label: "Dashboard", icon: "▦" },
  { id: "chat" as Page, label: "Chat Sofia", icon: "▱" },
  { id: "modules" as Page, label: "Módulos RAG", icon: "▱" },
  { id: "upload" as Page, label: "Upload", icon: "↥" },
  { id: "neural" as Page, label: "Rede Neural", icon: "♧" },
  { id: "connections" as Page, label: "Conexões & Fluxos", icon: "⎇" },
  { id: "pipeline" as Page, label: "Pipeline Explorer", icon: "◎" },
  { id: "access" as Page, label: "Acessos", icon: "♙" },
]

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("sofia_token"))
  const [user, setUser] = useState<AuthUser | null>(null)
  const [checking, setChecking] = useState(Boolean(token))
  const [items, setItems] = useState<Module[]>(knowledgeModules)
  const [moduleId, setModuleId] = useState(knowledgeModules[0]?.id ?? "")
  const [page, setPage] = useState<Page>("dashboard")
  const [dark, setDark] = useState(
    () => localStorage.getItem("sofia_theme") !== "light",
  )
  const [provider, setProvider] = useState<Provider>("auto")
  const [language, setLanguage] = useState<Language>("pt-BR")
  const [responseStyle, setResponseStyle] = useState<ResponseStyle>("structured")
  const [patientId, setPatientId] = useState("")
  const [message, setMessage] = useState("")
  const [attachment, setAttachment] = useState<File | null>(null)
  const [chat, setChat] = useState<ChatItem[]>([])
  const [chatBusy, setChatBusy] = useState(false)
  const [apiOnline, setApiOnline] = useState(false)
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null)
  const feedbackInFlight = useRef(new Set<number>())
  const mod = useMemo(
    () => items.find((item) => item.id === moduleId) ?? items[0],
    [items, moduleId],
  )

  const authFetch = (path: string, init: RequestInit = {}) =>
    fetch(`${API}${path}`, {
      ...init,
      headers: {
        ...(init.body instanceof FormData
          ? {}
          : { "Content-Type": "application/json" }),
        ...(init.headers || {}),
        Authorization: `Bearer ${token}`,
      },
    })
  const refresh = async () => {
    if (!token) return
    try {
      const response = await authFetch("/api/modules")
      if (!response.ok) throw new Error()
      const data = (await response.json()) as Array<Record<string, unknown>>
      setItems(
        data.map((item) => {
          const local = knowledgeModules.find(
            (candidate) => candidate.id === item.id,
          )
          return {
            ...local,
            id: String(item.id),
            name: String(item.name),
            category: String(item.category),
            color: String(item.color),
            icon: String(item.icon),
            docs: Number(item.documents).toLocaleString("pt-BR"),
            queries: "-",
            accuracy: "-",
            greeting: local?.greeting ?? "Consulte os documentos deste módulo.",
            manager: String(
              item.manager ?? local?.manager ?? "Gestor do módulo",
            ),
            focus: String(
              item.focus ??
                local?.focus ??
                "Conhecimento e procedimentos do domínio.",
            ),
            documentsByType:
              item.documents_by_type as Record<string, number> | undefined ??
              {},
            links: Number(item.links ?? 0),
            linkStorage: String(item.link_storage ?? "local-json"),
          } as Module
        }),
      )
      const capabilityResponse = await authFetch("/api/capabilities")
      if (capabilityResponse.ok)
        setCapabilities((await capabilityResponse.json()) as Capabilities)
      setApiOnline(true)
    } catch {
      setApiOnline(false)
    }
  }
  useEffect(() => {
    if (!token) {
      setChecking(false)
      return
    }
    authFetch("/api/auth/me")
      .then(async (response) => {
        if (!response.ok) throw new Error()
        const data = (await response.json()) as { user: AuthUser }
        setUser(data.user)
      })
      .then(() => {
        setChecking(false)
        void refresh()
      })
      .catch(() => {
        localStorage.removeItem("sofia_token")
        setToken(null)
        setUser(null)
        setChecking(false)
      })
  }, [token])
  useEffect(() => {
    if (!token) return
    const knowledgeRefreshTimer = window.setInterval(() => {
      void refresh()
    }, 15_000)
    return () => window.clearInterval(knowledgeRefreshTimer)
  }, [token])
  useEffect(() => {
    setChat([])
  }, [moduleId])
  useEffect(() => {
    if (!token) return
    const rotationTimer = window.setInterval(
      async () => {
        try {
          const response = await authFetch("/api/auth/token/rotate", {
            method: "POST",
          })
          if (!response.ok) return
          const data = (await response.json()) as { token?: string }
          if (data.token) {
            localStorage.setItem("sofia_token", data.token)
            setToken(data.token)
          }
        } catch {
          // A normal request will clear the session if the server is unavailable.
        }
      },
      10 * 60 * 1000,
    )
    return () => window.clearInterval(rotationTimer)
  }, [token])
  if (checking)
    return (
      <div className="login-screen">
        <div className="login-card">
          <div className="login-spinner" />
          Verificando sessão local...
        </div>
      </div>
    )
  if (!token)
    return (
      <Login
        onLogin={(value, loggedUser) => {
          localStorage.setItem("sofia_token", value)
          setToken(value)
          setUser(loggedUser)
        }}
      />
    )
  if (!mod)
    return (
      <div className="app dark">
        <div className="page-body">
          <h1>Adicione módulos em knowledge</h1>
        </div>
      </div>
    )
  if (user?.must_change_password)
    return (
      <FirstAccess
        authFetch={authFetch}
        onDone={() =>
          setUser((current) =>
            current ? { ...current, must_change_password: false } : current,
          )
        }
        onLogout={() => {
          localStorage.removeItem("sofia_token")
          setToken(null)
          setUser(null)
        }}
      />
    )
  if (user?.role === "admin" && !user.two_factor_enabled)
    return (
      <TwoFactorEnrollment
        authFetch={authFetch}
        onDone={() =>
          setUser((current) =>
            current ? { ...current, two_factor_enabled: true } : current,
          )
        }
        onLogout={() => {
          localStorage.removeItem("sofia_token")
          setToken(null)
          setUser(null)
        }}
      />
    )
  const selectModule = (id: string) => {
    setModuleId(id)
    setPage("dashboard")
  }
  const logout = () => {
    void authFetch("/api/auth/logout", { method: "POST" })
    localStorage.removeItem("sofia_token")
    setToken(null)
    setUser(null)
  }
  const send = async (overrideMessage?: string, options: SendOptions = {}) => {
    const selectedAttachment = overrideMessage ? null : attachment
    const isRetry = options.retry === true
    const text =
      overrideMessage?.trim() ||
      message.trim() ||
      (selectedAttachment
        ? `Resuma o conteúdo do arquivo anexado: ${selectedAttachment.name}`
        : "")
    if (!text || chatBusy) return
    setMessage("")
    setAttachment(null)
    setChatBusy(true)
    if (!options.silentUser) {
      setChat((prev) => [
        ...prev,
        { role: "user", text, attachment: selectedAttachment?.name },
      ])
    }
    try {
      if (selectedAttachment) {
        const form = new FormData()
        form.append("file", selectedAttachment)
        const uploadResponse = await authFetch(
          `/api/modules/${mod.id}/upload`,
          {
            method: "POST",
            body: form,
          },
        )
        const uploadData = await uploadResponse.json()
        if (!uploadResponse.ok && uploadResponse.status !== 409)
          throw new Error(uploadData.detail ?? "Falha ao anexar o arquivo")
        void refresh()
      }
      const response = await authFetch("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          module_id: mod.id,
          provider,
          language,
          response_style: responseStyle,
          message: text,
          retry: isRetry,
          retry_of: options.retryOf,
          retry_attempt: options.retryAttempt ?? 0,
          patient_id: patientId.trim() || undefined,
          history: chat.map((item) => ({
            role: item.role,
            content: item.text,
          })),
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? "Falha no provider")
      setChat((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources,
          provider: data.provider,
          verified: data.verified,
          agent_trace: data.agent_trace,
          analytics_id: data.analytics_id,
          retry_question: text,
          retry_attempt: options.retryAttempt ?? 0,
          learning: data.learning,
          privacy: data.privacy,
        },
      ])
    } catch (error) {
      setChat((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `Não foi possível obter resposta: ${(error as Error).message}.`,
        },
      ])
    } finally {
      setChatBusy(false)
    }
  }
  const sendFeedback = async (
    analyticsId: number,
    feedback: "good" | "medium" | "bad",
  ) => {
    if (feedbackInFlight.current.has(analyticsId)) return
    const answerItem = chat.find((item) => item.analytics_id === analyticsId)
    if (
      feedback === "bad" &&
      answerItem?.learning?.external_research_status &&
      answerItem.learning.external_research_status !== "not_requested"
    ) {
      return
    }
    feedbackInFlight.current.add(analyticsId)
    if (feedback === "bad" && user?.user_code === "AG000001") {
      setChat((prev) =>
        prev.map((item) =>
          item.analytics_id === analyticsId
            ? {
                ...item,
                learning: {
                  ...item.learning,
                  message:
                    "O SOFIA está consultando referências públicas com anonimização e filtros de LGPD/HL7. Aguarde a nova tentativa...",
                },
              }
            : item,
        ),
      )
    }
    try {
      const response = await authFetch("/api/analytics/feedback", {
        method: "POST",
        // The server uses the original prompt only for the one bounded,
        // admin-only external recovery pass. It is not persisted in analytics.
        body: JSON.stringify({
          analytics_id: analyticsId,
          feedback,
          question: answerItem?.retry_question,
        }),
      })
      if (!response.ok) throw new Error()
      const data = (await response.json()) as {
        retry_recommended?: boolean
        learning?: LearningInfo
      }
      setChat((prev) =>
        prev.map((item) =>
          item.analytics_id === analyticsId
            ? {
                ...item,
                feedback,
                learning: data.learning
                  ? { ...item.learning, ...data.learning }
                  : item.learning,
              }
            : item,
        ),
      )
      const nextAttempt = (answerItem?.retry_attempt ?? 0) + 1
      if (
        feedback === "bad" &&
        data.retry_recommended &&
        answerItem?.retry_question &&
        nextAttempt <= MAX_RETRY_ATTEMPTS
      ) {
        await send(answerItem.retry_question, {
          retry: true,
          retryOf: analyticsId,
          retryAttempt: nextAttempt,
          silentUser: true,
        })
      }
    } catch {
      // Feedback is optional; a temporary analytics outage must not interrupt chat.
    } finally {
      feedbackInFlight.current.delete(analyticsId)
    }
  }
  return (
    <div
      className={dark ? "app dark" : "app"}
      style={{ "--accent": mod.color } as React.CSSProperties}
    >
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-mark">S</div>
          <div>
            <strong>S.O.F.I.A.</strong>
            <span>Plataforma de IA</span>
          </div>
        </div>
        <div className="side-heading">MÓDULOS RAG</div>
        <div className="module-list">
          {items.map((item) => (
            <button
              key={item.id}
              className={
                item.id === mod.id ? "module-option selected" : "module-option"
              }
              onClick={() => selectModule(item.id)}
              style={
                item.id === mod.id
                  ? { "--module-color": item.color } as React.CSSProperties
                  : undefined
              }
            >
              <span>{item.icon}</span>
              <b>{item.name}</b>
              <small>{item.docs}</small>
              <i />
            </button>
          ))}
        </div>
        <div className="side-divider" />
        <div className="side-heading">NAVEGAÇÃO</div>
        <nav>
          {nav
            .filter(
              (item) =>
                (item.id !== "access" && item.id !== "pipeline") ||
                user?.role === "admin" &&
                (item.id !== "pipeline" || user?.user_code === "AG000001"),
            )
            .map((item) => (
              <button
                key={item.id}
                className={page === item.id ? "nav-item selected" : "nav-item"}
                onClick={() => setPage(item.id)}
              >
                <span>{item.icon}</span>
                {item.label}
                <i />
              </button>
            ))}
        </nav>
        <div className="side-footer">
          <div className="online">
            <i style={{ background: apiOnline ? "#22c55e" : "#f59e0b" }} />
            {apiOnline ? "Servidor MCP online" : "MCP offline"}
          </div>
          <button
            className="theme-button"
            onClick={() =>
              setDark((value) => {
                localStorage.setItem("sofia_theme", value ? "light" : "dark")
                return !value
              })
            }
          >
            ☼ &nbsp; {dark ? "Modo claro" : "Modo escuro"}
          </button>
          <button className="logout-button" onClick={logout}>
            ↪ &nbsp; Sair
          </button>
          <div className="profile">
            <div>{user?.user_code?.slice(-2) ?? "US"}</div>
            <span>
              <b>{user?.name ?? "Usuário"}</b>
              <small>
                {user?.user_code ?? ""} · {user?.email ?? ""}
              </small>
            </span>
          </div>
        </div>
      </aside>
      <main className="content">
        <header className="topbar">
          <div className="crumb">
            <span style={{ color: mod.color }}>
              {mod.icon} &nbsp;{mod.name}
            </span>
            <b>{pageLabel(page)}</b>
          </div>
          <div className="top-right">
            <span className="precision">● &nbsp;{mod.docs} documentos</span>
            <select
              className="provider-select"
              value={provider}
              onChange={(event) => setProvider(event.target.value as Provider)}
            >
              <option value="auto">Automático</option>
              <option
                value="openai"
                disabled={
                  capabilities !== null && capabilities.providers?.openai === false
                }
              >
                OpenAI Responses{capabilities?.providers?.openai === false ? " (bloqueado)" : ""}
              </option>
              <option
                value="gemini"
                disabled={
                  capabilities !== null && capabilities.providers?.gemini === false
                }
              >
                Gemini{capabilities?.providers?.gemini === false ? " (bloqueado)" : ""}
              </option>
              <option
                value="claude"
                disabled={
                  capabilities !== null && capabilities.providers?.claude === false
                }
              >
                Claude{capabilities?.providers?.claude === false ? " (bloqueado)" : ""}
              </option>
              <option value="ollama">Ollama</option>
            </select>
            <div className="top-avatar" style={{ background: mod.color }}>
              S
            </div>
          </div>
        </header>
        {page === "dashboard" && (
          <Dashboard
            mod={mod}
            online={apiOnline}
            authFetch={authFetch}
            isAdmin={user?.user_code === "AG000001"}
          />
        )}{" "}
        {page === "chat" && (
          <ChatView
            mod={mod}
            provider={provider}
            responseStyle={responseStyle}
            setResponseStyle={setResponseStyle}
            language={language}
            setLanguage={setLanguage}
            patientId={patientId}
            setPatientId={setPatientId}
            message={message}
            setMessage={setMessage}
            attachment={attachment}
            setAttachment={setAttachment}
            chat={chat}
            busy={chatBusy}
            send={send}
            sendFeedback={sendFeedback}
          />
        )}{" "}
        {page === "modules" && (
          <Modules
            items={items}
            selected={mod.id}
            selectModule={selectModule}
          />
        )}{" "}
        {page === "upload" && (
          <Upload mod={mod} authFetch={authFetch} onUploaded={refresh} />
        )}{" "}
        {page === "neural" && <Neural mod={mod} authFetch={authFetch} />}{" "}
        {page === "connections" && (
          <Connections items={items} capabilities={capabilities} />
        )}{" "}
        {page === "pipeline" && user?.user_code === "AG000001" && (
          <PipelineExplorer mod={mod} authFetch={authFetch} items={items} />
        )}
        {page === "access" && user?.role === "admin" && (
          <>
            <AccessControl authFetch={authFetch} />
            <UserAdministration authFetch={authFetch} />
          </>
        )}
      </main>
    </div>
  )
}

function Login({
  onLogin,
}: {
  onLogin: (token: string, user: AuthUser) => void
}) {
  const [identifier, setIdentifier] = useState("")
  const [password, setPassword] = useState("")
  const [otp, setOtp] = useState("")
  const [requires2FA, setRequires2FA] = useState(false)
  const [requesting, setRequesting] = useState(false)
  const [activating, setActivating] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError("")
    try {
      const response = await fetch(`${API}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier,
          password,
          ...(requires2FA ? { otp } : {}),
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        requires_2fa?: boolean
        token?: string
        user?: AuthUser
      }
      if (data.requires_2fa) {
        setRequires2FA(true)
        setError("Digite o código de 6 dígitos do seu aplicativo autenticador.")
        setBusy(false)
        return
      }
      if (!response.ok || !data.token || !data.user)
        throw new Error(data.detail ?? "Usuário ou senha inválidos")
      onLogin(data.token, data.user)
    } catch (reason) {
      setError((reason as Error).message)
      setBusy(false)
    }
  }
  if (requesting)
    return (
      <RequestAccess
        onBack={() => {
          setRequesting(false)
          setError("")
        }}
      />
    )
  if (activating)
    return (
      <ActivateAccount
        onBack={() => {
          setActivating(false)
          setError("")
        }}
      />
    )
  if (resetting)
    return (
      <ResetPassword
        onBack={() => {
          setResetting(false)
          setError("")
        }}
      />
    )
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card" onSubmit={submit}>
        <div className="login-logo">S</div>
        <div className="login-kicker">S.O.F.I.A. · PLATAFORMA LOCAL</div>
        <h1>Bem-vindo de volta.</h1>
        <p>Entre com sua matrícula ou e-mail cadastrado.</p>
        <label>
          Usuário ou e-mail
          <input
            type="text"
            value={identifier}
            onChange={(event) => setIdentifier(event.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {requires2FA && (
          <label>
            Código 2FA
            <input
              inputMode="numeric"
              pattern="\d{6}"
              maxLength={6}
              value={otp}
              onChange={(event) =>
                setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))
              }
              autoComplete="one-time-code"
              required
            />
          </label>
        )}
        {error && <div className="login-error">{error}</div>}
        <button className="login-submit" disabled={busy}>
          {busy
            ? "Entrando..."
            : requires2FA
              ? "Validar e entrar →"
              : "Entrar no workspace →"}
        </button>
        <button
          type="button"
          className="login-link"
          onClick={() => setRequesting(true)}
        >
          Ainda não tenho acesso · Solicitar conta
        </button>
        <button
          type="button"
          className="login-link"
          onClick={() => setActivating(true)}
        >
          Já fui aprovado · Ativar conta
        </button>
        <button
          type="button"
          className="login-link"
          onClick={() => setResetting(true)}
        >
          Tenho token de reset · Redefinir senha
        </button>
        <small>
          Use o código do usuário ou o e-mail cadastrado. A senha é definida
          localmente e nunca aparece nesta tela.
        </small>
      </form>
    </div>
  )
}

function ResetPassword({ onBack }: { onBack: () => void }) {
  const [userCode, setUserCode] = useState("")
  const [resetToken, setResetToken] = useState("")
  const [password, setPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (password !== confirmation) {
      setError("A confirmação não confere.")
      return
    }
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await fetch(`${API}/api/auth/password/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          reset_token: resetToken,
          new_password: password,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        message?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível redefinir a senha")
      setMessage(data.message ?? "Senha redefinida. Você já pode entrar.")
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card request-card" onSubmit={submit}>
        <button type="button" className="back-link" onClick={onBack}>
          ← Voltar para o login
        </button>
        <div className="login-logo">S</div>
        <div className="login-kicker">RECUPERAÇÃO DE ACESSO</div>
        <h1>Redefina sua senha.</h1>
        <p>
          Use a matrícula e o token de recuperação fornecidos pela AG000001. O
          token expira em 10 minutos e pode ser usado uma única vez.
        </p>
        <label>
          Matrícula
          <input
            value={userCode}
            onChange={(event) => setUserCode(event.target.value.toUpperCase())}
            placeholder="Ex.: IN000001"
            pattern="[A-Z]{2}\d{6}"
            required
          />
        </label>
        <label>
          Token de recuperação
          <input
            value={resetToken}
            onChange={(event) => setResetToken(event.target.value)}
            autoComplete="one-time-code"
            required
          />
        </label>
        <label>
          Nova senha
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
          <small>Use maiúscula, minúscula, número e caractere especial.</small>
        </label>
        <label>
          Confirme a nova senha
          <input
            type="password"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
        </label>
        {error && <div className="login-error">{error}</div>}
        {message && <div className="login-success">{message}</div>}
        <button className="login-submit" disabled={busy}>
          {busy ? "Redefinindo..." : "Redefinir senha →"}
        </button>
      </form>
    </div>
  )
}

function ScopePicker({
  value,
  onChange,
}: {
  value: string[]
  onChange: (next: string[]) => void
}) {
  const toggle = (scope: string) => {
    if (scope === "CORE") {
      onChange(value.includes("CORE") ? [] : ["CORE"])
      return
    }
    const next = value.filter((item) => item !== "CORE")
    onChange(
      next.includes(scope)
        ? next.filter((item) => item !== scope)
        : [...next, scope],
    )
  }
  return (
    <div className="scope-grid">
      {[
        ["CORE", "Todos os módulos"],
        ...knowledgeModules.map((item) => [item.id, item.name]),
      ].map(([id, label]) => (
        <label
          className={
            value.includes(id) ? "scope-option selected" : "scope-option"
          }
          key={id}
        >
          <input
            type="checkbox"
            checked={value.includes(id)}
            onChange={() => toggle(id)}
          />
          <span>{label}</span>
        </label>
      ))}
    </div>
  )
}

function RequestAccess({ onBack }: { onBack: () => void }) {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [requestedModule, setRequestedModule] = useState(
    knowledgeModules[0]?.id ?? "",
  )
  const [scopes, setScopes] = useState<string[]>([])
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await fetch(`${API}/api/auth/requests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          requested_module: requestedModule,
          scopes,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        request_code?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível enviar a solicitação")
      setMessage(
        `Solicitação ${data.request_code} enviada. A AG000001 analisará o acesso e enviará a matrícula e o token de ativação por um canal seguro.`,
      )
      setName("")
      setEmail("")
      setScopes([])
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card request-card" onSubmit={submit}>
        <button type="button" className="back-link" onClick={onBack}>
          ← Voltar para o login
        </button>
        <div className="login-logo">S</div>
        <div className="login-kicker">SOLICITAÇÃO DE ACESSO</div>
        <h1>Peça seu acesso.</h1>
        <p>
          Informe seus dados e escolha o alcance desejado. A senha será criada
          somente depois da aprovação.
        </p>
        <label>
          Nome completo
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            autoComplete="name"
            required
          />
        </label>
        <label>
          E-mail
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />
        </label>
        <label>
          Módulo principal da matrícula
          <select
            value={requestedModule}
            onChange={(event) => setRequestedModule(event.target.value)}
          >
            {knowledgeModules.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          <small>
            A matrícula usará as duas primeiras letras do módulo + seis números
            sequenciais.
          </small>
        </label>
        <div className="scope-label">Módulo(s) solicitado(s)</div>
        <ScopePicker value={scopes} onChange={setScopes} />
        {error && <div className="login-error">{error}</div>}
        {message && <div className="login-success">{message}</div>}
        <button className="login-submit" disabled={busy || scopes.length === 0}>
          {busy ? "Enviando..." : "Enviar solicitação →"}
        </button>
        <small>
          Não informe senha agora. Depois da aprovação, use o código e token
          recebidos para criar sua senha e ativar o 2FA.
        </small>
      </form>
    </div>
  )
}

function FirstAccess({
  authFetch,
  onDone,
  onLogout,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
  onDone: () => void
  onLogout: () => void
}) {
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (newPassword !== confirmation) {
      setError("A confirmação não confere.")
      return
    }
    setBusy(true)
    setError("")
    try {
      const response = await authFetch("/api/auth/password", {
        method: "POST",
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      })
      const data = (await response.json()) as { detail?: string }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível alterar a senha")
      onDone()
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card" onSubmit={submit}>
        <div className="login-logo">S</div>
        <div className="login-kicker">PRIMEIRO ACESSO</div>
        <h1>Proteja sua conta.</h1>
        <p>Defina uma senha pessoal antes de acessar o workspace.</p>
        <label>
          Senha recebida no primeiro acesso
          <input
            type="password"
            value={currentPassword}
            onChange={(event) => setCurrentPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <label>
          Nova senha
          <input
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
          <small>Use maiúscula, minúscula, número e caractere especial.</small>
        </label>
        <label>
          Confirme a nova senha
          <input
            type="password"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            minLength={8}
            autoComplete="new-password"
            required
          />
        </label>
        {error && <div className="login-error">{error}</div>}
        <button className="login-submit" disabled={busy}>
          {busy ? "Salvando..." : "Salvar nova senha →"}
        </button>
        <button type="button" className="login-link" onClick={onLogout}>
          Sair
        </button>
      </form>
    </div>
  )
}

function ActivateAccount({ onBack }: { onBack: () => void }) {
  const [userCode, setUserCode] = useState("")
  const [activationToken, setActivationToken] = useState("")
  const [password, setPassword] = useState("")
  const [confirmation, setConfirmation] = useState("")
  const [code, setCode] = useState("")
  const [artifact, setArtifact] = useState<{
    qr_data_uri: string
    secret: string
    otpauth_uri: string
  } | null>(null)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const createPassword = async (event: FormEvent) => {
    event.preventDefault()
    if (password !== confirmation) {
      setError("A confirmação não confere.")
      return
    }
    setBusy(true)
    setError("")
    try {
      const response = await fetch(`${API}/api/auth/activation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          activation_token: activationToken,
          new_password: password,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        qr_data_uri?: string
        secret?: string
        otpauth_uri?: string
        message?: string
      }
      if (
        !response.ok ||
        !data.qr_data_uri ||
        !data.secret ||
        !data.otpauth_uri
      )
        throw new Error(data.detail ?? "Não foi possível ativar a conta")
      setArtifact({
        qr_data_uri: data.qr_data_uri,
        secret: data.secret,
        otpauth_uri: data.otpauth_uri,
      })
      setMessage(data.message ?? "Senha criada.")
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const enable = async () => {
    setBusy(true)
    setError("")
    try {
      const response = await fetch(`${API}/api/auth/activation/2fa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_code: userCode,
          activation_token: activationToken,
          code,
        }),
      })
      const data = (await response.json()) as {
        detail?: string
        message?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível ativar o 2FA")
      setMessage(data.message ?? "Conta ativada.")
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <form className="login-card request-card" onSubmit={createPassword}>
        {!artifact ? (
          <>
            <button type="button" className="back-link" onClick={onBack}>
              ← Voltar para o login
            </button>
            <div className="login-logo">S</div>
            <div className="login-kicker">ATIVAÇÃO DE CONTA</div>
            <h1>Finalize seu acesso.</h1>
            <p>
              Use a matrícula e o token enviados pela administração. Depois,
              crie sua senha pessoal.
            </p>
            <label>
              Matrícula gerada
              <input
                value={userCode}
                onChange={(event) =>
                  setUserCode(event.target.value.toUpperCase())
                }
                placeholder="Ex.: IN000001"
                pattern="[A-Z]{2}\d{6}"
                required
              />
            </label>
            <label>
              Token de ativação
              <input
                value={activationToken}
                onChange={(event) => setActivationToken(event.target.value)}
                autoComplete="one-time-code"
                required
              />
            </label>
            <label>
              Nova senha
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={8}
                autoComplete="new-password"
                required
              />
              <small>
                Use maiúscula, minúscula, número e caractere especial.
              </small>
            </label>
            <label>
              Confirme a nova senha
              <input
                type="password"
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
                minLength={8}
                autoComplete="new-password"
                required
              />
            </label>
            {error && <div className="login-error">{error}</div>}
            <button className="login-submit" disabled={busy}>
              {busy ? "Ativando..." : "Criar senha e continuar →"}
            </button>
          </>
        ) : (
          <>
            <div className="login-logo">S</div>
            <div className="login-kicker">2FA DA SOFIA</div>
            <h1>Escaneie o QR.</h1>
            <p>{message}</p>
            <img
              className="two-factor-qr"
              src={artifact.qr_data_uri}
              alt="QR Code para configurar o 2FA"
            />
            <b className="qr-caption">
              Se preferir, cadastre este segredo manualmente:
            </b>
            <code className="two-factor-secret">{artifact.secret}</code>
            <small className="two-factor-uri">{artifact.otpauth_uri}</small>
            <label>
              Código exibido no autenticador
              <input
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                required
              />
            </label>
            {error && <div className="login-error">{error}</div>}
            <button
              type="button"
              className="login-submit"
              disabled={busy || code.length !== 6}
              onClick={() => void enable()}
            >
              {busy ? "Validando..." : "Ativar 2FA e concluir →"}
            </button>
            {message.startsWith("Conta ativada") && (
              <button type="button" className="login-link" onClick={onBack}>
                Voltar para o login
              </button>
            )}
          </>
        )}
      </form>
    </div>
  )
}

function TwoFactorEnrollment({
  authFetch,
  onDone,
  onLogout,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
  onDone: () => void
  onLogout: () => void
}) {
  const [setup, setSetup] = useState<{
    qr_data_uri: string
    secret: string
    otpauth_uri: string
  } | null>(null)
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const prepare = async () => {
    setError("")
    try {
      const response = await authFetch("/api/auth/2fa/setup", {
        method: "POST",
      })
      const data = (await response.json()) as {
        detail?: string
        qr_data_uri?: string
        secret?: string
        otpauth_uri?: string
      }
      if (
        !response.ok ||
        !data.qr_data_uri ||
        !data.secret ||
        !data.otpauth_uri
      )
        throw new Error(data.detail ?? "Não foi possível preparar o 2FA")
      setSetup({
        qr_data_uri: data.qr_data_uri,
        secret: data.secret,
        otpauth_uri: data.otpauth_uri,
      })
    } catch (reason) {
      setError((reason as Error).message)
    }
  }
  const enable = async () => {
    setBusy(true)
    setError("")
    try {
      const response = await authFetch("/api/auth/2fa/enable", {
        method: "POST",
        body: JSON.stringify({ code }),
      })
      const data = (await response.json()) as { detail?: string }
      if (!response.ok) throw new Error(data.detail ?? "Código inválido")
      onDone()
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="login-screen">
      <div className="login-glow" />
      <div className="login-card request-card">
        <div className="login-logo">S</div>
        <div className="login-kicker">PROTEÇÃO OBRIGATÓRIA</div>
        <h1>Ative o 2FA.</h1>
        <p>
          Antes de acessar o workspace, adicione a conta SOFIA ao seu
          autenticador.
        </p>
        {!setup ? (
          <>
            <button className="login-submit" onClick={() => void prepare()}>
              Gerar QR Code →
            </button>
            <button className="login-link" onClick={onLogout}>
              Sair
            </button>
          </>
        ) : (
          <>
            <img
              className="two-factor-qr"
              src={setup.qr_data_uri}
              alt="QR Code para configurar o 2FA"
            />
            <b className="qr-caption">
              Escaneie o QR e informe o código gerado.
            </b>
            <code className="two-factor-secret">{setup.secret}</code>
            <small className="two-factor-uri">{setup.otpauth_uri}</small>
            <label>
              Código 2FA
              <input
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                required
              />
            </label>
            <button
              className="login-submit"
              disabled={busy || code.length !== 6}
              onClick={() => void enable()}
            >
              {busy ? "Validando..." : "Ativar 2FA →"}
            </button>
            <button className="login-link" onClick={onLogout}>
              Sair
            </button>
          </>
        )}
        {error && <div className="login-error">{error}</div>}
      </div>
    </div>
  )
}

function AccessControl({
  authFetch,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
}) {
  const [requests, setRequests] = useState<AccessRequest[]>([])
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const [setup, setSetup] = useState<{
    qr_data_uri: string
    secret: string
    otpauth_uri: string
    enabled: boolean
  } | null>(null)
  const [code, setCode] = useState("")
  const load = async () => {
    try {
      const response = await authFetch("/api/auth/requests?status=pending")
      const data = (await response.json()) as {
        requests: AccessRequest[]
        detail?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao carregar solicitações")
      setRequests(data.requests)
    } catch (reason) {
      setError((reason as Error).message)
    }
  }
  useEffect(() => {
    void load()
  }, [])
  const decide = async (
    item: AccessRequest,
    approve: boolean,
    scopes = item.requested_scopes,
  ) => {
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await authFetch(
        `/api/auth/requests/${item.id}/decision`,
        {
          method: "POST",
          body: JSON.stringify({
            approve,
            scopes: approve ? scopes : [],
            note: approve
              ? "Aprovado pela AG000001"
              : "Rejeitado pela AG000001",
          }),
        },
      )
      const data = (await response.json()) as {
        detail?: string
        user_code?: string
        activation_token?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao decidir solicitação")
      setMessage(
        approve
          ? `Acesso aprovado. Matrícula: ${data.user_code}. Token de ativação: ${data.activation_token}. Entregue o token ao usuário por um canal seguro.`
          : "Solicitação rejeitada.",
      )
      await load()
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const setup2FA = async () => {
    setError("")
    try {
      const response = await authFetch("/api/auth/2fa/setup", {
        method: "POST",
      })
      const data = (await response.json()) as {
        detail?: string
        qr_data_uri: string
        secret: string
        otpauth_uri: string
        enabled: boolean
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao preparar o 2FA")
      setSetup(data)
      setMessage(
        "Cadastre o QR no aplicativo autenticador e valide o código abaixo.",
      )
    } catch (reason) {
      setError((reason as Error).message)
    }
  }
  const enable2FA = async () => {
    try {
      const response = await authFetch("/api/auth/2fa/enable", {
        method: "POST",
        body: JSON.stringify({ code }),
      })
      const data = (await response.json()) as { detail?: string }
      if (!response.ok) throw new Error(data.detail ?? "Código inválido")
      setMessage("2FA ativado para AG000001.")
      setSetup(null)
      setCode("")
    } catch (reason) {
      setError((reason as Error).message)
    }
  }
  return (
    <div className="page-body narrow">
      <h1>
        Controle de <em>Acessos</em>
      </h1>
      <p className="page-subtitle">
        Somente a conta <b>AG000001</b> aprova solicitações e define o módulo
        permitido.
      </p>
      <section className="admin-security">
        <div>
          <h2>Proteção da conta administradora</h2>
          <p>
            O 2FA TOTP é compatível com Google Authenticator, Microsoft
            Authenticator e similares.
          </p>
        </div>
        <button className="neural-run" onClick={() => void setup2FA()}>
          Configurar 2FA
        </button>
        {setup && (
          <div className="two-factor-box">
            <b>Escaneie o QR Code</b>
            <img
              className="two-factor-qr small"
              src={setup.qr_data_uri}
              alt="QR Code para configurar o 2FA da AG000001"
            />
            <b>Segredo para cadastro manual</b>
            <code>{setup.secret}</code>
            <small>{setup.otpauth_uri}</small>
            <div className="two-factor-verify">
              <input
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                placeholder="Código de 6 dígitos"
              />
              <button
                className="neural-run"
                onClick={() => void enable2FA()}
                disabled={code.length !== 6}
              >
                Ativar 2FA
              </button>
            </div>
          </div>
        )}
      </section>
      {error && <div className="login-error">{error}</div>}
      {message && <div className="login-success">{message}</div>}
      <section className="access-list">
        <div className="access-list-heading">
          <h2>Solicitações pendentes</h2>
          <button className="login-link" onClick={() => void load()}>
            Atualizar
          </button>
        </div>
        {requests.length === 0 ? (
          <p>Nenhuma solicitação pendente.</p>
        ) : (
          requests.map((item) => (
            <article className="access-card" key={item.id}>
              <div>
                <b>{item.name}</b>
                <small>
                  {item.email} · {item.request_code}
                </small>
                <span>
                  Matrícula: automática · módulo principal:{" "}
                  {item.requested_module ??
                    "definido pelos módulos solicitados"}
                </span>
                <span>
                  Acesso solicitado:{" "}
                  {item.requested_scopes.includes("CORE")
                    ? "CORE (todos os módulos)"
                    : item.requested_scopes.join(", ")}
                </span>
              </div>
              <div className="access-actions">
                <button
                  className="neural-run"
                  disabled={busy}
                  onClick={() => void decide(item, true)}
                >
                  Aprovar
                </button>
                <button
                  className="neural-run danger"
                  disabled={busy}
                  onClick={() => void decide(item, false)}
                >
                  Rejeitar
                </button>
              </div>
            </article>
          ))
        )}
      </section>
    </div>
  )
}

function UserAdministration({
  authFetch,
}: {
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
}) {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [inactiveDays, setInactiveDays] = useState("90")
  const [resetArtifact, setResetArtifact] = useState<{
    user_code: string
    reset_token: string
    expires_at: number
  } | null>(null)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const load = async () => {
    try {
      const response = await authFetch("/api/auth/users")
      const data = (await response.json()) as {
        users: AdminUser[]
        inactivity: { inactive_lock_days: number }
        detail?: string
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao carregar usuários")
      setUsers(data.users)
      setInactiveDays(String(data.inactivity.inactive_lock_days))
    } catch (reason) {
      setError((reason as Error).message)
    }
  }
  useEffect(() => {
    void load()
  }, [])
  const resetPassword = async (user: AdminUser) => {
    setBusy(true)
    setError("")
    setMessage("")
    setResetArtifact(null)
    try {
      const response = await authFetch(
        `/api/auth/users/${user.user_code}/reset`,
        {
          method: "POST",
        },
      )
      const data = (await response.json()) as {
        detail?: string
        reset_token?: string
        expires_at?: number
        user_code?: string
        message?: string
      }
      if (
        !response.ok ||
        !data.reset_token ||
        !data.expires_at ||
        !data.user_code
      )
        throw new Error(
          data.detail ?? "Não foi possível criar o token de reset",
        )
      setResetArtifact({
        user_code: data.user_code,
        reset_token: data.reset_token,
        expires_at: data.expires_at,
      })
      setMessage(data.message ?? "Token de reset criado.")
      await load()
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const changeStatus = async (user: AdminUser) => {
    const active = !user.active
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await authFetch(
        `/api/auth/users/${user.user_code}/status`,
        {
          method: "POST",
          body: JSON.stringify({
            active,
            reason: active ? undefined : "Bloqueado pela AG000001",
          }),
        },
      )
      const data = (await response.json()) as { detail?: string }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível alterar o status")
      setMessage(
        active
          ? `${user.user_code} reativado.`
          : `${user.user_code} bloqueado.`,
      )
      await load()
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const savePolicy = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError("")
    setMessage("")
    try {
      const response = await authFetch("/api/auth/users/inactivity-policy", {
        method: "POST",
        body: JSON.stringify({ inactive_lock_days: Number(inactiveDays) }),
      })
      const data = (await response.json()) as {
        detail?: string
        blocked_now?: number
      }
      if (!response.ok)
        throw new Error(data.detail ?? "Não foi possível salvar a política")
      setMessage(
        `Política salva. Usuários bloqueados agora: ${data.blocked_now ?? 0}. A AG000001 é isenta.`,
      )
      await load()
    } catch (reason) {
      setError((reason as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const date = (value?: string | null) =>
    value ? new Date(value).toLocaleString("pt-BR") : "Nunca"
  const expiry = (value: number) =>
    new Date(value * 1000).toLocaleTimeString("pt-BR")
  return (
    <div className="page-body user-admin-page">
      <div className="admin-page-heading">
        <div>
          <h1>
            Administração de <em>usuários</em>
          </h1>
          <p className="page-subtitle">
            Status, sessões, tokens de recuperação e política de inatividade.
          </p>
        </div>
        <button
          className="neural-run"
          onClick={() => void load()}
          disabled={busy}
        >
          Atualizar
        </button>
      </div>
      <section className="admin-token-note">
        <b>Tokens de sessão</b>
        <span>
          O token de sessão é rotacionado automaticamente a cada 10 minutos. Por
          segurança, o painel exibe apenas o fingerprint; nunca expõe o token em
          texto puro. Para recuperação, gere um token descartável abaixo.
        </span>
      </section>
      <form className="admin-policy" onSubmit={savePolicy}>
        <div>
          <h2>Bloqueio por inatividade</h2>
          <small>
            Contas sem login ou atividade acima desse período serão bloqueadas
            automaticamente. A AG000001 não é bloqueada.
          </small>
        </div>
        <label>
          Dias
          <input
            type="number"
            min={1}
            max={3650}
            value={inactiveDays}
            onChange={(event) => setInactiveDays(event.target.value)}
          />
        </label>
        <button className="neural-run" disabled={busy}>
          Salvar política
        </button>
      </form>
      {error && <div className="login-error">{error}</div>}
      {message && <div className="login-success">{message}</div>}
      {resetArtifact && (
        <section className="reset-token-box">
          <b>Token de recuperação — {resetArtifact.user_code}</b>
          <code>{resetArtifact.reset_token}</code>
          <small>
            Entregue por canal seguro. Expira hoje às{" "}
            {expiry(resetArtifact.expires_at)}e não poderá ser exibido novamente
            após sair desta tela.
          </small>
          <button
            className="login-link"
            type="button"
            onClick={() =>
              void navigator.clipboard?.writeText(resetArtifact.reset_token)
            }
          >
            Copiar token
          </button>
        </section>
      )}
      <section className="user-list">
        <div className="access-list-heading">
          <h2>Contas cadastradas ({users.length})</h2>
          <small>Admin protegida: AG000001</small>
        </div>
        {users.map((user) => (
          <article className="user-admin-card" key={user.user_code}>
            <div className="user-admin-main">
              <div className="user-admin-title">
                <span
                  className={user.active ? "status-dot active" : "status-dot"}
                />
                <b>{user.user_code}</b>
                <span
                  className={user.active ? "status-pill active" : "status-pill"}
                >
                  {user.active ? "ativo" : "bloqueado"}
                </span>
                {user.role === "admin" && (
                  <span className="status-pill admin">admin</span>
                )}
              </div>
              <strong>{user.name}</strong>
              <small>{user.email}</small>
              <span>
                Módulos:{" "}
                {user.scopes.includes("CORE")
                  ? "CORE (todos)"
                  : user.scopes.join(", ")}
              </span>
              <span>
                Último login: {date(user.last_login_at)} · atividade:{" "}
                {date(user.last_seen_at)}
              </span>
              {!user.active && user.blocked_reason && (
                <span>Motivo: {user.blocked_reason}</span>
              )}
              <span>
                2FA: {user.two_factor_enabled ? "ativo" : "não configurado"} ·
                sessões ativas: {user.session_count}
              </span>
              {user.tokens.length > 0 && (
                <div className="session-list">
                  {user.tokens.map((token) => (
                    <small key={token.fingerprint}>
                      Sessão {token.fingerprint} · última rotação:{" "}
                      {date(token.last_rotated_at)} · expira:{" "}
                      {new Date(token.expires_at * 1000).toLocaleString(
                        "pt-BR",
                      )}
                    </small>
                  ))}
                </div>
              )}
            </div>
            <div className="user-admin-actions">
              <button
                className="neural-run"
                disabled={busy || !user.active}
                onClick={() => void resetPassword(user)}
              >
                Gerar reset · 10 min
              </button>
              {user.role !== "admin" && (
                <button
                  className="neural-run danger"
                  disabled={busy}
                  onClick={() => void changeStatus(user)}
                >
                  {user.active ? "Bloquear" : "Reativar"}
                </button>
              )}
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

function pageLabel(page: Page) {
  return ({
    dashboard: "Dashboard",
    chat: "Chat Sofia",
    modules: "Módulos RAG",
    upload: "Upload",
    neural: "Rede Neural",
    connections: "Conexões & Fluxos",
    pipeline: "Pipeline Explorer",
    access: "Controle de acessos",
  } as Record<Page, string>)[page]
}
function Dashboard({
  mod,
  online,
  authFetch,
  isAdmin,
}: {
  mod: Module
  online: boolean
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
  isAdmin: boolean
}) {
  const empty = mod.docs === "0"
  const types = Object.entries(mod.documentsByType ?? {})
  const imageCount = types
    .filter(([type]) =>
      ["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"].includes(type),
    )
    .reduce((total, [, count]) => total + count, 0)
  const typeSummary =
    types.length > 0
      ? types
          .map(([type, count]) => `${type.toUpperCase()} ${count}`)
          .join(" · ")
      : "Nenhum formato indexado"
  const storage =
    mod.linkStorage === "postgresql" ? "PostgreSQL" : "adaptador local"
  const stats = [
    ["Arquivos indexados", mod.docs, `knowledge/${mod.id}`],
    ["Links associados", String(mod.links ?? 0), storage],
    [
      "Imagens com OCR",
      String(imageCount),
      imageCount > 0 ? "texto extraído sob demanda" : "nenhuma imagem",
    ],
    ["Runtime", online ? "API online" : "API offline", "local + MCP"],
  ]
  const [analysisQuestion, setAnalysisQuestion] = useState("")
  const [analysis, setAnalysis] = useState("")
  const [analysisBusy, setAnalysisBusy] = useState(false)
  const [themeAnalytics, setThemeAnalytics] = useState<ThemeAnalytics | null>(null)
  const [analyticsBusy, setAnalyticsBusy] = useState(false)
  const [expansion, setExpansion] = useState<ExpansionStatus | null>(null)
  const [expansionBusy, setExpansionBusy] = useState(false)
  useEffect(() => {
    let disposed = false
    setAnalyticsBusy(true)
    void authFetch(`/api/analytics/themes?module_id=${encodeURIComponent(mod.id)}&days=30&limit=8`)
      .then(async (response) => {
        if (!response.ok) throw new Error("analytics unavailable")
        return (await response.json()) as ThemeAnalytics
      })
      .then((data) => {
        if (!disposed) setThemeAnalytics(data)
      })
      .catch(() => {
        if (!disposed) setThemeAnalytics(null)
      })
      .finally(() => {
        if (!disposed) setAnalyticsBusy(false)
      })
    return () => {
      disposed = true
    }
  }, [mod.id])
  useEffect(() => {
    if (!isAdmin) {
      setExpansion(null)
      return
    }
    let disposed = false
    void authFetch(`/api/admin/expansion?module_id=${encodeURIComponent(mod.id)}`)
      .then(async (response) => {
        if (!response.ok) throw new Error("expansion unavailable")
        return (await response.json()) as ExpansionStatus
      })
      .then((data) => {
        if (!disposed) setExpansion(data)
      })
      .catch(() => {
        if (!disposed) setExpansion(null)
      })
    return () => {
      disposed = true
    }
  }, [isAdmin, mod.id])
  const refreshExpansion = async () => {
    if (!isAdmin) return
    const response = await authFetch(
      `/api/admin/expansion?module_id=${encodeURIComponent(mod.id)}`,
    )
    if (response.ok) setExpansion((await response.json()) as ExpansionStatus)
  }
  const runExpansion = async () => {
    if (!isAdmin || expansionBusy) return
    setExpansionBusy(true)
    try {
      await authFetch("/api/admin/expansion/run", {
        method: "POST",
        body: JSON.stringify({ module_id: mod.id }),
      })
      await refreshExpansion()
    } finally {
      setExpansionBusy(false)
    }
  }
  const toggleExpansion = async () => {
    if (!isAdmin || !expansion) return
    setExpansionBusy(true)
    try {
      await authFetch("/api/admin/expansion/pause", {
        method: "POST",
        body: JSON.stringify({ paused: !expansion.settings?.paused }),
      })
      await refreshExpansion()
    } finally {
      setExpansionBusy(false)
    }
  }
  const runAnalysis = async () => {
    const question = analysisQuestion.trim()
    if (!question) {
      setAnalysis("Informe um tema que exista nos documentos deste módulo.")
      return
    }
    if (empty) {
      setAnalysis("Este módulo ainda não possui fontes locais para análise.")
      return
    }
    setAnalysisBusy(true)
    setAnalysis("Consultando evidências e calculando cenários...")
    try {
      const response = await authFetch("/api/tools/analyst_scenario", {
        method: "POST",
        body: JSON.stringify({
          arguments: {
            module_id: mod.id,
            provider: "ollama",
            question,
            baseline: 100,
            volatility: 0.1,
            samples: 3000,
          },
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? "Falha na análise")
      setAnalysis(
        `${data.analysis} Fontes: ${data.sources?.join(", ") || "nenhuma"}.`,
      )
    } catch (error) {
      setAnalysis(`Falha: ${(error as Error).message}`)
    } finally {
      setAnalysisBusy(false)
    }
  }
  const themeRows = themeAnalytics?.top_themes ?? []
  const maxThemeConsultations = Math.max(
    1,
    ...themeRows.map((item) => item.consultations),
  )
  const rowFeedbackTotals = themeRows.reduce(
    (totals, item) => ({
      good: totals.good + item.good_answers,
      medium: totals.medium + item.medium_answers,
      bad: totals.bad + item.bad_answers,
      evaluated: totals.evaluated + item.good_answers + item.bad_answers,
      needsImprovement: totals.needsImprovement || item.needs_improvement,
    }),
    { good: 0, medium: 0, bad: 0, evaluated: 0, needsImprovement: false },
  )
  const feedbackSummary = themeAnalytics?.feedback_summary
  const feedbackTotals = {
    good: feedbackSummary?.good_answers ?? rowFeedbackTotals.good,
    medium: feedbackSummary?.medium_answers ?? rowFeedbackTotals.medium,
    bad: feedbackSummary?.bad_answers ?? rowFeedbackTotals.bad,
    evaluated: feedbackSummary?.evaluated_answers ?? rowFeedbackTotals.evaluated,
    quality:
      feedbackSummary?.quality_score ??
      (rowFeedbackTotals.evaluated
        ? rowFeedbackTotals.good / rowFeedbackTotals.evaluated
        : null),
    needsImprovement:
      feedbackSummary?.needs_improvement ?? rowFeedbackTotals.needsImprovement,
  }
  return (
    <div className="dashboard">
      <section className="welcome">
        <h1>
          Visão do gestor · <em>{mod.name}</em>
        </h1>
        <p>{mod.focus}</p>
        <div className="chips">
          <span>{mod.manager}</span>
          <span>{mod.docs} arquivos reais</span>
          <span>{empty ? "Aguardando fontes" : "RAG ativo"}</span>
        </div>
      </section>
      <div className="stats">
        {stats.map(([label, value, change], index) => (
          <div className="stat" key={label}>
            <div className="stat-top">
              <small>{label}</small>
              <i>{["▯", "↗", "▧", "◉"][index]}</i>
            </div>
            <strong>{value}</strong>
            <span>{change}</span>
          </div>
        ))}
      </div>
      {isAdmin && expansion && (
        <section className="expansion-card" aria-label="Expansão contínua do conhecimento">
          <div className="expansion-card-heading">
            <div>
              <h3>Expansão contínua</h3>
              <small>Fila persistente · fontes aprovadas · conhecimento offline</small>
            </div>
            <span className={expansion.settings?.paused ? "expansion-state paused" : "expansion-state"}>
              {expansion.settings?.paused ? "pausada" : "ativa"}
            </span>
          </div>
          <div className="expansion-metrics">
            <span><b>{expansion.queue_pending}</b><small>na fila</small></span>
            <span><b>{expansion.documents_by_status?.READY ?? 0}</b><small>documentos prontos</small></span>
            <span><b>{expansion.sources_by_status?.READY ?? 0}</b><small>fontes registradas</small></span>
            <span><b>{expansion.processing_errors}</b><small>erros isolados</small></span>
          </div>
          <div className="expansion-card-footer">
            <small>
              {expansion.last_cycle?.finished_at
                ? `Último ciclo: ${new Date(expansion.last_cycle.finished_at).toLocaleString("pt-BR")}`
                : "Nenhum ciclo executado ainda"}
            </small>
            <div>
              <button type="button" className="neural-run secondary" onClick={() => void toggleExpansion()} disabled={expansionBusy}>
                {expansion.settings?.paused ? "Retomar" : "Pausar"}
              </button>
              <button type="button" className="neural-run" onClick={() => void runExpansion()} disabled={expansionBusy || Boolean(expansion.settings?.paused)}>
                {expansionBusy ? "Executando..." : "Executar ciclo"}
              </button>
            </div>
          </div>
        </section>
      )}
      <div className="dashboard-grid">
        <section className="chart-card manager-card">
          <h3>Prioridades do gestor</h3>
          <small>{mod.category} · decisão baseada em fontes locais</small>
          <div className="manager-list">
            <div>
              <i>01</i>
              <span>
                <b>Cobertura</b>
                <small>
                  {empty
                    ? "Adicionar documentos, imagens ou links do domínio."
                    : `Cruzar ${mod.docs} arquivos com as perguntas do módulo.`}
                </small>
              </span>
            </div>
            <div>
              <i>02</i>
              <span>
                <b>Análise</b>
                <small>
                  {empty
                    ? "Aguardando dados para encontrar padrões."
                    : "Usar RAG, rede neural e Monte Carlo para comparar cenários."}
                </small>
              </span>
            </div>
            <div>
              <i>03</i>
              <span>
                <b>Próxima ação</b>
                <small>
                  {empty
                    ? "Abra Upload para alimentar este gestor."
                    : "Revisar fontes e treinar novamente após novas inclusões."}
                </small>
              </span>
            </div>
          </div>
        </section>
        <section className="recent">
          <h3>Fontes ativas</h3>
          <div className="source-box">
            <b>knowledge/{mod.id}</b>
            <small>{typeSummary}</small>
            <small>
              {mod.links ?? 0} links associados · armazenamento: {storage}
            </small>
            <small>OCR de imagens: disponível no backend</small>
          </div>
        </section>
      </div>
      <section className="theme-card">
        <div className="theme-card-heading">
          <div className="theme-card-title">
            <span className="theme-card-icon" aria-hidden="true">
              ◌
            </span>
            <div>
              <h3>Temas consultados</h3>
              <small>
                Últimos {themeAnalytics?.period_days ?? 30} dias · registro
                analítico do banco
              </small>
            </div>
          </div>
          <div className="theme-total" aria-label="Total de consultas no período">
            <strong>{themeAnalytics?.total_queries ?? 0}</strong>
            <span>consultas</span>
          </div>
        </div>
        {themeRows.length > 0 && (
          <div className="theme-feedback-summary" aria-label="Qualidade das respostas">
            <div className="theme-feedback-heading">
              <span className="theme-feedback-label">Qualidade percebida</span>
              <small>
                {feedbackTotals.quality === null
                  ? "sem avaliações explícitas"
                  : `${Math.round(feedbackTotals.quality * 100)}% nas avaliações`}
              </small>
            </div>
            <div className="theme-feedback-chips">
              <span className="feedback-good">
                <i aria-hidden="true" /> {feedbackTotals.good} úteis
              </span>
              <span className="feedback-medium">
                <i aria-hidden="true" /> {feedbackTotals.medium} sem opinião
              </span>
              <span className="feedback-bad">
                <i aria-hidden="true" /> {feedbackTotals.bad} para revisar
              </span>
              {feedbackTotals.needsImprovement && (
                <span className="feedback-training">
                  ↗ melhoria recomendada
                </span>
              )}
            </div>
          </div>
        )}
        {analyticsBusy ? (
          <p className="theme-empty">Atualizando consultas reais...</p>
        ) : themeRows.length ? (
          <div className="theme-list">
            {themeRows.map((item, index) => (
              <div className="theme-row" key={`${item.module_id}-${item.theme}`}>
                <div className="theme-row-label">
                  <div className="theme-row-title">
                    <span className="theme-rank">{String(index + 1).padStart(2, "0")}</span>
                    <div>
                      <b>{item.theme}</b>
                      {item.intent && <small>{item.intent}</small>}
                    </div>
                  </div>
                  <div className="theme-row-count">
                    <strong>{item.consultations}</strong>
                    <span>{item.consultations === 1 ? "consulta" : "consultas"}</span>
                  </div>
                </div>
                <div className="theme-meter" aria-hidden="true">
                  <i style={{ width: `${(item.consultations / maxThemeConsultations) * 100}%` }} />
                </div>
                <div className="theme-row-meta">
                  <span>{item.source_uses} fontes usadas</span>
                  <span>{item.verified_consultations} verificadas</span>
                  <span className="theme-quality">
                    {item.quality_score === null
                      ? "sem avaliação"
                      : `${Math.round(item.quality_score * 100)}% avaliada`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="theme-empty">Ainda não há consultas registradas para este módulo.</p>
        )}
        {!!themeAnalytics?.by_user?.length && (
          <div className="analytics-users">
            <div className="analytics-users-heading">
              <b>Consultas por usuário</b>
              <small>no período selecionado</small>
            </div>
            <div className="analytics-user-list">
              {themeAnalytics.by_user.slice(0, 5).map((item) => (
                <span key={item.user_code}>
                  <b>{item.user_code}</b>
                  <em>{item.consultations} consulta{item.consultations === 1 ? "" : "s"}</em>
                </span>
              ))}
            </div>
          </div>
        )}
        <small className="analytics-note">
          Visível somente para AG000001. São guardados módulo, usuário, tema, horário, fontes, motor e feedback; perguntas, respostas e conteúdo clínico não são armazenados.
        </small>
      </section>
      <section className="analyst-panel">
        <div>
          <h3>Analista de cenários</h3>
          <small>RAG + LLM + rede neural + aleatoriedade + Monte Carlo</small>
        </div>
        <div className="analyst-controls">
          <input
            value={analysisQuestion}
            onChange={(event) => setAnalysisQuestion(event.target.value)}
            placeholder={`Tema documentado em ${mod.name}...`}
            disabled={analysisBusy}
          />
          <button
            className="neural-run"
            onClick={() => void runAnalysis()}
            disabled={analysisBusy || empty}
          >
            {analysisBusy ? "Analisando..." : "Avaliar cenário →"}
          </button>
        </div>
        {analysis && <div className="analysis-result">{analysis}</div>}
        <small className="mcp-note">
          A análise é apoio à decisão e só interpreta evidências recuperadas do
          módulo; não é previsão, diagnóstico ou autorização automática.
        </small>
      </section>
    </div>
  )
}
function Modules({
  items,
  selected,
  selectModule,
}: {
  items: Module[]
  selected: string
  selectModule: (id: string) => void
}) {
  return (
    <div className="page-body">
      <h1>
        Módulos <em>RAG</em>
      </h1>
      <p className="page-subtitle">
        Domínios carregados diretamente da pasta knowledge.
      </p>
      <div className="rag-grid">
        {items.map((item) => (
          <button
            key={item.id}
            className={item.id === selected ? "rag-card active" : "rag-card"}
            onClick={() => selectModule(item.id)}
            style={{ "--module-color": item.color } as React.CSSProperties}
          >
            <div className="rag-icon">{item.icon}</div>
            <h3>{item.name}</h3>
            <small>{item.category}</small>
            <p>{item.docs} documentos indexados</p>
            <footer>
              <span>knowledge/{item.id}</span>
              <b>{item.docs}</b>
            </footer>
          </button>
        ))}
      </div>
    </div>
  )
}
function Connections({
  items,
  capabilities,
}: {
  items: Module[]
  capabilities: Capabilities | null
}) {
  const providerState = capabilities?.providers ?? {
    auto: true,
    ollama: false,
    openai: false,
    gemini: false,
    claude: false,
  }
  const privacy = capabilities?.privacy
  const tasy = capabilities?.integrations?.connectors?.tasy
  const agents = capabilities?.agents
  const cards = [
    {
      name: "MCP local",
      detail: capabilities?.mcp?.transport_http ?? "/mcp",
      active: Boolean(capabilities?.mcp?.transport_stdio),
    },
    {
      name: "Knowledge",
      detail: `${items.length} módulos ativos · fontes físicas`,
      active: items.length > 0,
    },
    {
      name: "OCR",
      detail: capabilities?.ocr?.available
        ? `${capabilities.ocr.engine} · ${capabilities.ocr.language}`
        : "Configure o Tesseract",
      active: Boolean(capabilities?.ocr?.available),
    },
    {
      name: "PostgreSQL",
      detail: capabilities?.links?.postgres_configured
        ? "Links e metadados configurados"
        : "Fallback local em data/links.json",
      active: Boolean(capabilities?.links?.postgres_configured),
    },
    {
      name: "FHIR",
      detail: "R4 · acesso autenticado · escrita autorizada",
      active: true,
    },
    {
      name: "Providers",
      detail: `Automático ${
        providerState.auto ? "ativo" : "indisponível"
      } · OpenAI ${capabilities?.models?.openai ?? "gpt-5.5"} ${
        providerState.openai ? "liberado" : "local/bloqueado"
      } · Ollama ${capabilities?.models?.ollama ?? "modelo configurado"} ${
        providerState.ollama ? "ativo" : "indisponível"
      } · Gemini ${
        providerState.gemini ? "liberado" : "local/bloqueado"
      } · Claude ${providerState.claude ? "liberado" : "local/bloqueado"} · store=${capabilities?.openai_store_responses ? "true" : "false"}`,
      active: Boolean(providerState.ollama),
    },
    {
      name: "Agentes / CORE",
      detail: agents
        ? `Planner, critic e memória ${
            agents.memory ? "ativos" : "indisponíveis"
          } · execução ${agents.execution}`
        : "carregando agentes",
      active: Boolean(agents?.core && agents?.planner && agents?.critic),
    },
    {
      name: "Treinamento modular",
      detail: capabilities?.training
        ? capabilities.training.active_modules.length > 0
          ? `Em andamento: ${capabilities.training.active_modules.join(", ")} · fila ${capabilities.training.queued_modules.length}`
          : `Fila ${capabilities.training.queued_modules.length} · um módulo por vez`
        : "carregando fila de treinamento",
      active: Boolean(capabilities?.training?.sequential),
    },
    {
      name: "Integrações",
      detail: tasy?.configured
        ? `TASY pronto · ${capabilities?.integrations?.jobs?.total ?? 0} jobs · DLQ ${capabilities?.integrations?.dlq_pending ?? 0}`
        : "TASY não configurado · sem dados fictícios",
      active: Boolean(tasy?.configured),
    },
    {
      name: "LGPD / privacidade",
      detail: privacy
        ? `${privacy.mode} · auditoria ${
            privacy.audit_log ? "ativa" : "indisponível"
          } · FHIR externo bloqueado`
        : "carregando controles locais",
      active: Boolean(privacy?.audit_log),
    },
  ]
  return (
    <div className="page-body">
      <h1>
        Conexões <em>& Fluxos</em>
      </h1>
      <p className="page-subtitle">
        Veja o que está ativo e o que cada configuração altera no resultado.
      </p>
      <div className="connector-grid">
        {cards.map((card) => (
          <article className="connector-card" key={card.name}>
            <span
              className={card.active ? "connector-dot active" : "connector-dot"}
            />
            <div>
              <h3>{card.name}</h3>
              <p>{card.detail}</p>
            </div>
            <b>{card.active ? "online" : "configurar"}</b>
          </article>
        ))}
      </div>
      <section className="flow-card">
        <h3>Fluxo analítico</h3>
        <div className="flow-strip">
          <span>Fontes reais</span>
          <i>→</i>
          <span>OCR / ingestão</span>
          <i>→</i>
          <span>RAG + MCP</span>
          <i>→</i>
          <span>Neural + Monte Carlo</span>
          <i>→</i>
          <span>Dashboard</span>
        </div>
        <small>
          Upload ou link novo entra no módulo, vira evidência offline, sinaliza
          a rede neural e pode ser analisado pelo gestor.
        </small>
      </section>
      <section className="parameters-card">
        <h3>Parametrização, em linguagem simples</h3>
        <div className="parameter-grid">
          <div>
            <b>Resposta</b>
            <span>
              Resumo direto reduz linhas e tempo; detalhada amplia a explicação.
            </span>
          </div>
          <div>
            <b>Pesquisa densa</b>
            <span>
              Segue até 10 páginas reais do domínio e salva o resultado offline.
            </span>
          </div>
          <div>
            <b>Provider</b>
            <span>
              Troca o motor de geração. Não troca o módulo nem libera
              conhecimento fora do RAG.
            </span>
          </div>
          <div>
            <b>Treinamento</b>
            <span>
              Novas fontes atualizam a assinatura e agendam o treino isolado
              daquele módulo.
            </span>
          </div>
          <div>
            <b>LGPD</b>
            <span>
              Ollama é local; Gemini/Claude exigem liberação explícita. Logs
              guardam metadados, não conteúdo.
            </span>
          </div>
          <div>
            <b>Semântica</b>
            <span>
              Conecta conceitos que aparecem nos mesmos chunks e os documentos
              que os comprovam.
            </span>
          </div>
          <div>
            <b>Integrações</b>
            <span>
              TASY lê páginas, grava o RAW local, retoma pelo checkpoint e envia
              falhas para a DLQ; nenhum registro fictício é criado.
            </span>
          </div>
        </div>
      </section>
    </div>
  )
}
function Upload({
  mod,
  authFetch,
  onUploaded,
}: {
  mod: Module
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
  onUploaded: () => void
}) {
  const [status, setStatus] = useState("")
  const [dragging, setDragging] = useState(false)
  const [url, setUrl] = useState("")
  const [deep, setDeep] = useState(true)
  const [links, setLinks] = useState<Array<{
    title?: string
    pages?: number
    file_name?: string
    offline_path?: string
    storage?: string
  }>>([])
  const loadLinks = async () => {
    try {
      const response = await authFetch(`/api/modules/${mod.id}/links`)
      if (response.ok) {
        const data = (await response.json()) as {
          links: Array<{
            title?: string
            pages?: number
            file_name?: string
            offline_path?: string
            storage?: string
          }>
        }
        setLinks(data.links)
      }
    } catch {
      setLinks([])
    }
  }
  useEffect(() => {
    void loadLinks()
  }, [mod.id])
  const uploadFile = async (file?: File) => {
    if (!file) return
    setStatus("Enviando e salvando no módulo...")
    const form = new FormData()
    form.append("file", file)
    try {
      const response = await authFetch(`/api/modules/${mod.id}/upload`, {
        method: "POST",
        body: form,
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? "Falha no upload")
      const destination = data.ocr
        ? `knowledge/${mod.id}/imagens · OCR ${
            data.ocr.available ? "disponível" : "indisponível"
          }`
        : `knowledge/${mod.id}/textos`
      setStatus(
        `${data.file} salvo em ${destination} · treinamento automático agendado`,
      )
      onUploaded()
    } catch (error) {
      setStatus(`Falha: ${(error as Error).message}`)
    }
  }
  const submitLink = async (event: FormEvent) => {
    event.preventDefault()
    if (!url.trim()) return
    setStatus(
      `Lendo o link${
        deep ? " e até 10 páginas relacionadas do mesmo domínio" : ""
      }...`,
    )
    try {
      const response = await authFetch(`/api/modules/${mod.id}/links`, {
        method: "POST",
        body: JSON.stringify({ url, max_pages: deep ? 10 : 1, dense: deep }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? "Falha ao ingerir link")
      setStatus(
        `Documento offline salvo: ${data.link.title} · ${data.link.pages} página(s) reais · ${
          data.link.storage === "postgresql" ? "PostgreSQL" : "adaptador local"
        } · treinamento agendado`,
      )
      setUrl("")
      await loadLinks()
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
  return (
    <div className="page-body narrow">
      <h1>
        Upload de <em>Fontes</em>
      </h1>
      <p className="page-subtitle">
        Tudo é associado ao gestor ativo:{" "}
        <b style={{ color: mod.color }}>knowledge/{mod.id}</b>. A fonte entra no
        RAG e pode atualizar a rede neural.
      </p>
      <section className="ingest-card">
        <h2>Arquivos e imagens</h2>
        <p>
          Imagens entram no módulo e passam por OCR no treinamento e na busca.
        </p>
        <label
          className={dragging ? "drop-zone is-dragging" : "drop-zone"}
          onDragEnter={() => setDragging(true)}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={() => setDragging(false)}
          onDrop={drop}
        >
          ⇧<strong>Arraste arquivos aqui ou clique para selecionar</strong>
          <small>
            PDF · DOCX · TXT · MD · CSV · JSON · XML · YAML · LOG · XLSX · PNG ·
            JPG · WEBP · TIFF · BMP — máx. 50 MB
          </small>
          <input
            type="file"
            hidden
            accept=".pdf,.docx,.txt,.md,.csv,.json,.xml,.yaml,.yml,.log,.xlsx,.png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff"
            onChange={(event) => void uploadFile(event.target.files?.[0])}
          />
        </label>
      </section>
      <section className="ingest-card">
        <h2>Links viram documentos offline</h2>
        <p>
          O conteúdo é capturado em <b>knowledge/{mod.id}/links</b>, entra no
          RAG e é registrado no PostgreSQL quando configurado.
        </p>
        <form className="link-form" onSubmit={submitLink}>
          <input
            type="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://dominio.com/documentacao"
            required
          />
          <label className="check-row">
            <input
              type="checkbox"
              checked={deep}
              onChange={(event) => setDeep(event.target.checked)}
            />{" "}
            Pesquisa densa: seguir até 10 páginas reais do mesmo domínio
          </label>
          <button className="neural-run" type="submit">
            Salvar documento offline →
          </button>
        </form>
        {links.length > 0 && (
          <div className="offline-list">
            <strong>Documentos offline deste módulo</strong>
            {links.map((link, index) => (
              <div key={`${link.file_name}-${index}`}>
                <span>{link.title ?? "Link capturado"}</span>
                <small>
                  {link.pages ?? 1} página(s) ·{" "}
                  {link.storage === "postgresql"
                    ? "PostgreSQL + arquivo local"
                    : "arquivo local"}{" "}
                  ·{" "}
                  {link.offline_path ??
                    `knowledge/${mod.id}/links/${link.file_name ?? ""}`}
                </small>
              </div>
            ))}
          </div>
        )}
      </section>
      {status && (
        <div className="upload-status" role="status">
          {status}
        </div>
      )}
    </div>
  )
}
type GraphNode = {
  id: string
  label: string
  kind: "document" | "concept"
  x: number
  y: number
  frequency: number
  documents?: number
}
type GraphEdge = {
  source: string
  target: string
  weight: number
  kind: "evidence" | "semantic"
}
type NeuralGraph = {
  trained: boolean
  architecture: number[]
  training: {
    samples?: number
    epochs?: number
    mse?: number
    trained_at?: string
    stale?: boolean
  }
  features: string[]
  nodes: GraphNode[]
  edges: GraphEdge[]
  concept_count: number
  document_count: number
  weights?: { w1?: number[][]; w2?: number[][] }
  meaning: string
}
function SemanticNetwork({
  graph,
  color,
}: {
  graph: NeuralGraph | null
  color: string
}) {
  if (!graph)
    return (
      <div className="network-empty">
        Carregando relações semânticas da base...
      </div>
    )
  const nodeMap = new Map(graph.nodes.map((node) => [node.id, node]))
  const architecture = graph.architecture ?? [3, 4, 3]
  const w1 = graph.weights?.w1 ?? []
  const w2 = graph.weights?.w2 ?? []
  const layers = [
    architecture[0] ?? 3,
    architecture[1] ?? 4,
    architecture[2] ?? 3,
  ]
  const yPosition = (count: number, index: number) =>
    20 + (60 * index) / Math.max(1, count - 1)
  return (
    <div className="semantic-network">
      <div className="network-section-title">
        <b>Grafo semântico adaptativo</b>
        <small>
          {graph.document_count} documentos · {graph.concept_count} conceitos ·
          conexões derivadas dos chunks
        </small>
      </div>
      <svg
        className="semantic-graph"
        viewBox="0 0 100 100"
        role="img"
        aria-label="Relações entre documentos e conceitos encontrados"
      >
        <g className="semantic-edges">
          {graph.edges.map((edge, index) => {
            const source = nodeMap.get(edge.source)
            const target = nodeMap.get(edge.target)
            return source && target ? (
              <line
                key={`${edge.source}-${edge.target}-${index}`}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                className={
                  edge.kind === "semantic" ? "semantic-edge" : "evidence-edge"
                }
                style={{
                  strokeWidth: 0.5 + edge.weight * 2,
                  opacity: 0.22 + edge.weight * 0.72,
                }}
              />
            ) : null
          })}
        </g>
        <g className="semantic-nodes">
          {graph.nodes.map((node) => (
            <g key={node.id} transform={`translate(${node.x},${node.y})`}>
              <circle
                r={
                  node.kind === "concept"
                    ? Math.min(3.8, 2.1 + node.frequency / 12)
                    : 2.2
                }
                style={{
                  fill: node.kind === "concept" ? color : "var(--surface-2)",
                  stroke: color,
                }}
              />
              <text
                x={node.kind === "concept" ? 4.5 : -4.5}
                y="1"
                textAnchor={node.kind === "concept" ? "start" : "end"}
              >
                {node.label}
              </text>
            </g>
          ))}
        </g>
      </svg>
      <div className="network-legend">
        <span>
          <i className="legend-document" /> documento
        </span>
        <span>
          <i style={{ background: color }} /> conceito
        </span>
        <span>
          <i className="legend-semantic" /> coocorrência semântica
        </span>
      </div>
      <small className="network-meaning">{graph.meaning}</small>
      <div className="network-section-title architecture-title">
        <b>Arquitetura treinada</b>
        <small>
          pesos reais do autoencoder · entrada → camada oculta → reconstrução
        </small>
      </div>
      <svg
        className="architecture-graph"
        viewBox="0 0 100 100"
        aria-hidden="true"
      >
        {layers
          .slice(0, 2)
          .flatMap((count, layer) =>
            Array.from({ length: count }, (_, from) =>
              Array.from({ length: layers[layer + 1] }, (_, to) => {
                const matrix = layer === 0 ? w1 : w2
                const weight = Number(matrix[from]?.[to] ?? 0)
                return (
                  <line
                    key={`weight-${layer}-${from}-${to}`}
                    x1={layer === 0 ? 18 : 50}
                    y1={yPosition(count, from)}
                    x2={layer === 0 ? 50 : 82}
                    y2={yPosition(layers[layer + 1], to)}
                    style={{
                      stroke: color,
                      strokeWidth: Math.min(1.7, 0.35 + Math.abs(weight) * 1.8),
                      opacity: graph.trained
                        ? Math.min(0.9, 0.18 + Math.abs(weight))
                        : 0.12,
                    }}
                  />
                )
              }),
            ),
          )
          .flat()}
        {layers.map((count, layer) =>
          Array.from({ length: count }, (_, node) => (
            <circle
              key={`layer-node-${layer}-${node}`}
              cx={layer === 0 ? 18 : layer === 1 ? 50 : 82}
              cy={yPosition(count, node)}
              r="2.3"
              style={{ fill: color, opacity: graph.trained ? 1 : 0.45 }}
            />
          )),
        )}
      </svg>
      <div className="layer-labels">
        <span>ENTRADA · {layers[0]}</span>
        <span>OCULTA · {layers[1]}</span>
        <span>SAÍDA · {layers[2]}</span>
      </div>
    </div>
  )
}
function Neural({
  mod,
  authFetch,
}: {
  mod: Module
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
}) {
  const [graph, setGraph] = useState<NeuralGraph | null>(null)
  const [result, setResult] = useState("")
  const [busy, setBusy] = useState(false)
  const [values, setValues] = useState(["0.2", "0.7", "0.4"])
  const load = async () => {
    try {
      const response = await authFetch("/api/tools/neural_graph", {
        method: "POST",
        body: JSON.stringify({ arguments: { module_id: mod.id } }),
      })
      const data = await response.json()
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao consultar o modelo")
      setGraph(data)
    } catch (error) {
      setResult((error as Error).message)
    }
  }
  useEffect(() => {
    void load()
  }, [mod.id])
  const train = async () => {
    setBusy(true)
    setResult("Treinando com os documentos deste módulo...")
    try {
      const response = await authFetch("/api/tools/neural_train", {
        method: "POST",
        body: JSON.stringify({
          arguments: { module_id: mod.id, epochs: 160, learning_rate: 0.08 },
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? "Falha no treinamento")
      await load()
      setResult(
        `Modelo adaptado com ${data.samples} chunks · MSE ${data.mse} · grafo semântico atualizado`,
      )
    } catch (error) {
      setResult((error as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const run = async () => {
    setBusy(true)
    setResult("Executando inferência no modelo treinado...")
    try {
      const response = await authFetch("/api/tools/neural_infer", {
        method: "POST",
        body: JSON.stringify({
          arguments: { module_id: mod.id, values: values.map(Number) },
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? "Falha na inferência")
      setResult(
        `reconstrução: [${data.reconstruction.join(", ")}] · erro: ${data.reconstruction_error}`,
      )
    } catch (error) {
      setResult((error as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const model = graph?.training
  return (
    <div className="page-body">
      <h1>
        Rede Neural <em>S.O.F.I.A.</em>
      </h1>
      <p className="page-subtitle">
        A rede é treinada com chunks reais de{" "}
        <b style={{ color: mod.color }}>knowledge/{mod.id}</b> e conecta cada
        conceito aos documentos que o sustentam.
      </p>
      <div className="neural-card">
        <SemanticNetwork graph={graph} color={mod.color} />
        <div className="neural-status">
          {graph?.trained
            ? `${
                model?.stale ? "Pendente · fonte nova detectada" : "Atualizada"
              } · ${model?.samples} chunks · ${model?.epochs} épocas · MSE ${model?.mse}`
            : "Não treinada · aguardando documentos e treinamento automático"}
        </div>
        <div className="neural-actions">
          <button className="neural-run" disabled={busy} onClick={train}>
            {busy ? "Processando..." : "Treinar com knowledge →"}
          </button>
          <div className="neural-inputs">
            {values.map((value, index) => (
              <input
                key={index}
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={value}
                onChange={(event) =>
                  setValues((current) =>
                    current.map((item, itemIndex) =>
                      itemIndex === index ? event.target.value : item,
                    ),
                  )
                }
                aria-label={`Feature ${index + 1}`}
              />
            ))}
          </div>
          <button
            className="neural-run secondary"
            disabled={busy || !graph?.trained}
            onClick={run}
          >
            Executar inferência →
          </button>
        </div>
        {result && <div className="upload-status">{result}</div>}
        <small className="mcp-note">
          MCP: neural_graph · neural_status · neural_train · neural_infer. As
          arestas semânticas são coocorrências nos mesmos chunks; não são
          relações inventadas pelo modelo.
        </small>
      </div>
    </div>
  )
}

export default App
