---
layout: "week"
status: "approved"
version: "1.0.1"
last_reviewed: "2026-11-13"
header_context: "Interview cheat sheets"
back_label: "Cheat sheets"
back_url: "/cheat-sheets/"
toc_heading: "Cheat-sheet sections"
pagination_label: "Cheat sheets hub"
pagination_url: "/cheat-sheets/"
title: "Document ingestion, chunking, and indexing interview cheat sheet"
description: "Offline RAG ingestion, parsing, provenance, chunking, idempotency, incremental updates, deletions, and index operations."
summary: "Revise source contracts, canonical documents, parsing quality, provenance, chunking strategies, deterministic IDs, backfills, and deletion correctness."
permalink: "/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 3 · Ingestion and indexing"
current_label: "Revision guide"
alternate_label: "Cheat sheets hub"
alternate_url: "/cheat-sheets/"
---
> **Batch 3 source:** This page integrates the prepared revision artifact into the Prep site. It is separate from the Week 1–30 learning assessments.

**Target roles:** RAG Engineer, AI Engineer, Data/ML Engineer, Senior/Lead Data Scientist  
**Use:** design and debug the offline side of a retrieval system  
**Interview rule:** parsing success is not ingestion correctness. Preserve structure, provenance, permissions, versions, and deletion semantics.

## 1. Thirty-second revision

- The ingestion pipeline converts sources into trustworthy, retrievable, versioned chunks—not merely extracted text.
- Distinguish born-digital documents from scanned/image documents; OCR is not required for every PDF and is imperfect when required.
- Preserve headings, tables, lists, page/section location, captions, and source metadata whenever they affect retrieval or citation.
- Chunk boundaries should follow semantic/document structure and model token limits. There is no universal best chunk size or overlap.
- Small chunks improve retrieval precision but can lose context; large chunks preserve context but dilute matches and consume prompt budget.
- Parent-child retrieval searches small child chunks and returns a larger parent/section for generation.
- Deterministic document/chunk IDs, hashes, and version fields make ingestion idempotent and deletions/audits possible.
- Apply access-control metadata before indexing and enforce it again at retrieval. Never infer permissions from document text.
- Re-embedding is a versioned migration. Dual-write/build, validate, switch an alias, and retain rollback rather than overwriting blindly.
- Measure extraction coverage, OCR/table quality, duplicates, chunk-size distribution, indexing failures, freshness, deletion lag, and retrieval impact.

## 2. Offline ingestion architecture

A production ingestion flow commonly has these stages:

1. discover a source item and its permissions;
2. acquire bytes through an authorized connector;
3. verify type, size, malware/policy, and immutable source identity;
4. parse native structure or run OCR/layout analysis;
5. normalize cautiously while preserving the original artifact;
6. produce canonical elements and metadata;
7. deduplicate and version the document;
8. chunk using a selected strategy;
9. enrich chunks with headings, parent context, and provenance;
10. generate embeddings in bounded batches;
11. write lexical/vector indexes transactionally or with recoverable state;
12. validate counts, permissions, retrieval smoke cases, and freshness;
13. publish the new index/version;
14. handle updates, revocations, and deletions.

Keep source acquisition, parsing, chunking, embedding, and indexing separable so each stage can be replayed and evaluated.

## 3. Source inventory and contracts

Before selecting tools, record:

- source systems and owners;
- formats, size/page distributions, languages, and scan percentage;
- tables, forms, equations, images, handwriting, code, and attachments;
- update/delete frequency and event mechanism;
- authoritative document/version identifier;
- permission model and tenant boundary;
- retention, residency, privacy, and audit requirements;
- freshness and deletion SLOs;
- volume, throughput, and cost envelope.

Connectors should use least-privilege identities and checkpoint cursors. A periodic full reconciliation is still valuable because event feeds can drop or reorder changes.

## 4. Parsing: text is not enough

### Born-digital documents

Text, reading order, fonts, coordinates, bookmarks, and table structure may be available directly. Prefer native extraction when it is accurate; unnecessary OCR adds cost and errors.

