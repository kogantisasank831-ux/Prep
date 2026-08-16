---
layout: week
permalink: /weeks/week-06/beginner/
title: "Document parsing and chunking: a beginner's introduction"
description: Learn how to turn procurement files into bounded, traceable retrieval units without breaking the evidence an analyst needs.
summary: Continue the P-101 through P-105 procurement collection from raw document blocks to metadata, chunks, retrieval candidates, and an honest chunking comparison.
kicker_primary: Document parsing and chunking
kicker_secondary: Beginner context
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-06/
---

## A search result is only as useful as the text unit behind it

Week 5 searched one already-short document at a time. Real procurement files are not always that kind. A purchase agreement can contain a title, headings, tables, a scanned signature page, an amendment, and a payment exception far from the product line it qualifies.

Continue the synthetic collection. P-101 through P-104 remain short source records. We now add P-105:

```text
P-105 | Atlas Metals framework agreement

Section 1 — Scope
Atlas Metals supplies copper wire to the Northwind plant.

Section 2 — Delivery and acceptance
The receiving team records incoming-material inspection before acceptance.

Schedule A — line items
| line | product      | quantity | unit price |
| 1    | copper wire  | 1,000 kg | USD 12.00  |

Section 3 — Invoicing
Invoice terms are Net 30 after inspection approval.
The payment condition in this section controls Schedule A.
```

An analyst asks: **“What payment condition applies to the 1,000 kg copper-wire line?”** The useful evidence is not just the table, and not just the invoicing paragraph. A good retrieval unit should preserve enough nearby structure for a reviewer to see that Section 3 controls Schedule A.

This is the job of **document parsing and chunking**:

```text
untrusted file or text
        |
        v
parsed blocks + metadata + source locations
        |
        v
chunking policy creates bounded retrieval units
        |
        v
local embedding/retrieval system ranks units
        |
        v
reviewer reads traceable source evidence
```

Chunking does not make a document true, repair an OCR error, or generate an answer. It chooses the units that a retrieval system is allowed to compare. A bad boundary can separate `after inspection approval` from `Net 30`, merge two suppliers, duplicate evidence, or hide a table header. Treat parsed text, metadata, chunks, vectors, and model output as untrusted data until the appropriate deterministic checks and review occur.

**Checkpoint.** If a retrieved chunk contains “Net 30” but not “after inspection approval,” can a caller state the complete payment condition? No. The returned unit may be incomplete evidence. The reviewer must follow its source location or parent document and apply the declared evidence policy.

## Parsing comes before chunking

A **parser** turns an input representation into a usable internal representation. For a plain-text note, that may be simple decoding and line handling. For a PDF, it may mean extracting positioned text, recognising headings, reconstructing tables, or sending a scanned page through OCR. The parser’s output is not automatically reliable just because it is text.

Use a small, explicit parsed representation rather than a naked string:

| Field | Why it matters |
| --- | --- |
| document ID and version | identifies the immutable source being searched |
| tenant/owner | enables authorization before retrieval |
| title and document type | supports filtering and review context |
| block kind | distinguishes paragraph, heading, table, and page text |
| source location | lets a reviewer return to the page, section, or row |
| extracted text | is the material being chunked, but remains untrusted |
| content digest | identifies the parsed content used for an index build |

Metadata is not decorative. `supplier=Atlas Metals`, `document_type=framework_agreement`, `effective_date`, `tenant_id`, and `source_version` can keep a result interpretable and can support deterministic authorization or filtering. Extract only fields your parser can support and retain the original source span. Do not ask a language model to silently invent metadata for a file whose header is unreadable.

### Tables and PDFs are not ordinary paragraphs

A visually simple PDF table can extract as a scrambled stream: headers may appear after values, cells can interleave across columns, and a row can continue on the next page. A scanned PDF may contain no text layer at all, so OCR can confuse `0` with `O`, lose a decimal point, or put a heading into a body sentence. Multi-column layouts may extract in the wrong reading order. Headers, footers, page numbers, and signature blocks can create misleading repeated text.

For P-105, the meaning of `USD 12.00` depends on its column header and row. Converting the table to this flattened sentence loses useful structure:

```text
1 copper wire 1,000 kg USD 12.00 line product quantity unit price
```

Prefer a parser output that keeps a table as a table block, with row/column location and a deliberate text representation for retrieval. A retrieval-friendly rendering might be:

