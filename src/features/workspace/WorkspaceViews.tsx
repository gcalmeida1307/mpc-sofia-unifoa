import { useEffect, useState, type CSSProperties } from "react"
import { describeApiError } from "../../services/api-client"
import type { KnowledgeModule } from "../../knowledge"
import type { ExpansionStatus, ThemeAnalytics, WorkspaceCapabilities } from "../../types/workspace"

type Module = KnowledgeModule
type Capabilities = WorkspaceCapabilities

export function Dashboard({
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
  const [themeAnalytics, setThemeAnalytics] = useState<ThemeAnalytics | null>(
    null,
  )
  const [analyticsBusy, setAnalyticsBusy] = useState(false)
  const [expansion, setExpansion] = useState<ExpansionStatus | null>(null)
  const [expansionBusy, setExpansionBusy] = useState(false)
  useEffect(() => {
    let disposed = false
    setAnalyticsBusy(true)
    void authFetch(
      `/api/analytics/themes?module_id=${encodeURIComponent(mod.id)}&days=30&limit=8`,
    )
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
    void authFetch(
      `/api/admin/expansion?module_id=${encodeURIComponent(mod.id)}`,
    )
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
      setAnalysis(`Falha: ${describeApiError(error)}`)
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
    evaluated:
      feedbackSummary?.evaluated_answers ?? rowFeedbackTotals.evaluated,
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
        <section
          className="expansion-card"
          aria-label="Expansão contínua do conhecimento"
        >
          <div className="expansion-card-heading">
            <div>
              <h3>Expansão contínua</h3>
              <small>
                Fila persistente · fontes aprovadas · conhecimento offline
              </small>
            </div>
            <span
              className={
                expansion.settings?.paused
                  ? "expansion-state paused"
                  : "expansion-state"
              }
            >
              {expansion.settings?.paused ? "pausada" : "ativa"}
            </span>
          </div>
          <div className="expansion-metrics">
            <span>
              <b>{expansion.queue_pending}</b>
              <small>na fila</small>
            </span>
            <span>
              <b>{expansion.documents_by_status?.READY ?? 0}</b>
              <small>documentos prontos</small>
            </span>
            <span>
              <b>{expansion.sources_by_status?.READY ?? 0}</b>
              <small>fontes registradas</small>
            </span>
            <span>
              <b>{expansion.processing_errors}</b>
              <small>erros isolados</small>
            </span>
          </div>
          <div className="expansion-card-footer">
            <small>
              {expansion.last_cycle?.finished_at
                ? `Último ciclo: ${new Date(expansion.last_cycle.finished_at).toLocaleString("pt-BR")}`
                : "Nenhum ciclo executado ainda"}
            </small>
            <div>
              <button
                type="button"
                className="neural-run secondary"
                onClick={() => void toggleExpansion()}
                disabled={expansionBusy}
              >
                {expansion.settings?.paused ? "Retomar" : "Pausar"}
              </button>
              <button
                type="button"
                className="neural-run"
                onClick={() => void runExpansion()}
                disabled={expansionBusy || Boolean(expansion.settings?.paused)}
              >
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
          <div
            className="theme-total"
            aria-label="Total de consultas no período"
          >
            <strong>{themeAnalytics?.total_queries ?? 0}</strong>
            <span>consultas</span>
          </div>
        </div>
        {themeRows.length > 0 && (
          <div
            className="theme-feedback-summary"
            aria-label="Qualidade das respostas"
          >
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
              <div
                className="theme-row"
                key={`${item.module_id}-${item.theme}`}
              >
                <div className="theme-row-label">
                  <div className="theme-row-title">
                    <span className="theme-rank">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <div>
                      <b>{item.theme}</b>
                      {item.intent && <small>{item.intent}</small>}
                    </div>
                  </div>
                  <div className="theme-row-count">
                    <strong>{item.consultations}</strong>
                    <span>
                      {item.consultations === 1 ? "consulta" : "consultas"}
                    </span>
                  </div>
                </div>
                <div className="theme-meter" aria-hidden="true">
                  <i
                    style={{
                      width: `${(item.consultations / maxThemeConsultations) * 100}%`,
                    }}
                  />
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
          <p className="theme-empty">
            Ainda não há consultas registradas para este módulo.
          </p>
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
                  <em>
                    {item.consultations} consulta
                    {item.consultations === 1 ? "" : "s"}
                  </em>
                </span>
              ))}
            </div>
          </div>
        )}
        <small className="analytics-note">
          Visível somente para AG000001. São guardados módulo, usuário, tema,
          horário, fontes, motor e feedback; perguntas, respostas e conteúdo
          clínico não são armazenados.
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
export function Modules({
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
            style={{ "--module-color": item.color } as CSSProperties}
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
export function Connections({
  items,
  capabilities,
}: {
  items: Module[]
  capabilities: WorkspaceCapabilities | null
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
      } · Claude ${
        providerState.claude ? "liberado" : "local/bloqueado"
      } · store=${capabilities?.openai_store_responses ? "true" : "false"}`,
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

