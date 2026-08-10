from prometheus_client import Counter, Gauge, Histogram


HTTP_REQUESTS = Counter("sofia_http_requests_total", "HTTP requests", ["method", "route", "status"])
HTTP_LATENCY = Histogram("sofia_http_request_duration_seconds", "HTTP request latency", ["method", "route"])
INTEGRATION_REQUESTS = Counter("sofia_integration_requests_total", "External integration requests", ["integration", "operation", "status"])
INTEGRATION_LATENCY = Histogram("sofia_integration_request_duration_seconds", "External integration latency", ["integration", "operation"])
LLM_REQUESTS = Counter("sofia_llm_requests_total", "LLM requests", ["provider", "status"])
LLM_TOKENS = Counter("sofia_llm_tokens_total", "LLM tokens", ["provider", "direction"])
WORKFLOW_RUNS = Counter("sofia_workflow_runs_total", "Workflow executions", ["status"])
SNAPSHOT_DURATION = Histogram("sofia_snapshot_duration_seconds", "Snapshot collection duration")
SNAPSHOT_AGE = Gauge("sofia_snapshot_age_seconds", "Age of the current shared snapshot")
