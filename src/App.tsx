import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
} from "react"
import { knowledgeModules, type KnowledgeModule } from "./knowledge"
import PipelineExplorer from "./features/pipeline/PipelineExplorer"
import ChatView from "./features/chat/Chat"
import {
  AccessControl,
  ActivateAccount,
  FirstAccess,
  Login,
  TwoFactorEnrollment,
  RequestAccess,
  ResetPassword,
  UserAdministration,
} from "./features/authentication/AuthScreens"
import KnowledgeUpload from "./features/knowledge/Upload"
import NeuralView from "./features/neural/Neural"
import {
  Connections,
  Dashboard,
  Modules,
} from "./features/workspace/WorkspaceViews"
import { type AccessRequest, type AdminUser, type AuthUser } from "./types/auth"
import type { ExpansionStatus, ThemeAnalytics, WorkspaceCapabilities } from "./types/workspace"
import AppShell from "./layouts/AppShell"
import {
  apiRequest,
  describeApiError,
  SofiaApiError,
} from "./services/api-client"

type Page = "dashboard" | "chat" | "modules" | "upload" | "neural" | "connections" | "pipeline" | "access"
type Provider = "auto" | "openai" | "gemini" | "claude" | "ollama"
type Language = "pt-BR" | "en" | "es"
type Module = KnowledgeModule
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
  error?: boolean
  agent_trace?: Array<{
    id: string
    stage: string
    status: string
    agent: string
    detail?: string
  }>
}
type SendOptions = {
  retry?: boolean
  retryOf?: number
  retryAttempt?: number
  silentUser?: boolean
}

const MAX_RETRY_ATTEMPTS = 3
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
  const [responseStyle, setResponseStyle] =
    useState<ResponseStyle>("structured")
  const [patientId, setPatientId] = useState("")
  const [message, setMessage] = useState("")
  const [attachment, setAttachment] = useState<File | null>(null)
  const [chat, setChat] = useState<ChatItem[]>([])
  const [chatBusy, setChatBusy] = useState(false)
  const [apiOnline, setApiOnline] = useState(false)
  const [capabilities, setCapabilities] = useState<WorkspaceCapabilities | null>(null)
  const feedbackInFlight = useRef(new Set<number>())
  const refreshInFlight = useRef(false)
  const mod = useMemo(
    () => items.find((item) => item.id === moduleId) ?? items[0],
    [items, moduleId],
  )

  const authFetch = (path: string, init: RequestInit = {}) =>
    apiRequest(path, init, { token })
  const refresh = async () => {
    if (!token || refreshInFlight.current) return
    refreshInFlight.current = true
    try {
      const [response, capabilityResponse] = await Promise.all([
        authFetch("/api/modules"),
        authFetch("/api/capabilities"),
      ])
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
      if (capabilityResponse.ok)
        setCapabilities((await capabilityResponse.json()) as WorkspaceCapabilities)
      setApiOnline(true)
    } catch {
      setApiOnline(false)
    } finally {
      refreshInFlight.current = false
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
    }, 30_000)
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
  if (!user)
    return (
      <div className="login-screen">
        <div className="login-card" role="status">
          <div className="login-spinner" />
          Carregando seu workspace...
        </div>
      </div>
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
          text: `Não foi possível obter resposta. ${describeApiError(
            error,
            "Tente novamente em alguns instantes.",
          )}`,
          error: true,
          retry_question: text,
          retry_attempt: options.retryAttempt ?? 0,
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
      // Feedback is optional, but the user still needs to know why a retry did
      // not appear. Keep the answer and surface a non-blocking status instead
      // of silently leaving the old response unchanged.
      setChat((prev) =>
        prev.map((item) =>
          item.analytics_id === analyticsId
            ? {
                ...item,
                learning: {
                  ...item.learning,
                  message:
                    "O feedback foi marcado localmente, mas não foi possível iniciar a nova tentativa agora. Tente novamente em instantes.",
                },
              }
            : item,
        ),
      )
    } finally {
      feedbackInFlight.current.delete(analyticsId)
    }
  }
  return (
    <AppShell
      modules={items}
      activeModule={mod}
      activePage={page}
      user={user}
      dark={dark}
      apiOnline={apiOnline}
      provider={provider}
      providerAvailability={capabilities?.providers}
      onModuleChange={selectModule}
      onPageChange={(nextPage) => setPage(nextPage as Page)}
      onThemeChange={() =>
        setDark((value) => {
          localStorage.setItem("sofia_theme", value ? "light" : "dark")
          return !value
        })
      }
      onProviderChange={(nextProvider) => setProvider(nextProvider as Provider)}
      onLogout={logout}
      isAdmin={user.user_code === "AG000001"}
    >
      {page === "dashboard" && (
        <Dashboard
          mod={mod}
          online={apiOnline}
          authFetch={authFetch}
          isAdmin={user.user_code === "AG000001"}
        />
      )}
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
      )}
      {page === "modules" && (
        <Modules items={items} selected={mod.id} selectModule={selectModule} />
      )}
      {page === "upload" && (
        <KnowledgeUpload mod={mod} authFetch={authFetch} onUploaded={refresh} />
      )}
      {page === "neural" && <NeuralView mod={mod} authFetch={authFetch} />}
      {page === "connections" && (
        <Connections items={items} capabilities={capabilities} />
      )}
      {page === "pipeline" && user.user_code === "AG000001" && (
        <PipelineExplorer mod={mod} authFetch={authFetch} items={items} />
      )}
      {page === "access" && user.role === "admin" && (
        <>
          <AccessControl authFetch={authFetch} />
          <UserAdministration authFetch={authFetch} />
        </>
      )}
    </AppShell>
  )
}

export default App