```text
Schedule A, row 1: product=copper wire; quantity=1,000 kg; unit price=USD 12.00
```

That rendering is an application policy, not a claim that every table parser is correct. Preserve the original page/table coordinates so a reviewer can compare it with the source. If a parser cannot establish row structure, mark that limitation and route the document for review rather than pretending the reconstructed fields are authoritative.

**Checkpoint.** Does OCR output “USD 12.00” prove the PDF showed that price? No. OCR is another untrusted transformation. The source image/page and the parser/OCR version remain part of evidence provenance.

## A chunk is a retrieval unit, not a universal text size

A **chunk** is one bounded piece of parsed source text stored and retrieved as a unit. Chunking decides four related things:

- what text becomes one vector or searchable record;
- what metadata and source location travel with it;
- what nearby context is preserved or duplicated; and
- what a reviewer can see after a result is returned.

The best chunk size is not a magic value such as 500 tokens. It depends on document structure, retrieval unit, context budget, and evaluation.

| Decision input | Question |
| --- | --- |
| Document structure | Are clauses, headings, tables, and amendments meaningful boundaries? |
| Retrieval unit | Does the query need one sentence, one clause, one row, or a section plus its heading? |
| Context budget | How many retrieved units can a later reviewer or bounded consumer inspect together? |
| Model behavior | What input length and language/document format was the embedding model evaluated for? |
| Evaluation evidence | Which policy finds complete supporting evidence with acceptable noise? |
| Operations | How many vectors, bytes, rebuild time, and duplicate text can the system afford? |

For this beginner lesson, a chunk is measured in characters to keep the code local and dependency-free. Real systems often count tokenizer-specific tokens, and their policy must record which tokenizer/version produced that count. Characters are not tokens, and a 300-character limit does not mean 300 English words or 300 model tokens.

## Strategy 1: fixed-size chunks

**Fixed-size chunking** splits text every fixed number of characters or tokens. It is easy to implement, predictable, and useful as a baseline. It does not understand words, sentences, clauses, or tables.

```text
Section 3 — Invoicing. Invoice terms are Net 30 after inspection approval.
                         ^ fixed boundary might land here
```

If the boundary cuts through `inspection approval`, one chunk may contain the rate while the next contains the condition. A query can retrieve either incomplete half. Fixed chunks can also split a table row or attach an unrelated following section to a clause.

The virtue of a baseline is honesty: it reveals how much quality comes from simple size rather than sophisticated heuristics. Do not call it unsafe in every setting; a short, regular corpus with broad queries may work acceptably. Measure it against the questions users actually ask.

```python
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from statistics import mean
from typing import Iterable


MAX_PARSED_DOCUMENT_CHARS = 4_000


@dataclass(frozen=True)
class ParsedBlock:
    kind: str
    location: str
    text: str


@dataclass(frozen=True)
class ParsedDocument:
    tenant_id: str
    document_id: str
    version: str
    title: str
    metadata: tuple[tuple[str, str], ...]
    blocks: tuple[ParsedBlock, ...]


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    version: str
    text: str
    locations: tuple[str, ...]
    metadata: tuple[tuple[str, str], ...]
    parent_id: str | None = None


def digest_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def validated_text(document: ParsedDocument) -> str:
    text = "\n".join(block.text.strip() for block in document.blocks if block.text.strip())
    if not text or len(text) > MAX_PARSED_DOCUMENT_CHARS:
        raise ValueError("parsed document text must be non-empty and bounded")
    return text


def parsed_content_digest(document: ParsedDocument) -> str:
    return digest_text(validated_text(document))


def fixed_size_chunks(document: ParsedDocument, *, width: int) -> tuple[Chunk, ...]:
    if width <= 0:
        raise ValueError("width must be positive")
    text = validated_text(document)
    locations = tuple(block.location for block in document.blocks)
    return tuple(
        Chunk(
            chunk_id=f"{document.document_id}:{document.version}:fixed:{offset}",
            document_id=document.document_id,
            version=document.version,
            text=text[offset : offset + width],
            locations=locations,
            metadata=document.metadata,
        )
        for offset in range(0, len(text), width)
    )
```

The code intentionally carries the source locations even though a fixed chunk can span several blocks. A production parser would retain more precise character/page offsets. It should also reject malformed source identity and enforce tenant/object authorization outside this pure chunking function.

