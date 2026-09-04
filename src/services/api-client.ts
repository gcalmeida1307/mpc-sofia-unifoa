export type ApiErrorKind = "offline" | "timeout" | "unauthorized" | "forbidden" | "validation" | "provider" | "retrieval" | "pipeline" | "server" | "unknown"

export class SofiaApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number
  readonly endpoint: string
  readonly requestId: string
  readonly retryable: boolean
  readonly durationMs?: number

  constructor(
    message: string,
    options: {
      kind: ApiErrorKind
      endpoint: string
      requestId: string
      status?: number
      retryable?: boolean
      durationMs?: number
    },
  ) {
    super(message)
    this.name = "SofiaApiError"
    this.kind = options.kind
    this.status = options.status
    this.endpoint = options.endpoint
    this.requestId = options.requestId
    this.retryable = options.retryable ?? false
    this.durationMs = options.durationMs
  }
}

const DEFAULT_TIMEOUT_MS = 30_000

function resolveApiBaseUrl(): string {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL
  if (typeof window !== "undefined") {
    const host = window.location.hostname
    if (host !== "127.0.0.1" && host !== "localhost")
      return `${window.location.protocol}//${host}:8787`
  }
  return "http://127.0.0.1:8787"
}

export const API_BASE_URL = resolveApiBaseUrl()

function requestId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto)
    return crypto.randomUUID()
  return `sofia-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function classifyStatus(status: number, endpoint: string): ApiErrorKind {
  if (status === 401) return "unauthorized"
  if (status === 403) return "forbidden"
  if (status === 400 || status === 409 || status === 422) return "validation"
  if (endpoint.includes("provider") || endpoint.includes("chat"))
    return "provider"
  if (endpoint.includes("pipeline") || endpoint.includes("embedding"))
    return "pipeline"
  return status >= 500 ? "server" : "unknown"
}

function timeoutFor(endpoint: string): number {
  if (endpoint === "/api/chat") return 60_000
  if (endpoint.includes("/upload")) return 120_000
  return DEFAULT_TIMEOUT_MS
}

async function responseMessage(response: Response): Promise<string> {
  try {
    const body: unknown = await response.clone().json()
    if (typeof body === "object" && body !== null && "detail" in body) {
      const detail = (body as { detail?: unknown }).detail
      if (typeof detail === "string" && detail.trim()) return detail
    }
    if (typeof body === "object" && body !== null && "message" in body) {
      const message = (body as { message?: unknown }).message
      if (typeof message === "string" && message.trim()) return message
    }
  } catch {
    // Some infrastructure failures return an empty or non-JSON body.
  }
  return `A API respondeu com status ${response.status}.`
}

export async function apiRequest(
  endpoint: string,
  init: RequestInit = {},
  options: { token?: string | null; timeoutMs?: number } = {},
): Promise<Response> {
  const controller = new AbortController()
  const startedAt =
    typeof performance !== "undefined" ? performance.now() : Date.now()
  let outcome = "unknown"
  const timer = window.setTimeout(
    () => controller.abort(),
    options.timeoutMs ?? timeoutFor(endpoint),
  )
  const headers = new Headers(init.headers)
  if (!(init.body instanceof FormData) && !headers.has("Content-Type"))
    headers.set("Content-Type", "application/json")
  if (options.token) headers.set("Authorization", `Bearer ${options.token}`)
  const id = requestId()
  headers.set("X-Request-ID", id)

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...init,
      headers,
      signal: init.signal ?? controller.signal,
    })
    if (!response.ok) {
      const message = await responseMessage(response)
      throw new SofiaApiError(message, {
        kind: classifyStatus(response.status, endpoint),
        endpoint,
        requestId: response.headers.get("X-Request-ID") ?? id,
        status: response.status,
        retryable: response.status >= 500,
        durationMs: Math.round(
          (typeof performance !== "undefined"
            ? performance.now()
            : Date.now()) - startedAt,
        ),
      })
    }
    outcome = "success"
    return response
  } catch (error) {
    if (error instanceof SofiaApiError) {
      outcome = `error:${error.kind}`
      throw error
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      outcome = "error:timeout"
      throw new SofiaApiError(
        "A operação demorou mais que o esperado. Tente novamente.",
        {
          kind: "timeout",
          endpoint,
          requestId: id,
          retryable: true,
          durationMs: Math.round(
            (typeof performance !== "undefined"
              ? performance.now()
              : Date.now()) - startedAt,
          ),
        },
      )
    }
    outcome = "error:offline"
    throw new SofiaApiError(
      "A API local está indisponível. Verifique se o servidor está ativo na porta 8787.",
      {
        kind: "offline",
        endpoint,
        requestId: id,
        retryable: true,
        durationMs: Math.round(
          (typeof performance !== "undefined"
            ? performance.now()
            : Date.now()) - startedAt,
        ),
      },
    )
  } finally {
    window.clearTimeout(timer)
    if (typeof window !== "undefined") {
      window.dispatchEvent(
        new CustomEvent("sofia:api", {
          detail: {
            endpoint,
            request_id: id,
            duration_ms: Math.round(
              (typeof performance !== "undefined"
                ? performance.now()
                : Date.now()) - startedAt,
            ),
            outcome,
          },
        }),
      )
    }
  }
}

export async function apiJson<T>(
  endpoint: string,
  init: RequestInit = {},
  options: { token?: string | null; timeoutMs?: number } = {},
): Promise<T> {
  const response = await apiRequest(endpoint, init, options)
  try {
    return (await response.json()) as T
  } catch {
    throw new SofiaApiError("A API retornou uma resposta inválida.", {
      kind: "server",
      endpoint,
      requestId: response.headers.get("X-Request-ID") ?? "unknown",
      status: response.status,
    })
  }
}

export function describeApiError(
  error: unknown,
  fallback = "Não foi possível concluir a operação.",
): string {
  if (error instanceof SofiaApiError) {
    if (error.kind === "unauthorized")
      return "Sua sessão expirou. Entre novamente para continuar."
    if (error.kind === "forbidden")
      return "Sua conta não possui autorização para esta ação."
    return error.message
  }
  if (error instanceof Error && error.message.trim()) return error.message
  return fallback
}
