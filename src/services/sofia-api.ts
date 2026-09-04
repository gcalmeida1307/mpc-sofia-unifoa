import type {
  EmbeddingsPayload,
  EvaluationPayload,
  InsightsPayload,
  ObservabilityPayload,
  PipelinePayload,
  ProductionGatePayload,
  ReadinessPayload,
  SofiaAuthFetch,
} from "../types/contracts"

/**
 * Browser adapter for the local API. It deliberately contains no provider
 * keys and keeps the admin-only endpoints behind the caller's session fetch.
 */
export async function loadAdminPipeline(
  authFetch: SofiaAuthFetch,
  moduleId: string,
  limit = 80,
): Promise<{
  pipeline: PipelinePayload | null
  observability: ObservabilityPayload | null
  insights: InsightsPayload | null
  embeddings: EmbeddingsPayload | null
}> {
  const query = `module_id=${encodeURIComponent(moduleId)}&limit=${limit}`
  const [pipelineResponse, traceResponse, insightResponse, embeddingsResponse] =
    await Promise.all([
      authFetch(`/api/admin/pipeline?${query}`),
      authFetch(`/api/admin/observability?${query}`),
      authFetch(`/api/admin/insights?${query}`),
      authFetch(`/api/admin/embeddings?${query}`),
    ])
  return {
    pipeline: pipelineResponse.ok
      ? (await pipelineResponse.json()) as PipelinePayload
      : null,
    observability: traceResponse.ok
      ? (await traceResponse.json()) as ObservabilityPayload
      : null,
    insights: insightResponse.ok
      ? (await insightResponse.json()) as InsightsPayload
      : null,
    embeddings: embeddingsResponse.ok
      ? (await embeddingsResponse.json()) as EmbeddingsPayload
      : null,
  }
}

export async function loadAdminReadiness(
  authFetch: SofiaAuthFetch,
  moduleId: string,
): Promise<ReadinessPayload | null> {
  const response = await authFetch(
    `/api/admin/readiness?module_id=${encodeURIComponent(moduleId)}`,
  )
  return response.ok ? (await response.json()) as ReadinessPayload : null
}

export async function runAdminEvaluation(
  authFetch: SofiaAuthFetch,
): Promise<EvaluationPayload | null> {
  const response = await authFetch("/api/admin/evaluation")
  return response.ok ? (await response.json()) as EvaluationPayload : null
}

export async function runAdminProductionGate(
  authFetch: SofiaAuthFetch,
): Promise<ProductionGatePayload | null> {
  const response = await authFetch("/api/admin/production-gate")
  return response.ok ? (await response.json()) as ProductionGatePayload : null
}
