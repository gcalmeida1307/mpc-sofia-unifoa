/** Public browser contracts for the admin observability surface. */

export type SofiaAuthFetch = (
  path: string,
  init?: RequestInit,
) => Promise<Response>

export type PipelineDocument = {
  id: number | string
  file_name?: string
  mime_type?: string
  status?: string
  current_stage?: string
  extraction_quality?: number | null
  ocr_quality?: number | null
  chunk_count?: number
  source_origin?: string
  author?: string | null
  sensitivity?: string
  version_number?: number
  validation_status?: string
  events?: Array<{
    stage?: string
    status?: string
    started_at?: string
    finished_at?: string
    error_message?: string | null
  }>
  artifacts?: Record<string, unknown>
}

export type PipelinePayload = {
  module_id: string
  stages: string[]
  documents: PipelineDocument[]
}

export type EmbeddingsPayload = {
  enabled: boolean
  query_enabled: boolean
  model: string
  max_chunks_per_module?: number
  ollama_available: boolean
  available_models?: string[]
  storage?: { backend?: string; postgres_configured?: boolean; postgres_error?: string | null }
  modules?: Array<{ module_id: string; status: string; items: number; chunk_count?: number; dimension: number }>
}

export type ObservabilityPayload = {
  total: number
  traces: Array<Record<string, unknown>>
}

export type InsightsPayload = {
  count: number
  insights: Array<Record<string, unknown>>
}

export type EvaluationPayload = {
  kind: string
  note: string
  global_score: number
  modules: Array<{
    module: string
    score: number
    documents: number
    ready: number
    retrieval_evidence: number
    status: string
  }>
  semantic_evaluation?: {
    global_score: number
    case_count: number
    cases: Array<{
      case_id: string
      module: string
      category: string
      evidence_count: number
      term_coverage: number
      source_match: boolean | null
      score: number
      status: string
    }>
  }
}

export type ReadinessLevel = {
  id: number
  title: string
  status: "ready" | "partial" | "blocked" | string
  status_label: string
  score: number
  details: string
  evidence: string[]
  action?: string | null
}

export type ReadinessPayload = {
  module_id: string
  evaluated_at: string
  ready_levels: number
  partial_levels: number
  blocked_levels: number
  scale_ready: boolean
  summary: string
  levels: ReadinessLevel[]
}