### Scanned documents

Require OCR plus layout/rotation handling. Track OCR confidence and page-level failures. Low-confidence content may need review or exclusion from high-risk answers.

### Mixed/hybrid documents

Some pages have selectable text while others are scans. Detect at page/region level rather than assuming one method for the entire file.

### Format-specific structure

- PDF: visual layout is primary; logical reading order may be missing.
- DOCX/HTML/Markdown: headings and lists are usually explicit.
- PPTX: slide, title, notes, diagrams, and reading order matter.
- XLSX/CSV: rows, sheets, headers, formulas, units, and merged cells matter.
- Email: headers, body, thread, and attachments need separate provenance.
- Images: OCR alone may miss charts, diagrams, and spatial relationships.

## 5. Canonical document model

Define a stable internal representation instead of passing tool-specific objects across the system.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ElementType(StrEnum):
    TITLE = "title"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE = "table"
    CODE = "code"
    IMAGE_CAPTION = "image_caption"


@dataclass(frozen=True, slots=True)
class DocumentElement:
    document_id: str
    version_id: str
    element_id: str
    element_type: ElementType
    text: str
    page_number: int | None
    section_path: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SourceDocument:
    document_id: str
    version_id: str
    source_uri: str
    effective_at: datetime
    acl_ids: tuple[str, ...]
    elements: tuple[DocumentElement, ...]
