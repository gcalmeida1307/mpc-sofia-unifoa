import { useEffect, useState } from "react"
import { describeApiError } from "../../services/api-client"

type NeuralModule = {
  id: string
  color: string
}

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
        {layers.slice(0, 2).flatMap((count, layer) =>
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
        )}
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

export default function Neural({
  mod,
  authFetch,
}: {
  mod: NeuralModule
  authFetch: AuthFetch
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
      const data = (await response.json()) as NeuralGraph & { detail?: string }
      if (!response.ok)
        throw new Error(data.detail ?? "Falha ao consultar o modelo")
      setGraph(data)
    } catch (error) {
      setResult(
        describeApiError(error, "Não foi possível carregar o grafo neural."),
      )
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
      const data = (await response.json()) as {
        detail?: string
        samples?: number
        mse?: number
      }
      if (!response.ok) throw new Error(data.detail ?? "Falha no treinamento")
      await load()
      setResult(
        `Modelo adaptado com ${data.samples ?? 0} chunks · MSE ${data.mse ?? "—"} · grafo semântico atualizado`,
      )
    } catch (error) {
      setResult(
        describeApiError(error, "Não foi possível treinar a rede neural."),
      )
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
      const data = (await response.json()) as {
        detail?: string
        reconstruction?: number[]
        reconstruction_error?: number
      }
      if (!response.ok) throw new Error(data.detail ?? "Falha na inferência")
      setResult(
        `Reconstrução: [${data.reconstruction?.join(", ") ?? ""}] · erro: ${data.reconstruction_error ?? "—"}`,
      )
    } catch (error) {
      setResult(
        describeApiError(error, "Não foi possível executar a inferência."),
      )
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
          <button
            className="neural-run"
            disabled={busy}
            onClick={() => void train()}
          >
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
            onClick={() => void run()}
          >
            Executar inferência →
          </button>
        </div>
        {result && (
          <div className="upload-status" role="status">
            {result}
          </div>
        )}
        <small className="mcp-note">
          MCP: neural_graph · neural_status · neural_train · neural_infer. As
          arestas semânticas são coocorrências nos mesmos chunks; não são
          relações inventadas pelo modelo.
        </small>
      </div>
    </div>
  )
}
