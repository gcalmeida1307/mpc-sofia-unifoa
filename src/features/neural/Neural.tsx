import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react"
import { knowledgeModules, type KnowledgeModule } from "../../knowledge"
import { describeApiError } from "../../services/api-client"

type NeuralModule = Pick<KnowledgeModule, "id" | "name" | "icon" | "color" | "docs">

type AuthFetch = (path: string, init?: RequestInit) => Promise<Response>

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

type ClusterPosition = { x: number; y: number }

const CLUSTER_POSITIONS: ClusterPosition[] = [
  { x: 14, y: 18 },
  { x: 37, y: 10 },
  { x: 63, y: 10 },
  { x: 86, y: 20 },
  { x: 94, y: 47 },
  { x: 84, y: 76 },
  { x: 62, y: 90 },
  { x: 37, y: 89 },
  { x: 15, y: 76 },
  { x: 7, y: 48 },
  { x: 27, y: 47 },
]

function conceptsFor(graph: NeuralGraph | undefined): GraphNode[] {
  return (graph?.nodes ?? [])
    .filter((node) => node.kind === "concept")
    .sort((left, right) => right.frequency - left.frequency)
    .slice(0, 6)
}

function ArchitecturePreview({
  graph,
  color,
}: {
  graph?: NeuralGraph
  color: string
}) {
  const layers = graph?.architecture?.length
    ? graph.architecture.slice(0, 3)
    : [3, 4, 3]
  const weights = graph?.weights ?? {}
  const yPosition = (count: number, index: number) =>
    12 + (76 * index) / Math.max(1, count - 1)

  return (
    <svg className="neural-architecture-preview" viewBox="0 0 100 100" aria-label="Arquitetura neural">
      {layers.slice(0, 2).flatMap((count, layer) =>
        Array.from({ length: count }, (_, from) =>
          Array.from({ length: layers[layer + 1] ?? 0 }, (_, to) => {
            const matrix = layer === 0 ? weights.w1 : weights.w2
            const weight = Number(matrix?.[from]?.[to] ?? 0)
            return (
              <line
                key={`${layer}-${from}-${to}`}
                x1={layer === 0 ? 15 : 50}
                y1={yPosition(count, from)}
                x2={layer === 0 ? 50 : 85}
                y2={yPosition(layers[layer + 1] ?? 1, to)}
                style={{
                  stroke: color,
                  strokeWidth: Math.min(1.5, 0.35 + Math.abs(weight) * 1.5),
                  opacity: graph?.trained ? Math.min(0.8, 0.18 + Math.abs(weight)) : 0.2,
                }}
              />
            )
          }),
        ),
      )}
      {layers.map((count, layer) =>
        Array.from({ length: count }, (_, node) => (
          <circle
            key={`${layer}-${node}`}
            cx={layer === 0 ? 15 : layer === 1 ? 50 : 85}
            cy={yPosition(count, node)}
            r="2.25"
            style={{ fill: color, opacity: graph?.trained ? 1 : 0.5 }}
          />
        )),
      )}
    </svg>
  )
}

