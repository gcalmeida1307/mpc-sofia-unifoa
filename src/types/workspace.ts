export type WorkspaceCapabilities = {
  ocr?: { available: boolean; engine: string; language?: string }
  links?: { storage: string; postgres_configured: boolean }
  providers?: Record<"auto" | "openai" | "gemini" | "claude" | "ollama", boolean>
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
export type ExpansionStatus = {
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
  last_cycle?: {
    finished_at?: string
    status?: string
    pages_new?: number
    errors?: number
  } | null
}
export type ThemeAnalytics = {
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
