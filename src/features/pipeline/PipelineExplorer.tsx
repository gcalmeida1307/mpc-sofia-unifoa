import { useEffect, useState } from "react"
import { loadAdminPipeline, loadAdminReadiness, runAdminEvaluation } from "../../services/sofia-api"
import type {
  EmbeddingsPayload,
  EvaluationPayload,
  InsightsPayload,
  ObservabilityPayload,
  PipelinePayload,
  ReadinessPayload,
  SofiaAuthFetch,
} from "../../types/contracts"

type PipelineModule = { id: string; name: string; color?: string; icon?: string }

export default function PipelineExplorer({
  mod,
  items,
  authFetch,
}: {
  mod: PipelineModule
  items: PipelineModule[]
  authFetch: SofiaAuthFetch
}) {
  const [selected, setSelected] = useState(mod.id)
  const [payload, setPayload] = useState<PipelinePayload | null>(null)
  const [observability, setObservability] = useState<ObservabilityPayload | null>(null)
  const [insights, setInsights] = useState<InsightsPayload | null>(null)
  const [embeddings, setEmbeddings] = useState<EmbeddingsPayload | null>(null)
  const [readiness, setReadiness] = useState<ReadinessPayload | null>(null)
  const [evaluation, setEvaluation] = useState<EvaluationPayload | null>(null)
  const [busy, setBusy] = useState(false)
  const [evaluating, setEvaluating] = useState(false)

  const load = async (moduleId = selected) => {
    setBusy(true)
    try {
      const result = await loadAdminPipeline(authFetch, moduleId, 80)
      setPayload(result.pipeline)
      setObservability(result.observability)
      setInsights(result.insights)
      setEmbeddings(result.embeddings)
      setReadiness(null)
      void loadAdminReadiness(authFetch, moduleId).then(setReadiness).catch(() => setReadiness(null))
    } finally {
      setBusy(false)
    }
  }

  const evaluate = async () => {
    setEvaluating(true)
    try {
      setEvaluation(await runAdminEvaluation(authFetch))
    } finally {
      setEvaluating(false)
    }
  }

  useEffect(() => {
    void load()
  }, [selected])

  const documents = payload?.documents ?? []
  const selectedModule = items.find((item) => item.id === selected) ?? mod
  const embeddingRecord = embeddings?.modules?.find((item) => item.module_id === selected)
  const stageLabel = (stage: string) => (stage === "READY" ? "Pronto" : stage.replace(/_/g, " "))

  return (
    <div className="page-body explorer-page">
      <div className="page-heading-row">
        <div>
          <h1>Pipeline <em>Explorer</em></h1>
          <p className="page-subtitle">Acompanhe a ingestão real por documento: extração, OCR, qualidade, conhecimento, relações, índice e validação.</p>
        </div>
        <div className="explorer-toolbar">
          <label className="explorer-module-control" htmlFor="pipeline-module">
            <span>Módulo monitorado</span>
            <select id="pipeline-module" className="provider-select" value={selected} onChange={(event) => setSelected(event.target.value)}>
              {items.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </label>
          <div className="explorer-actions">
            <button className="neural-run" onClick={() => void load()} disabled={busy}>{busy ? "Atualizando..." : "Atualizar"}</button>
            <button className="neural-run secondary" onClick={() => void evaluate()} disabled={evaluating}>{evaluating ? "Avaliando..." : "Avaliar corpus"}</button>
          </div>
        </div>
      </div>
      <div className="explorer-health-grid">
        <article className="metric-card"><small>Documentos no pipeline</small><strong>{documents.length}</strong><span>{selectedModule.name}</span></article>
        <article className="metric-card"><small>Traces observáveis</small><strong>{observability?.total ?? 0}</strong><span>últimas execuções</span></article>
        <article className="metric-card"><small>Insights observados</small><strong>{insights?.count ?? 0}</strong><span>coocorrências, não causalidade</span></article>
        <article className="metric-card"><small>Smoke score técnico</small><strong>{evaluation ? `${evaluation.global_score}%` : "—"}</strong><span>corpus + pipeline + recuperação</span></article>
        <article className="metric-card"><small>Índice neural</small><strong>{embeddingRecord?.items ?? 0}</strong><span>{embeddingRecord?.status ?? "pending"} · {embeddings?.model ?? "embedding local"}</span></article>
      </div>
      {readiness && (
        <section className="explorer-panel readiness-panel">
          <div className="section-heading readiness-heading">
            <div><h2>Checklist de escala</h2><p>Dez níveis verificáveis para saber exatamente o que está pronto, parcial ou bloqueado.</p></div>
            <div className={`readiness-banner ${readiness.scale_ready ? "ready" : "attention"}`}><strong>{readiness.ready_levels}/10</strong><span>{readiness.scale_ready ? "Escala aprovada" : "Ainda não aprovado para escala"}</span></div>
          </div>
          <p className="readiness-summary">{readiness.summary}</p>
          <div className="readiness-list">
            {readiness.levels.map((level) => (
              <article className={`readiness-row readiness-${level.status}`} key={level.id}>
                <div className="readiness-level"><span className="readiness-number">{String(level.id).padStart(2, "0")}</span><div><strong>{level.title}</strong><small>{level.status_label}</small></div></div>
                <div className="readiness-content"><p>{level.details}</p><ul>{level.evidence.map((item, index) => <li key={`${level.id}-${index}`}>{item}</li>)}</ul>{level.action && <small className="readiness-action">Próximo passo: {level.action}</small>}</div>
                <div className="readiness-score" aria-label={`Score ${level.score}%`}><strong>{level.score}%</strong><span>evidência</span></div>
              </article>
            ))}
          </div>
          <small className="readiness-footnote">Avaliado em {new Date(readiness.evaluated_at).toLocaleString("pt-BR")}. Números ausentes não são estimados.</small>
        </section>
      )}
      <section className="explorer-panel">
        <div className="section-heading"><div><h2>Estados do documento</h2><p>Falhas permanecem identificadas e podem ser reprocessadas; metadados incompletos não viram “pronto”.</p></div><span className="status-pill active">somente administrador</span></div>
        {documents.length === 0 ? <div className="empty-state">Nenhum documento registrado neste módulo.</div> : (
          <div className="explorer-table-wrap"><table className="explorer-table"><thead><tr><th>Documento</th><th>Estado</th><th>Qualidade</th><th>Chunks</th><th>Etapas registradas</th></tr></thead><tbody>
            {documents.map((document) => {
              const status = String(document.status ?? "PENDING")
              const events = Array.isArray(document.events) ? (document.events as Array<Record<string, unknown>>) : []
              return <tr key={String(document.id)}><td><strong>{String(document.file_name ?? "Documento")}</strong><small>{String(document.mime_type ?? "")} · {String(document.source_origin ?? "origem não informada")} · v{String(document.version_number ?? "—")}</small><small>{String(document.sensitivity ?? "sensibilidade não informada")}</small></td><td><span className={`pipeline-status ${status.toLowerCase()}`}>{stageLabel(status)}</span></td><td>{document.extraction_quality == null ? "—" : `${Math.round(Number(document.extraction_quality) * 100)}%`}</td><td>{String(document.chunk_count ?? 0)}</td><td><div className="stage-chips">{events.map((event) => <span key={`${String(event.stage)}-${String(event.started_at)}`} title={String(event.error_message ?? "")} className={String(event.status).toLowerCase()}>{stageLabel(String(event.stage))}</span>)}</div></td></tr>
            })}
          </tbody></table></div>
        )}
      </section>
      <section className="explorer-panel">
        <div className="section-heading"><div><h2>Últimas execuções</h2><p>Latência, modelo, evidência, confiança, tokens e custo quando retornados; sem armazenar o conteúdo da pergunta.</p></div></div>
        <div className="trace-list">{(observability?.traces ?? []).slice(0, 6).map((trace) => {
          let metrics: Record<string, unknown> = {}
          try { metrics = JSON.parse(String(trace.metrics_json ?? "{}")) as Record<string, unknown> } catch { metrics = {} }
          const tokens = metrics.tokens ?? metrics.usage_tokens
          const cost = metrics.cost ?? metrics.cost_brl
          return <div className="trace-row" key={String(trace.trace_id)}><span className="status-dot" /><div className="trace-primary"><strong>{String(trace.provider ?? "local")}</strong><small>{String(trace.model ?? "modelo não registrado")} · {String(trace.complexity ?? "L1")}</small></div><div className="trace-metric"><strong>{trace.latency_ms == null ? "—" : `${Math.round(Number(trace.latency_ms))} ms`}</strong><small>latência</small></div><div className="trace-metric"><strong>{trace.confidence == null ? "—" : `${Math.round(Number(trace.confidence) * 100)}%`}</strong><small>confiança</small></div><div className="trace-metric"><strong>{String(metrics.source_count ?? 0)} fonte(s)</strong><small>evidência</small></div><div className="trace-metric trace-optional"><strong>{tokens == null ? "—" : String(tokens)}</strong><small>tokens · custo {cost == null ? "—" : String(cost)}</small></div></div>
        })}{!observability?.traces?.length && <div className="empty-state">Ainda não há traces para este módulo.</div>}</div>
      </section>
      {evaluation && <section className="explorer-panel"><div className="section-heading"><div><h2>Última avaliação do corpus</h2><p>{evaluation.note}</p></div></div><div className="evaluation-grid">{evaluation.modules.map((item) => <div className="evaluation-row" key={item.module}><strong>{item.module}</strong><span>{item.status === "ready" ? "pronto" : "precisa de dados"}</span><b>{item.score}%</b></div>)}</div>{evaluation.semantic_evaluation && <div className="evaluation-summary"><strong>Avaliação semântica de evidências: {evaluation.semantic_evaluation.global_score}%</strong><span>{evaluation.semantic_evaluation.case_count} casos revisáveis · cobertura de termos e aderência às fontes</span></div>}</section>}
    </div>
  )
}