function NeuralConstellation({
  modules,
  graphs,
  selectedId,
  onSelect,
}: {
  modules: NeuralModule[]
  graphs: Record<string, NeuralGraph>
  selectedId: string
  onSelect: (moduleId: string) => void
}) {
  const center = { x: 50, y: 50 }

  return (
    <div className="neural-map-stage">
      <div className="neural-map-grid" aria-hidden="true" />
      <svg
        className="neural-constellation"
        viewBox="0 0 100 100"
        role="img"
        aria-label="Mapa neural dos módulos e conceitos da SOFIA"
      >
        <defs>
          <radialGradient id="sofia-core-gradient">
            <stop offset="0%" stopColor="#f5f3ff" />
            <stop offset="35%" stopColor="#b79aff" />
            <stop offset="100%" stopColor="#6d28d9" />
          </radialGradient>
          <filter id="sofia-neural-glow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="1.8" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <g className="neural-global-links" aria-hidden="true">
          {modules.map((module, index) => {
            const position = CLUSTER_POSITIONS[index % CLUSTER_POSITIONS.length]
            return (
              <line
                key={`center-${module.id}`}
                x1={center.x}
                y1={center.y}
                x2={position.x}
                y2={position.y}
                style={{ stroke: module.color, opacity: module.id === selectedId ? 0.55 : 0.13 }}
              />
            )
          })}
          {modules.map((module, index) => {
            const position = CLUSTER_POSITIONS[index % CLUSTER_POSITIONS.length]
            const next = CLUSTER_POSITIONS[(index + 1) % CLUSTER_POSITIONS.length]
            return (
              <line
                key={`ring-${module.id}`}
                x1={position.x}
                y1={position.y}
                x2={next.x}
                y2={next.y}
                style={{ stroke: module.color, opacity: 0.08 }}
              />
            )
          })}
        </g>
        <g className="neural-core" filter="url(#sofia-neural-glow)">
          <circle cx={center.x} cy={center.y} r="8.3" className="neural-core-halo" />
          <circle cx={center.x} cy={center.y} r="4.4" fill="url(#sofia-core-gradient)" />
          <text x={center.x} y="48.3" textAnchor="middle" className="neural-core-mark">S</text>
          <text x={center.x} y="61" textAnchor="middle" className="neural-core-label">SOFIA CORE</text>
        </g>
        <g className="neural-clusters">
          {modules.map((module, index) => {
            const position = CLUSTER_POSITIONS[index % CLUSTER_POSITIONS.length]
            const graph = graphs[module.id]
            const concepts = conceptsFor(graph)
            const selected = module.id === selectedId
            return (
              <g
                key={module.id}
                className={`neural-cluster ${selected ? "is-selected" : ""}`}
                transform={`translate(${position.x},${position.y})`}
                style={{ color: module.color } as CSSProperties}
                role="button"
                tabIndex={0}
                aria-label={`Selecionar módulo ${module.name}`}
                onClick={() => onSelect(module.id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") onSelect(module.id)
                }}
              >
                <circle r={selected ? 3.7 : 2.75} className="neural-cluster-halo" />
                <circle r={selected ? 2.1 : 1.55} className="neural-cluster-dot" />
                <text y="6.2" textAnchor="middle" className="neural-cluster-label">
                  {module.name}
                </text>
                {concepts.map((concept, conceptIndex) => {
                  const angle = (Math.PI * 2 * conceptIndex) / Math.max(1, concepts.length)
                  const radius = selected ? 7.2 : 5.5
                  const x = Math.cos(angle) * radius
                  const y = Math.sin(angle) * radius
                  return (
                    <g key={concept.id} className="neural-concept-node" transform={`translate(${x},${y})`}>
                      <line x1="0" y1="0" x2={-x * 0.32} y2={-y * 0.32} />
                      <circle r={selected ? 0.72 : 0.48} />
                      {selected && (
                        <text x={x >= 0 ? 1.4 : -1.4} y="0.7" textAnchor={x >= 0 ? "start" : "end"}>
                          {concept.label.slice(0, 18)}
                        </text>
                      )}
                    </g>
                  )
                })}
              </g>
            )
          })}
        </g>
      </svg>
      <div className="neural-map-caption">
        <span><i className="neural-legend-dot core" /> núcleo Sofia</span>
        <span><i className="neural-legend-dot module" /> módulo</span>
        <span><i className="neural-legend-dot concept" /> conceito</span>
        <span><i className="neural-legend-line" /> relação observada</span>
      </div>
    </div>
  )
}