```

The schema should also support source checksum, parser/version, language, creation/update times, content type, tenant, classification, and lineage as needed.

## 6. Provenance and citation coordinates

Every chunk should be traceable to the immutable source version and location:

- source system and document ID;
- document version/checksum;
- page, slide, sheet/row, section path, or element IDs;
- parser/OCR version;
- ingestion timestamp and effective validity;
- access-control identifiers;
- parent/neighbor relationships.

Do not cite a mutable URL alone. If the source changes, the answer audit must still identify what version supported it.

## 7. Cleaning and normalization

Safe candidates:

- normalize Unicode consistently;
- remove repeated headers/footers after detection;
- repair deterministic line-break/hyphenation artifacts;
- standardize whitespace while preserving tables/code;
- exclude navigation boilerplate when verified;
- preserve original and normalized text separately if auditability matters.

Avoid blind lowercasing, punctuation removal, stop-word deletion, or number normalization. These can destroy IDs, units, negation, code, formulas, and names.

## 8. Deduplication

### Exact duplicates

Hash canonical bytes or normalized content. Keep source mappings even if content storage is deduplicated.

### Near duplicates

Use MinHash/LSH, shingles, similarity, or structural comparison to find copied templates and document revisions. A similarity threshold is a policy requiring review.

### Version versus duplicate

Two documents with similar text may have different permissions, effective dates, jurisdiction, or approval status. Never merge away these semantics.

Deduplication should prevent duplicate retrieval without losing ownership and lineage.

## 9. Chunking goals

A chunk should be:

- small enough for precise retrieval;
- large enough to answer a useful unit of meaning;
- within embedding/reranker limits after any prefix/context;
- attributable to a source location;
- safe to filter by tenant/ACL;
- reconstructable with parent/neighbor context.

Chunking is an experimental variable, not a preprocessing constant.

## 10. Chunking strategies

| Strategy | Method | Good for | Main risk |
|---|---|---|---|
| Fixed tokens/characters | Split every $n$ units | Simple baseline | Breaks sentences/tables/sections |
| Recursive separators | Try section, paragraph, sentence, then token boundaries | General text | Still ignores deeper layout semantics |
| Sentence grouping | Pack whole sentences to a budget | Prose | Tables/code and abbreviations |
| Structural/by-title | Respect headings/elements | Manuals, policies, reports | Parser heading errors and uneven sizes |
| Semantic | Split when adjacent semantic similarity changes | Topic shifts | Extra model cost and unstable thresholds |
| Parent-child | Search child; return parent | Precise search + sufficient context | More storage/mapping and parent dilution |
| Sliding window | Overlapping windows | Local continuity | Duplicates and larger index |
| Table-aware | Keep headers/cells/rows meaningful | Financial/technical tables | Large tables and cross-row questions |
| Code-aware | Split by symbols/classes/functions | Source code | Cross-file dependencies |

## 11. Chunk size and overlap

There is no universal `500 tokens with 50 overlap` rule.

### Smaller chunks

- higher topical precision;
- more vectors and index/storage cost;
- less surrounding evidence;
- higher risk of orphaned references/pronouns.

### Larger chunks

- preserve context and tables/sections;
- lower retrieval specificity;
- consume more reranker/generator tokens;
- may exceed embedding limits or be truncated.

### Overlap

Overlap protects boundary-spanning facts but creates near duplicates, repeated context, larger indexes, and misleading citation counts. Start with structural boundaries; add measured overlap only when boundary errors justify it.

Evaluate several sizes/strategies on question-to-evidence labels and end-to-end answers.

## 12. Token-aware chunking

Character count is not token count. Tokenization varies by model, language, whitespace, and code.

The effective input may include:

$$
\text{heading prefix}+\text{document context}+\text{chunk text}
$$

Reserve model special tokens and respect the shortest limit among embedding and reranker stages. Record token-count distributions and truncation rate.

## 13. Parent-child and neighbor expansion

### Parent-child

Index a small child chunk. On retrieval, map it to a larger parent section for generation. Deduplicate when several child hits share a parent.

### Neighbor expansion

Retrieve the matched chunk plus one or more adjacent chunks. Use section/document boundaries so expansion does not cross unrelated content.

### Trade-off

Both improve context, but returning too much parent/neighbor text can undo precise retrieval. Measure answer support per token.

## 14. Contextual and late chunking awareness

### Contextual chunking

Prepend a short document/section-specific context to each chunk before embedding and/or lexical indexing, for example the document title and section purpose. This can resolve ambiguous isolated chunks but adds generation/indexing cost and can inject incorrect summaries.

### Late chunking

Encode a longer document context first and pool token representations into chunk embeddings afterward, where supported. This aims to retain broader context in each chunk representation but depends on model/context limits and implementation.

Neither technique removes the need for labeled retrieval evaluation.

## 15. Tables, images, and multimodal content

### Tables

Options include:

- preserve as HTML/Markdown plus caption/header;
- create row-group chunks repeating headers;
- produce a faithful textual description for semantic search;
- store structured cells for deterministic SQL/aggregation.

Do not expect a language model to perform reliable arithmetic over a lossy table serialization when a database/calculator is available.

### Images and diagrams

Store OCR text, captions, nearby text, page coordinates, and image references. Use multimodal embeddings or vision models only when diagrams/images are genuinely needed and evaluated.

## 16. Deterministic IDs and idempotency

A chunk ID can derive from document identity, version, strategy version, and stable position/content:

```python
from __future__ import annotations

from hashlib import sha256


def make_chunk_id(
    *,
    document_id: str,
    version_id: str,
    chunker_version: str,
    ordinal: int,
    text: str,
) -> str:
    if ordinal < 0:
        raise ValueError("ordinal cannot be negative")
    canonical = "\x1f".join(
        [document_id, version_id, chunker_version, str(ordinal), text.strip()]
    )
    return sha256(canonical.encode("utf-8")).hexdigest()