**Checkpoint.** Why is fixed-size chunking still useful? It provides a simple, repeatable baseline. If a more elaborate policy cannot beat it on held-out retrieval and support-quality measures, its extra complexity has not earned its place.

## Strategy 2: overlap protects a boundary at a cost

**Overlapping fixed-size chunking** repeats the final part of one chunk at the start of the next. The overlap gives a clause straddling a boundary another chance to appear intact.

```text
chunk 1: [................ Net 30 after inspect]
chunk 2: [after inspection approval.............]
                 ^ repeated overlap
```

Overlap can help P-105’s payment clause, but it is not free. It increases chunk count, vector storage, indexing time, duplicate retrieval candidates, and the chance that a downstream consumer sees the same evidence twice. Too much overlap can produce a high apparent Recall@k merely because the same supporting phrase has many near-duplicate copies.

```python
def overlapping_fixed_chunks(
    document: ParsedDocument,
    *,
    width: int,
    overlap: int,
) -> tuple[Chunk, ...]:
    if width <= 0 or not 0 <= overlap < width:
        raise ValueError("require positive width and overlap smaller than width")
    text = validated_text(document)
    locations = tuple(block.location for block in document.blocks)
    stride = width - overlap
    starts = range(0, len(text), stride)
    return tuple(
        Chunk(
            chunk_id=f"{document.document_id}:{document.version}:overlap:{offset}",
            document_id=document.document_id,
            version=document.version,
            text=text[offset : offset + width],
            locations=locations,
            metadata=document.metadata,
        )
        for offset in starts
        if text[offset : offset + width]
    )
```

The overlap is a policy parameter that must be recorded with the index. Changing it changes the corpus of chunks and therefore changes retrieval, storage, and evaluation. Do not silently compare one build with 20% overlap against another with no overlap and attribute every difference to the embedding model.

## Strategy 3: sentence-based chunks protect readable units

**Sentence-based chunking** first identifies sentence boundaries, then groups whole sentences until a target size is reached. It is often easier for a reviewer to read and less likely to cut a payment condition in the middle.

It has limits. Sentence detection is language- and format-dependent. A period can occur in `Inc.`, a decimal, a product code, a bullet, or an abbreviation. Tables and headings are not ordinary sentences. A very long sentence can still exceed the target, and a short sentence can rely on a heading or preceding exception.

The compact splitter below is for controlled synthetic prose only. It is not a general natural-language parser and deliberately treats table blocks separately later.

```python
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def sentence_based_chunks(
    document: ParsedDocument,
    *,
    target_width: int,
) -> tuple[Chunk, ...]:
    if target_width <= 0:
        raise ValueError("target width must be positive")
    chunks: list[Chunk] = []
    current_sentences: list[str] = []
    current_locations: list[str] = []
    for block in document.blocks:
        if block.kind != "paragraph":
            continue
        for sentence in SENTENCE_END.split(block.text.strip()):
            candidate = " ".join((*current_sentences, sentence)).strip()
            if current_sentences and len(candidate) > target_width:
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.document_id}:{document.version}:sentence:{len(chunks)}",
                        document_id=document.document_id,
                        version=document.version,
                        text=" ".join(current_sentences),
                        locations=tuple(current_locations),
                        metadata=document.metadata,
                    )
                )
                current_sentences = [sentence]
                current_locations = [block.location]
            else:
                current_sentences.append(sentence)
                current_locations.append(block.location)
    if current_sentences:
        chunks.append(
            Chunk(
                chunk_id=f"{document.document_id}:{document.version}:sentence:{len(chunks)}",
                document_id=document.document_id,
                version=document.version,
                text=" ".join(current_sentences),
                locations=tuple(current_locations),
                metadata=document.metadata,
            )
        )
    return tuple(chunks)
```

**Checkpoint.** Does preserving a sentence guarantee that the chunk contains enough evidence? No. “The payment condition in this section controls Schedule A” depends on the section and table context. Sentence boundaries are more readable than raw character boundaries, not universally sufficient.

## Strategy 4: structure-aware chunks preserve document meaning

A **structure-aware** policy uses parser labels such as heading, paragraph, list, and table. It can attach a heading to its following paragraphs, keep each table row with its header, and make a section boundary visible. For P-105, one useful policy creates a chunk for `Section 3 — Invoicing` plus both invoicing paragraphs, while representing Schedule A as a separate, row-aware table chunk.