export default function Neural({
  mod,
  authFetch,
}: {
  mod: NeuralModule
  authFetch: AuthFetch
}) {
  const modules = useMemo<NeuralModule[]>(() => {
    const catalog = knowledgeModules.map((item) => ({
      id: item.id,
      name: item.name,
      icon: item.icon,
      color: item.color,
      docs: item.docs,
    }))
    return catalog.map((item) => (item.id === mod.id ? { ...item, ...mod } : item))
  }, [mod])
  const [graphs, setGraphs] = useState<Record<string, NeuralGraph>>({})
  const [loadingModules, setLoadingModules] = useState<Record<string, boolean>>({})
  const loadingModulesRef = useRef(new Set<string>())
  const [selectedId, setSelectedId] = useState(mod.id)
  const [result, setResult] = useState("")
  const [busy, setBusy] = useState(false)
  const [controlsOpen, setControlsOpen] = useState(true)
  const [values, setValues] = useState(["0.2", "0.7", "0.4"])

  const selectedModule = modules.find((item) => item.id === selectedId) ?? mod
  const graph = graphs[selectedModule.id]
  const model = graph?.training

  const loadModule = async (moduleId: string) => {
    if (loadingModulesRef.current.has(moduleId)) return
    loadingModulesRef.current.add(moduleId)
    setLoadingModules((current) => ({ ...current, [moduleId]: true }))
    try {
      const response = await authFetch("/api/tools/neural_graph", {
        method: "POST",
        body: JSON.stringify({ arguments: { module_id: moduleId } }),
      })
      const data = (await response.json()) as NeuralGraph & { detail?: string }
      if (!response.ok) throw new Error(data.detail ?? "Falha ao consultar o modelo")
      setGraphs((current) => ({ ...current, [moduleId]: data }))
      return data
    } finally {
      loadingModulesRef.current.delete(moduleId)
      setLoadingModules((current) => ({ ...current, [moduleId]: false }))
    }
  }

  useEffect(() => {
    setSelectedId(mod.id)
    setResult("")
    void loadModule(mod.id).catch((error) => setResult(describeApiError(error, "Não foi possível carregar a rede neural.")))
  }, [mod.id])

  const train = async () => {
    setBusy(true)
    setResult(`Treinando ${selectedModule.name} com os documentos do módulo...`)
    try {
      const response = await authFetch("/api/tools/neural_train", {
        method: "POST",
        body: JSON.stringify({
          arguments: { module_id: selectedModule.id, epochs: 160, learning_rate: 0.08 },
        }),
      })
      const data = (await response.json()) as { detail?: string; samples?: number; mse?: number }
      if (!response.ok) throw new Error(data.detail ?? "Falha no treinamento")
      await loadModule(selectedModule.id)
      setResult(`Modelo adaptado com ${data.samples ?? 0} chunks · MSE ${data.mse ?? "—"} · grafo atualizado.`)
    } catch (error) {
      setResult(describeApiError(error, "Não foi possível treinar a rede neural."))
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
          arguments: { module_id: selectedModule.id, values: values.map(Number) },
        }),
      })
      const data = (await response.json()) as { detail?: string; reconstruction?: number[]; reconstruction_error?: number }
      if (!response.ok) throw new Error(data.detail ?? "Falha na inferência")
      setResult(`Reconstrução: [${data.reconstruction?.join(", ") ?? ""}] · erro: ${data.reconstruction_error ?? "—"}`)
    } catch (error) {
      setResult(describeApiError(error, "Não foi possível executar a inferência."))
    } finally {
      setBusy(false)
    }
  }

  const concepts = conceptsFor(graph)
  const documentCount = graph?.document_count ?? (Number(selectedModule.docs) || 0)
  const chunkCount = graph?.training?.samples ?? 0
  const selectedModuleLoading = Boolean(loadingModules[selectedModule.id])

  return (
    <div className="page-body neural-page">
      <div className="neural-heading-row">
        <div>
          <div className="neural-eyebrow">INTELIGÊNCIA · CONHECIMENTO · RELAÇÕES</div>
          <h1>
            Mapa Neural <em>S.O.F.I.A.</em>
          </h1>
          <p className="page-subtitle">
            Uma visão viva dos módulos, documentos e conceitos que sustentam a inteligência institucional.
          </p>
        </div>
        <div className="neural-heading-status">
          <span className="neural-live-dot" /> {modules.length} módulos conectados
        </div>
      </div>

      <div className="neural-toolbar">
        <div className="neural-selected-module" style={{ "--module-color": selectedModule.color } as CSSProperties}>
          <span>{selectedModule.icon}</span>
          <b>{selectedModule.name}</b>
          <small>{documentCount} documentos · {graph?.concept_count ?? 0} conceitos{selectedModuleLoading ? " · carregando grafo…" : ""}</small>
        </div>
        <button className="neural-control-toggle" type="button" onClick={() => setControlsOpen((open) => !open)}>
          {controlsOpen ? "Ocultar controles" : "Abrir controles"}
        </button>
      </div>

      <div className={`neural-workbench ${controlsOpen ? "controls-visible" : "controls-hidden"}`}>
        <section className="neural-map-card" aria-label="Mapa neural">
          <div className="neural-map-card-heading">
            <div>
              <b>Constelação institucional</b>
              <small>Clique em um cluster para explorar o módulo e seus conceitos ativos.</small>
            </div>
            <span className="neural-map-metric">{selectedModuleLoading ? "carregando…" : `${chunkCount || "—"} chunks indexados`}</span>
          </div>
          <NeuralConstellation
            modules={modules}
            graphs={graphs}
            selectedId={selectedModule.id}
            onSelect={(moduleId) => {
              setSelectedId(moduleId)
              setResult("")
              if (!graphs[moduleId]) {
                void loadModule(moduleId).catch((error) => setResult(describeApiError(error, "Não foi possível carregar o mapa deste módulo.")))
              }
            }}
          />
        </section>

        {controlsOpen && (
          <aside className="neural-control-panel" aria-label={`Controles do módulo ${selectedModule.name}`}>
            <div className="neural-panel-title">
              <span>CONTROLES · {selectedModule.name.toUpperCase()}</span>
              <i style={{ background: selectedModule.color }} />
            </div>
            <div className="neural-stats-grid">
              <div><small>DOCUMENTOS</small><strong>{documentCount}</strong></div>
              <div><small>CHUNKS</small><strong>{chunkCount || "—"}</strong></div>
              <div><small>ÉPOCAS</small><strong>{model?.epochs ?? "—"}</strong></div>
              <div><small>MSE</small><strong>{model?.mse ?? "—"}</strong></div>
            </div>
            <div className="neural-panel-section">
              <div className="neural-panel-section-heading"><b>ARQUITETURA</b><small>{graph?.trained ? "treinada" : "aguardando treino"}</small></div>
              <ArchitecturePreview graph={graph} color={selectedModule.color} />
              <div className="neural-layer-labels"><span>ENTRADA</span><span>OCULTA</span><span>SAÍDA</span></div>
            </div>
            <button className="neural-panel-button" type="button" disabled={busy} onClick={() => void train()}>
              {busy ? "Processando..." : `Treinar com knowledge/${selectedModule.id} →`}
            </button>
            <div className="neural-panel-section inference-section">
              <div className="neural-panel-section-heading"><b>INFERÊNCIA</b><small>3 features</small></div>
              <div className="neural-inputs neural-panel-inputs">
                {values.map((value, index) => (
                  <input
                    key={index}
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={value}
                    onChange={(event) => setValues((current) => current.map((item, itemIndex) => itemIndex === index ? event.target.value : item))}
                    aria-label={`Feature ${index + 1}`}
                  />
                ))}
              </div>
              <button className="neural-panel-button secondary" type="button" disabled={busy || !graph?.trained} onClick={() => void run()}>
                Executar inferência →
              </button>
            </div>
            <div className="neural-panel-section neural-concepts-panel">
              <div className="neural-panel-section-heading"><b>CONCEITOS ATIVOS</b><small>{concepts.length || 0} observados</small></div>
              <div className="neural-concept-chips">
                {concepts.length ? concepts.map((concept) => <span key={concept.id}>{concept.label}</span>) : <small>{selectedModuleLoading ? "Carregando o grafo do módulo…" : "Aguardando a indexação do módulo."}</small>}
              </div>
            </div>
          </aside>
        )}
      </div>

      {result && <div className="neural-result" role="status">{result}</div>}
      <p className="neural-disclaimer">As conexões exibidas representam relações observadas nos documentos e chunks locais; não são causalidade nem conhecimento inventado pelo modelo.</p>
    </div>
  )
}