```

Idempotency also requires unique constraints/upserts, checkpointed job state, retry-safe writes, and reconciliation.

## 17. Embedding and indexing jobs

Production controls:

- bounded batches by token count and item count;
- provider/GPU rate limits and backpressure;
- per-item status and retry classification;
- dead-letter/quarantine for irrecoverable parsing/content failures;
- model/tokenizer/prefix/dimension/normalization version in every record;
- validation before publishing an index;
- resumability without duplicating vectors;
- cost, latency, throughput, and failure telemetry.

Never mark a document searchable until required chunks, permissions, and indexes reach a consistent publish state.

## 18. Incremental updates and deletions

### Create/update

Use source change events plus periodic reconciliation. Compare version/checksum; parse and index a new immutable version; atomically switch visibility where possible.

### Permission change

Treat as a high-priority security update. Update filters/caches and test revocation latency even if content is unchanged.

### Deletion

Delete or tombstone from:

- document/chunk stores;
- lexical and vector indexes;
- embedding/cache layers;
- generated summaries/graph projections when applicable;
- replicas/backups according to retention policy.

Verify deletion by document ID and prevent stale jobs from resurrecting removed content.

## 19. Re-embedding and index migration

Changing the embedding model, dimension, prefix, normalization, chunking, or distance metric usually creates a new incompatible index version.

Safe migration:

1. pin the new configuration and build a separate index;
2. replay a frozen corpus snapshot plus queued changes;
3. compare counts, filters, exact/ANN recall, labeled retrieval, and latency;
4. shadow or canary query traffic;
5. switch a logical alias/version pointer;
6. monitor and retain rollback;
7. retire the old index only after the retention window.

## 20. Multi-tenancy and point-in-time correctness

### Tenant isolation

- tenant/ACL identifiers must come from an authoritative system;
- enforce eligibility before content enters model context;
- scope cache keys and logs;
- test malicious IDs, empty permissions, and shared documents;
- avoid a shared namespace if the engine cannot prove filter isolation.

### Point-in-time correctness

For policies/contracts, queries may require the document version effective at a specific time. Store validity intervals and filter accordingly. “Latest indexed” is not always legally or analytically correct.

## 21. Parsing and ingestion tool map

| Tool | Typical role | What to validate |
|---|---|---|
| Docling | Layout-aware conversion, elements, tables, native chunkers | Format coverage, structure/table quality, resource cost |
| PyMuPDF | PDF extraction, coordinates, rendering, chunking capabilities | Reading order, scans, fonts/encoding, license fit |
| Unstructured | Format partitioning into typed elements and chunking | Strategy/version behavior and external dependencies |
| pypdf | Lightweight PDF text/metadata operations | Not a universal layout/OCR solution |
| Apache Tika | Broad file-type detection and text/metadata extraction | Server/runtime footprint and structure fidelity |
| Tesseract/PaddleOCR/cloud OCR | OCR for image/scanned content | Language, handwriting/layout, confidence, privacy, cost |
| MarkItDown/format converters | Convert supported files to text/Markdown | Loss of structure, images, tables, provenance |

Use a representative format test corpus. No single parser wins for every source.

## 22. Ingestion quality metrics

Track by source/format/language:

- discovery-to-searchable freshness;
- parse success and page/element coverage;
- OCR confidence and manual spot-check accuracy;
- table/heading/list preservation;
- empty, tiny, huge, and truncated chunk rates;
- chunk token-size distribution and overlap duplication;
- exact/near duplicate rate;
- embedding/index success and retry counts;
- source-to-index count reconciliation;
- permission/revocation/deletion lag;
- downstream Recall@K and citation-location correctness.

Operational success alone does not prove extracted content is useful.

## 23. Common failure modes

| Symptom | Likely cause | Investigation |
|---|---|---|
| Garbled text | Bad encoding/font map or OCR | Compare rendered page, native extraction, OCR path |
| Wrong answer from table | Reading order/header lost | Inspect element tree and table serialization |
| Repeated retrieval | Headers/footers/overlap/versions | Dedup by canonical/parent IDs |
| Missing policy section | Parser or chunk truncation | Page coverage, element counts, token limits |
| Old document still cited | Incomplete update/deletion/cache invalidation | Trace document/version across all stores |
| Cross-tenant chunk | Wrong ACL ingestion/filter | Reconcile permissions and quarantine index |
| Index count drifts | Partial retry/non-idempotent writes | Unique IDs, job ledger, source reconciliation |
| New model performs worse | Unmigrated prefix/normalization/chunks | Compare full versioned pipeline |

## 24. Common interview traps

- Assuming every PDF has a correct text layer.
- Treating OCR output as ground truth.
- Choosing chunk size by convention without retrieval labels.
- Adding overlap without deduplication and prompt-budget analysis.
- Storing only text and losing source/page/permissions.
- Overwriting vectors during a model migration with no rollback.
- Deleting the source row while leaving vectors, cache, graph, or summaries.
- Trusting connector events without periodic reconciliation.
- Claiming parser support means acceptable table/reading-order quality.

## 25. Rapid interview questions and answers

1. **Why preserve layout?** Reading order, headings, tables, and captions carry meaning and enable accurate retrieval/citation.
2. **Why not OCR every PDF?** Native extraction is faster and often more accurate for born-digital text; OCR adds errors and cost.
3. **Best chunk size?** There is no universal value; tune against model limits and labeled retrieval/end-to-end tasks.
4. **Why parent-child retrieval?** Search precise child chunks while returning sufficient parent context.
5. **Why deterministic chunk IDs?** Idempotent retries, lineage, updates, deletion, and auditability.
6. **What changes require re-embedding?** Model/tokenizer/prefix/normalization/dimension and usually chunk-text changes.
7. **How handle permissions?** Ingest authoritative ACL metadata and enforce eligibility inside retrieval, with revocation tests.
8. **How remove stale content?** Version/tombstone and delete across every derived store/cache, then verify by ID.
9. **How test a parser?** Representative golden documents with expected text, elements, tables, locations, and failure cases.
10. **What makes ingestion production-ready?** Idempotency, observability, reconciliation, versioned artifacts, access control, deletion, and rollback.

## 26. Lead-level design case

**Question:** Ingest one million mixed PDFs, Office files, and emails from enterprise repositories with four-hour freshness and immediate permission revocation.

**Strong answer structure:**

1. Inventory formats, scan rate, source APIs/events, permissions, volumes, data classes, and freshness/deletion SLOs.
2. Use least-privilege connectors, immutable source/version IDs, checkpoints, and periodic reconciliation.
3. Route by detected type/page: native parsing first, OCR/layout only where required; quarantine unsafe/corrupt files.
4. Normalize into a canonical element schema preserving pages, sections, tables, attachments, lineage, and ACLs.
5. Evaluate structural, token-aware, table-aware, and parent-child chunking on labeled questions.
6. Use deterministic IDs and job ledgers; embed/index in bounded retry-safe batches.
7. Publish versioned indexes only after count, permission, retrieval, and citation smoke checks.
8. Handle revocation as a priority control path; invalidate caches and verify denial before content reaches prompts.
9. Support tombstones and deletion across lexical/vector/object/cache/derived stores; reconcile stale workers.
10. Monitor format-level quality, freshness, permission/deletion lag, cost, and retrieval impact; canary parser/chunker/model changes.

## 27. Final revision checklist

- [ ] I can design an ingestion pipeline from connector to published index.
- [ ] I can distinguish native extraction, OCR, layout parsing, and multimodal processing.
- [ ] I can define a canonical element/chunk schema with provenance and ACLs.
- [ ] I can compare fixed, recursive, structural, semantic, parent-child, and table-aware chunking.
- [ ] I can explain size/overlap trade-offs using token budgets and evaluation.
- [ ] I can design deterministic IDs, retries, reconciliation, update, and deletion behavior.
- [ ] I can plan a safe re-embedding/index migration.
- [ ] I can measure extraction quality, freshness, and downstream retrieval impact.
- [ ] I can test tenant isolation and point-in-time correctness.

## Primary references

- [Docling chunking documentation](https://github.com/docling-project/docling/blob/main/docs/concepts/chunking.md)
- [PyMuPDF chunking documentation](https://pymupdf.readthedocs.io/en/latest/chunking/index.html)
- [Unstructured partitioning documentation](https://docs.unstructured.io/open-source/core-functionality/partitioning)
- [Unstructured chunking documentation](https://docs.unstructured.io/open-source/core-functionality/chunking)
- [OWASP RAG Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)