```text
chunk: Section 3 — Invoicing
       Invoice terms are Net 30 after inspection approval.
       The payment condition in this section controls Schedule A.

chunk: Schedule A, row 1
       product=copper wire; quantity=1,000 kg; unit price=USD 12.00
```

This preserves interpretable units, but it relies on parser quality. A PDF parser that mistakes a footer for a heading or loses a table row can make a structure-aware policy worse than a simple baseline. Structure-aware does not mean correct; it means the policy uses declared structure and must be evaluated against parsed-document reality.

```python
def structure_aware_chunks(document: ParsedDocument) -> tuple[Chunk, ...]:
    chunks: list[Chunk] = []
    active_heading: ParsedBlock | None = None
    for block in document.blocks:
        if block.kind == "heading":
            active_heading = block
            continue
        prefix = f"{active_heading.text}\n" if active_heading else ""
        if block.kind in {"paragraph", "table_row"}:
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_id}:{document.version}:structure:{len(chunks)}",
                    document_id=document.document_id,
                    version=document.version,
                    text=f"{prefix}{block.text}".strip(),
                    locations=tuple(
                        location
                        for location in (
                            active_heading.location if active_heading else None,
                            block.location,
                        )
                        if location is not None
                    ),
                    metadata=document.metadata,
                )
            )
    return tuple(chunks)
```

The function is deliberately small: it demonstrates heading inheritance and table-row preservation but does not claim to parse arbitrary PDF structure. In a real system, retain table ID, row index, header provenance, page coordinates, and parser confidence/status; do not flatten a failed table extraction into reliable-looking prose.

## Semantic chunks and parent-child retrieval are different ideas

**Semantic chunking** uses a similarity signal between neighbouring units to decide whether a topic changed. For example, a policy might keep adjacent sentences together while their local embedding similarity remains high and start a new chunk when it drops below a configured threshold. This can make natural topic groups, but it adds another model dependency, threshold, language/domain sensitivity, and evaluation problem.

Semantic chunking is not “the best strategy” by definition. P-105’s table and the sentence saying it is controlled by Section 3 might be semantically distant even though they are legally related. A threshold can also be unstable across document types. If you use a local embedding model for semantic boundaries, pin its identity, preprocessing, similarity metric, threshold, and source snapshot, then compare it with fixed and structure-aware baselines on the same held-out labels.

**Parent-child retrieval** separates the unit used for matching from the unit shown for context. A small child chunk may match the query precisely; its parent section supplies readable supporting context:

```text
parent: P-105 / Section 3 — Invoicing
  child: "Invoice terms are Net 30 after inspection approval."
  child: "The payment condition in this section controls Schedule A."

query -> match child -> return child plus declared parent context
```

This can improve both focused matching and review context, but it requires a durable parent/child mapping and clear result policy. Do not let a child from one document pull an unrelated parent from another version. Parent context can also add noise or expose more sensitive text, so authorization applies to both child and parent before retrieval and display.

## Compare strategies on one collection without inventing a benchmark

The Week 6 build compares strategies on the **same bounded collection**, not on four hand-picked screenshots. Use P-101 through P-105 plus additional synthetic or appropriately governed documents that contain headings, tables, amendments, repeated boilerplate, and OCR-like defects. Freeze source versions and the local retrieval configuration before comparing policies.

The following compact collection gives the code one structured P-105 document. The `metadata` values are parser output supplied by the controlled fixture; in a real pipeline, record how each was extracted and whether it needs review.

