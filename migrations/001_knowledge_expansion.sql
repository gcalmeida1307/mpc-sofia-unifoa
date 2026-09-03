-- SOFIA continuous knowledge expansion (PostgreSQL)
-- The local runtime initializes the equivalent SQLite schema automatically.
-- Apply this migration when SOFIA_POSTGRES_URL/DATABASE_URL is provisioned.

CREATE TABLE IF NOT EXISTS sofia_expansion_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sofia_search_topics (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    topic_key TEXT NOT NULL,
    main_topic TEXT NOT NULL,
    normalized_topic TEXT NOT NULL,
    origin TEXT NOT NULL,
    query_count INTEGER NOT NULL DEFAULT 0,
    last_searched_at TIMESTAMPTZ,
    last_expanded_at TIMESTAMPTZ,
    expansion_state TEXT NOT NULL DEFAULT 'PENDING',
    priority NUMERIC(8,3) NOT NULL DEFAULT 0,
    is_latest BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (module_id, topic_key)
);

CREATE TABLE IF NOT EXISTS sofia_search_queries (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES sofia_search_topics(id) ON DELETE CASCADE,
    user_code TEXT,
    original_query TEXT NOT NULL,
    normalized_query TEXT NOT NULL,
    keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    entities JSONB NOT NULL DEFAULT '[]'::jsonb,
    date_start TEXT,
    date_end TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sofia_topic_keywords (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL REFERENCES sofia_search_topics(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    origin_term TEXT NOT NULL,
    depth SMALLINT NOT NULL DEFAULT 0,
    confidence NUMERIC(5,4) NOT NULL DEFAULT 0,
    justification TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (topic_id, term)
);

CREATE TABLE IF NOT EXISTS sofia_expansion_queue (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT NOT NULL UNIQUE REFERENCES sofia_search_topics(id) ON DELETE CASCADE,
    state TEXT NOT NULL DEFAULT 'PENDING',
    priority NUMERIC(8,3) NOT NULL DEFAULT 0,
    available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    attempts INTEGER NOT NULL DEFAULT 0,
    last_started_at TIMESTAMPTZ,
    last_finished_at TIMESTAMPTZ,
    last_error TEXT
);

CREATE TABLE IF NOT EXISTS sofia_expansion_domains (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'allow' CHECK (mode IN ('allow', 'block')),
    reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (module_id, domain)
);

CREATE TABLE IF NOT EXISTS sofia_sources (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    url TEXT,
    normalized_url TEXT,
    canonical_url TEXT,
    local_path TEXT,
    title TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'PENDING',
    reliability NUMERIC(5,4) NOT NULL DEFAULT 0,
    content_hash TEXT,
    etag TEXT NOT NULL DEFAULT '',
    last_modified TEXT NOT NULL DEFAULT '',
    pages INTEGER NOT NULL DEFAULT 1,
    last_checked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (module_id, normalized_url),
    UNIQUE (module_id, local_path)
);

CREATE TABLE IF NOT EXISTS sofia_source_versions (
    id BIGSERIAL PRIMARY KEY,
    source_id BIGINT NOT NULL REFERENCES sofia_sources(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    local_path TEXT,
    status TEXT NOT NULL DEFAULT 'READY',
    bytes BIGINT NOT NULL DEFAULT 0,
    pages INTEGER NOT NULL DEFAULT 1,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, content_hash)
);

CREATE TABLE IF NOT EXISTS sofia_documents (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    source_id BIGINT REFERENCES sofia_sources(id),
    path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    mime_type TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'PENDING',
    content_hash TEXT,
    bytes BIGINT NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    version_number INTEGER NOT NULL DEFAULT 1,
    file_hash TEXT,
    duplicate_of BIGINT REFERENCES sofia_documents(id),
    source_origin TEXT NOT NULL DEFAULT 'local',
    author TEXT,
    sensitivity TEXT NOT NULL DEFAULT 'internal',
    current_stage TEXT NOT NULL DEFAULT 'RECEIVED',
    received_at TIMESTAMPTZ,
    extraction_quality DOUBLE PRECISION,
    ocr_quality DOUBLE PRECISION,
    summary TEXT,
    keywords_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    entities_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    concepts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    relations_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    questions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    embeddings_status TEXT NOT NULL DEFAULT 'PENDING',
    indexing_status TEXT NOT NULL DEFAULT 'PENDING',
    validation_status TEXT NOT NULL DEFAULT 'PENDING',
    insights_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (module_id, path)
);

CREATE TABLE IF NOT EXISTS sofia_document_pipeline_events (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    document_id BIGINT NOT NULL REFERENCES sofia_documents(id) ON DELETE CASCADE,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS sofia_knowledge_artifacts (
    document_id BIGINT PRIMARY KEY REFERENCES sofia_documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    keywords_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    entities_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    concepts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    relations_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    questions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    quality DOUBLE PRECISION NOT NULL DEFAULT 0,
    ocr_quality DOUBLE PRECISION,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sofia_document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES sofia_documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    ordinal INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'READY',
    UNIQUE (document_id, version_number, ordinal)
);

CREATE TABLE IF NOT EXISTS sofia_processing_jobs (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    source_id BIGINT REFERENCES sofia_sources(id),
    document_id BIGINT REFERENCES sofia_documents(id),
    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS sofia_processing_errors (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    source_id BIGINT REFERENCES sofia_sources(id),
    document_id BIGINT REFERENCES sofia_documents(id),
    stage TEXT NOT NULL,
    error_type TEXT NOT NULL,
    message TEXT NOT NULL,
    retryable BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sofia_retrieval_tests (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    document_id BIGINT REFERENCES sofia_documents(id),
    source_id BIGINT REFERENCES sofia_sources(id),
    title_ok BOOLEAN NOT NULL DEFAULT FALSE,
    semantic_ok BOOLEAN NOT NULL DEFAULT FALSE,
    module_ok BOOLEAN NOT NULL DEFAULT FALSE,
    citation_ok BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sofia_expansion_cycles (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    topics_claimed INTEGER NOT NULL DEFAULT 0,
    topics_completed INTEGER NOT NULL DEFAULT 0,
    pages_discovered INTEGER NOT NULL DEFAULT 0,
    pages_new INTEGER NOT NULL DEFAULT 0,
    pages_updated INTEGER NOT NULL DEFAULT 0,
    duplicates_ignored INTEGER NOT NULL DEFAULT 0,
    errors INTEGER NOT NULL DEFAULT 0,
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Derived local neural vectors. The runtime compatibility adapter stores the
-- same contract as semantic_embeddings inside the isolated sofia_runtime schema.
CREATE TABLE IF NOT EXISTS sofia_semantic_embeddings (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    source_hash TEXT NOT NULL,
    model TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    vector_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (module_id, source_path, ordinal, source_hash, model)
);

CREATE INDEX IF NOT EXISTS idx_sofia_topics_priority ON sofia_search_topics (module_id, priority DESC, last_searched_at DESC);
CREATE INDEX IF NOT EXISTS idx_sofia_queue_due ON sofia_expansion_queue (state, available_at, priority DESC);
CREATE INDEX IF NOT EXISTS idx_sofia_sources_status ON sofia_sources (module_id, status);
CREATE INDEX IF NOT EXISTS idx_sofia_documents_status ON sofia_documents (module_id, status);
CREATE INDEX IF NOT EXISTS idx_sofia_processing_errors ON sofia_processing_errors (module_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sofia_pipeline_events_document ON sofia_document_pipeline_events (document_id, id);
CREATE INDEX IF NOT EXISTS idx_sofia_artifacts_concepts ON sofia_knowledge_artifacts (document_id, version_number);
CREATE INDEX IF NOT EXISTS idx_sofia_semantic_embeddings_module ON sofia_semantic_embeddings (module_id, model);
