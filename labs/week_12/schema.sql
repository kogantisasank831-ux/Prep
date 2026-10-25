-- Bootstrap-only, versioned additive schema for the isolated synthetic lab.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS week12_schema (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    version text NOT NULL
);
INSERT INTO week12_schema(singleton, version) VALUES (true, 'week12/1')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS week12_documents (
    tenant_id text NOT NULL,
    document_id text NOT NULL,
    document_version text NOT NULL,
    source_digest text NOT NULL CHECK (source_digest ~ '^[a-f0-9]{64}$'),
    state text NOT NULL CHECK (state IN ('approved', 'quarantined')),
    readers text[] NOT NULL CHECK (cardinality(readers) <= 32),
    bindings jsonb NOT NULL CHECK (jsonb_typeof(bindings) = 'object'),
    PRIMARY KEY (tenant_id, document_id, document_version)
);
CREATE TABLE IF NOT EXISTS week12_chunks (
    tenant_id text NOT NULL,
    document_id text NOT NULL,
    document_version text NOT NULL,
    chunk_id text NOT NULL,
    representation jsonb NOT NULL
        CHECK (jsonb_typeof(representation) = 'object'
               AND octet_length(representation::text) <= 32768),
    embedding vector(32) NOT NULL,
    embedding_contract text NOT NULL CHECK (embedding_contract = 'token-hash32-l2/v1'),
    PRIMARY KEY (tenant_id, chunk_id),
    FOREIGN KEY (tenant_id, document_id, document_version)
        REFERENCES week12_documents(tenant_id, document_id, document_version)
);
-- Exact eligible-set vector scans are intentional. No ANN index is created.
REVOKE ALL ON week12_schema, week12_documents, week12_chunks FROM PUBLIC;