```python
P105 = ParsedDocument(
    tenant_id="northwind-procurement",
    document_id="P-105",
    version="1",
    title="Atlas Metals framework agreement",
    metadata=(
        ("supplier", "Atlas Metals"),
        ("document_type", "framework_agreement"),
    ),
    blocks=(
        ParsedBlock("heading", "p1:section-1", "Section 1 — Scope"),
        ParsedBlock(
            "paragraph",
            "p1:section-1:p1",
            "Atlas Metals supplies copper wire to the Northwind plant.",
        ),
        ParsedBlock("heading", "p1:section-2", "Section 2 — Delivery and acceptance"),
        ParsedBlock(
            "paragraph",
            "p1:section-2:p1",
            "The receiving team records incoming-material inspection before acceptance.",
        ),
        ParsedBlock("heading", "p1:schedule-a", "Schedule A — line items"),
        ParsedBlock(
            "table_row",
            "p1:schedule-a:r1",
            "Schedule A, row 1: product=copper wire; quantity=1,000 kg; unit price=USD 12.00.",
        ),
        ParsedBlock("heading", "p1:section-3", "Section 3 — Invoicing"),
        ParsedBlock(
            "paragraph",
            "p1:section-3:p1",
            "Invoice terms are Net 30 after inspection approval.",
        ),
        ParsedBlock(
            "paragraph",
            "p1:section-3:p2",
            "The payment condition in this section controls Schedule A.",
        ),
    ),
)


def short_document(document_id: str, title: str, text: str) -> ParsedDocument:
    return ParsedDocument(
        tenant_id="northwind-procurement",
        document_id=document_id,
        version="1",
        title=title,
        metadata=(("document_type", "procurement_note"),),
        blocks=(ParsedBlock("paragraph", "p1:body", text),),
    )


COLLECTION = (
    short_document(
        "P-101",
        "Atlas Metals purchase confirmation",
        "Copper wire will ship after incoming-material inspection. "
        "Invoice terms: Net 30 after inspection approval.",
    ),
    short_document(
        "P-102",
        "Beacon Plastics purchase confirmation",
        "Polymer pellets will ship on 2026-09-03. Invoice terms: Net 15 from receipt.",
    ),
    short_document(
        "P-103",
        "Atlas Metals delivery update",
        "The copper-wire shipment is delayed by two days while quality checks finish.",
    ),
    short_document(
        "P-104",
        "Cedar Fasteners payment note",
        "Payment is due after the receiving team signs off on the delivered bolts.",
    ),
    P105,
)


def average_chunk_length(chunks: Iterable[Chunk]) -> float:
    lengths = [len(chunk.text) for chunk in chunks]
    if not lengths:
        raise ValueError("at least one chunk is required")
    return mean(lengths)


STRATEGIES = {
    "fixed": tuple(
        chunk for document in COLLECTION for chunk in fixed_size_chunks(document, width=120)
    ),
    "overlap": tuple(
        chunk
        for document in COLLECTION
        for chunk in overlapping_fixed_chunks(document, width=120, overlap=40)
    ),
    "sentence": tuple(
        chunk
        for document in COLLECTION
        for chunk in sentence_based_chunks(document, target_width=120)
    ),
    "structure": tuple(
        chunk for document in COLLECTION for chunk in structure_aware_chunks(document)
    ),
}

assert all(chunks for chunks in STRATEGIES.values())
assert {
    chunk.document_id for chunks in STRATEGIES.values() for chunk in chunks
} == {"P-101", "P-102", "P-103", "P-104", "P-105"}
assert len({parsed_content_digest(document) for document in COLLECTION}) == 5
```

The assertions check only fixture and contract behavior. They do not claim that one strategy wins. If you run the code, it can report chunk count and average character length; do not present those fixture-specific numbers as a production benchmark.

### What to record for every strategy

| Measure | What to record | Why it matters |
| --- | --- | --- |
| Retrieval quality | labelled relevant chunks in top-k for each held-out query | measures whether evidence is found |
| Chunk count | number of chunks per document and collection | affects vectors, indexing, and duplicates |
| Average chunk length | characters or documented tokenizer tokens | shows the retrieval-unit scale |
| Storage impact | chunk text bytes, metadata bytes, vector dimension/bytes, and index overhead | overlap and smaller chunks increase cost |
| Answer-support quality | whether retrieved source units contain the complete evidence a reviewer needs | avoids treating a partial clause as a complete answer |

“Answer-support quality” is intentionally retrieval-only. Do not generate an answer and call fluent prose a quality measure. For each query, create a rubric such as: *Does the top-k set contain the rate, the inspection-approval condition, and the link from Section 3 to Schedule A, with source locations?* A reviewer can judge support from the returned evidence. If the rubric needs a business interpretation beyond the document, mark it as requiring authorised human review.

### An illustrative evaluation procedure

