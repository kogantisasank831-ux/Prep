# Week 6: document parsing and chunking

Compare fixed, overlap, sentence, structure, shared-term “semantic,” and
parent-child policies on one versioned procurement collection. Inspect what the
retriever actually returns before choosing a boundary.

- [Main lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-06/)
- [Beginner lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-06/beginner/)

## Run the teaching comparison

From the repository root in the project's Python environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_06.compare --summary
python -m labs.week_06.compare
python -m labs.week_06.compare --context-budget-chars 100 --summary
python -m pytest tests/test_week06_chunking.py -q
```

The default run needs no downloaded model, network, credential, or GPU. The core
uses the standard library and Week 5 vector/adapter interfaces. The teaching
encoder adds a constant 0.1 coordinate to Week 5's five hand features so headings
have a nonzero vector. Its identity explicitly differs from Week 5's encoder.
This is pipeline practice, not trained-model quality evaluation. The separate
shared-term Jaccard boundary heuristic is also not a learned semantic model.

## Files

| File | Responsibility |
| --- | --- |
| `fixtures.py` | Five accepted parsed-layout documents and one uncertain OCR-like table |
| `queries.jsonl` | Nine visible practice queries with per-document evidence substrings |
| `chunking.py` | Parser status, versioned policies, precise window spans, manifests, access filter |
| `compare.py` | Exact cosine comparison, bounded authorized parent expansion, measurements |
| `sample-comparison.json` | Executed default `--summary` output, reproducible without a model |
| `tests/test_week06_chunking.py` (repository root) | Boundaries, evidence retention, identity, authorization, metrics |

P-101 through P-105 are synthetic. P-105 has headings, a labelled table row, and a
cross-reference between its invoicing section and Schedule A. P-106 contains
`USD 12.O0` and stays `needs_review`. No PDF bytes, images, or OCR engine are used.
The parser validates fixture blocks and a deliberately narrow labelled-row
format; an accepted row is not independently verified against an original file.
Missing table locations, uncertain row format, replacement characters, and
heading-only sources need review. Invalid text/identity/locations or oversized
inputs are rejected. Review-required sources cannot enter `ChunkCollection.build`.

Fixed and overlapping windows use half-open offsets relative to trimmed parsed
block text, in Python characters. They cite only intersecting blocks and stop at
the first window reaching the source end. These offsets are not raw bytes, PDF
bounding boxes, or tokenizer positions. Sentence chunks preserve nonparagraph
blocks atomically; the regex is only a controlled-prose splitter and its width
is a soft target. Structure chunks attach the active heading to each body block;
isolated headings without bodies are a limitation of that simple policy.
Parent-child policy also retains isolated headings as explicit children.

Content digests identify canonical text; representation fingerprints additionally
bind parser, metadata, layout, and status. Chunk manifests checksum the stored
records. These checks require a trusted manifest; they are not signatures or a
proof of source authenticity. Local collections use the versioned
`procurement-chunks/1.1.0` schema, without migrating any existing index.

## Read the measurements

Every policy receives the same accepted source representation, queries,
authorization rules, model identity, cosine metric, top-three **chunk** budget,
and 800-character context budget. Only children are embedded for parent-child
retrieval. Parents are stored too, re-authorized on expansion, deduplicated, and
admitted only as whole units that fit. A Section 3 parent does not include the
Schedule A row automatically. Too-large context units are skipped.

Seven practice queries have direct-support document labels; two have no gold
support. Labels assume one tenant/version per document ID in this frozen
snapshot; comparisons reject repeated IDs across versions/tenants. A real
multi-version benchmark needs fully scoped labels and active-version rules.

- `document_recall_at_chunk_k`: distinct labelled relevant documents reached by
  the top k chunks, divided by relevant-document count. Duplicate document hits
  still consume the chunk budget. This is not chunk-level recall or recall over
  a separately ranked list of k distinct documents.
- `complete_support_source_fraction`: for each query, the fraction of labelled
  sources with every required substring in admitted context; then averaged over
  labelled queries. Substrings are matched only within their own document.
  Equivalent wording can fail, and matching words does not prove entailment.
- No-gold queries get null recall/support and are excluded from both means.
  Candidates are still returned: the lab has no abstention policy, so these
  queries do not demonstrate correct no-answer behavior.
- Text bytes cover stored UTF-8 text only. Packed float32 vector bytes are an
  estimate: indexed count × dimension × 4. IDs, metadata, parent links, Python
  objects, allocator overhead, and index structures are excluded.
- `average_tokens` and `generated_answer_quality` remain null. No tokenizer
  lengths, latency, actual memory, generated answers, human answer grades, or
  real PDF/OCR accuracy were measured.

The checked-in summary is the result of the default practice configuration. It
is not held-out evidence of a winning policy. Run without `--summary` to inspect
per-query ranked/context IDs. Use `policy.chunk(source)` in a Python session to
resolve IDs to text and locations. Begin with Q04: the relevant document can be
found while the row, payment condition, and cross-reference do not all reach
context. Change one factor at a time and retain the source/query fingerprints.

## Optional actual local model

Reuse [Week 5's optional adapter instructions](../week_05/README.md#optional-actual-local-model-run)
for the pinned dependency, reviewed materialized artifact, model-specific exact
prefixes, offline settings, and input-preparation limits. Then run:

```shell
python -m labs.week_06.compare --model-directory .runtime/embedding-model --model-id reviewed-local-model --summary
```

Pass `--query-prefix` and `--document-prefix` exactly as the selected model
requires. The adapter uses CPU/local-files-only/no remote code, checks prompted
token limits before encoding, and rejects truncating inputs. Those flags do not
certify an arbitrary model artifact. No actual model was loaded for the sample.
A real-model run changes retrieval measurements but leaves the Jaccard boundary
heuristic unchanged; a learned boundary experiment needs its own versioned
`AdjacentSimilarity` adapter, development labels, and held-out evaluation.