1. Freeze the document collection, parser version, metadata policy, chunk policy parameters, local embedding model/version, metric, top-k, and authorization filter.
2. Write held-out queries and relevance/support labels before looking at candidate rankings. Include “What payment condition applies to the copper-wire line?”, “Which document says sign-off is required before payment?”, and negative/ambiguous cases.
3. Run every strategy against the same eligible documents. Do not let one strategy see table headers or metadata that another strategy is denied unless that difference is the deliberate independent variable.
4. Record Recall@k and Precision@k for retrieval, chunk count, average length, storage calculation, and the reviewer’s answer-support rubric. Keep raw source text out of general logs.
5. Inspect failures by document type: prose, table, scanned/OCR, amendments, headings, and long sections. Choose a policy only after considering quality, cost, and failure modes together.

This is an evaluation design, not a benchmark result. It supplies no scores because none have been measured here.

**Checkpoint.** If overlap increases Recall@5 on this collection, should it be adopted immediately? Not necessarily. Check duplicate rate, Precision@5, storage/index cost, support completeness, subgroup failures, and whether the gain holds on held-out documents.

## Failure boundaries and safe defaults

Chunking is downstream of parsing and upstream of retrieval. Make failure ownership visible:

```text
unreadable PDF / failed OCR        -> ingestion or parser status; no trusted text claim
malformed table reconstruction     -> preserve source location; review or reject table fields
oversized document                 -> explicit bounded-policy failure; do not silently truncate
unknown heading/layout             -> declared fallback policy and evaluation case
incompatible embedding/index       -> rebuild or reject; do not mix vectors
unauthorised source                -> exclude before candidate retrieval
partial retrieved evidence         -> show provenance; do not claim a complete answer
```

The right fallback depends on risk. A document may be retained with a visible `needs_review` parser status; it should not become a high-confidence chunk merely because an extraction function returned a string. Never drop an invalid row, page, or table silently. Preserve enough safe provenance to investigate without exposing sensitive document contents to every log consumer.

## Choosing chunk size: an interview-quality answer

There is no universal correct chunk size. Start from the retrieval unit and the document’s meaningful structure. A payment clause may need its heading and cross-reference; a table query may need a header plus one row; a short FAQ may need only one answer. Translate that unit into a policy that fits the local embedding model’s input limits and the downstream context/review budget.

Then evaluate multiple candidates on a fixed, representative, held-out collection. Measure retrieval Recall@k and Precision@k, answer-support completeness, chunk count, average token length, storage, latency, and failure groups such as tables, OCR, amendments, and multilingual text. Use overlap only where it fixes measured boundary losses. Prefer structure-aware or parent-child policies where source structure carries meaning and parser quality supports it. Rebuild/version the index whenever the parser, chunk policy, tokenizer, or embedding configuration changes.

That answer is stronger than “use 500 tokens” because it names the evidence needed to justify a size and the constraints that can make a different size correct.

## Exercises

1. Add a P-106 scanned invoice fixture with one deliberately ambiguous OCR character. Define the parser status and what a reviewer must verify before a price is used.
2. Add an amendment to P-105 that changes only the payment condition. Design source/version metadata and a test that prevents the old clause from silently appearing as current evidence.
3. Implement a parent-child mapping for the two Section 3 sentences. Define exactly which parent text is shown after a child match and how tenant/object authorization applies to both records.
4. Create five evaluation queries that expose fixed-boundary failures, table-header loss, sentence abbreviation errors, and structure-aware parser errors. Write relevance and answer-support labels before ranking chunks.
5. Calculate the storage effect of changing one collection from no overlap to 25% overlap, using measured chunk count and your selected vector dimension. State what is excluded from the estimate.

## Definition of done

- [ ] I can distinguish parsing, metadata extraction, chunking, retrieval, and factual verification.
- [ ] I can explain fixed-size, overlapping, sentence-based, semantic, and structure-aware chunking with a concrete failure case.
- [ ] I can explain parent-child retrieval as focused matching plus bounded context, not as a factual answer generator.
- [ ] I can keep table rows, headers, page/section locations, and parser limitations traceable to the source.
- [ ] I can compare at least three chunking strategies on the same frozen collection without fabricating scores.
- [ ] I can record retrieval quality, chunk count, average length, storage impact, and answer-support quality.
- [ ] I can choose chunk size from document structure, retrieval unit, context budget, and held-out evaluation evidence.
- [ ] I know that a parsed string, chunk, vector, or retrieved passage remains untrusted evidence rather than permission to act.

The production lesson can harden these contracts with fuller interfaces, parser boundaries, tests, and operational trade-offs.
