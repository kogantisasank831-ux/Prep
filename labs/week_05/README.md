# Week 5: embeddings and vector retrieval

Build the smallest inspectable procurement-search pipeline: load documents, make
traceable initial chunks, embed documents/queries, store vectors, and retrieve
authorised top-k passages. No orchestration framework is used.

- [Main lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-05/)
- [Beginner lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-05/beginner/)

## Teaching run

From the repository root, using the project's Python environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_05.demo
python -m pytest tests/test_week05_retrieval.py -q
```

The default demo has no network requests, downloaded model, GPU requirement, or
credential. It prints `teaching features; not semantic-model evaluation`, then
P-101 and P-104 with tied scores of approximately 0.57735. The teaching encoder
uses explicit features, including payment/approval/inspection terms. Its result
demonstrates the pipeline and deterministic tie policy; it is not evidence of a
learned embedding model's accuracy. The score is not a probability.

`data.py` reads the checked-in `corpus.jsonl` with a 64 KiB corpus limit and strict
UTF-8/JSONL validation. Document IDs are scoped by tenant and version; duplicates,
unknown fields, malformed JSON, invalid text, and oversized records fail.
`retrieval.py` limits each short document/query to 1,000 Python characters. That
limit is a teaching input policy, not a model token budget.

One accepted short document becomes one chunk. Long-document splitting belongs
to Week 6; this baseline rejects oversized inputs rather than silently slicing
off potentially important terms.

## Files and contracts

| File | Responsibility |
| --- | --- |
| `corpus.jsonl` | Four synthetic, versioned procurement documents |
| `queries.jsonl` | Twelve practice queries and direct-support relevance labels |
| `data.py` | Bounded JSONL loading and source validation |
| `retrieval.py` | Vector math, identity/manifest checks, exact storage/search, access policy |
| `metrics.py` | Binary Precision/Recall/reciprocal-rank/nDCG arithmetic |
| `local_model.py` | Optional adapter for an already-reviewed local Sentence Transformers directory |
| `demo.py` | Teaching run, or explicit local-model integration run |

The exact index requires finite, non-zero, dimension-compatible vectors and
normalizes them before cosine search. It records source and model fingerprints,
rejects observable identity drift during a call, filters the candidate set before
scoring, and breaks equal-score ties by chunk ID. The object access policy is
supplied by trusted application code; a query cannot grant itself access.

The baseline requires `1 <= k <= authorised candidate count`. No authorised
objects returns an empty tuple. It does not implement a relevance threshold or
automatically conclude that no evidence exists. Filtering before ranking is not
a constant-time guarantee or complete multi-tenant side-channel defence.

The manifest's logical index ID identifies the source/configuration recipe. It
does not attest actual vector bytes or guarantee bitwise reproducibility. A
persisted snapshot needs its own checksum and recovery/promotion contract.

## Evaluate a ranking

```python
from labs.week_05.metrics import evaluate_ranking

result = evaluate_ranking(
    ["P-103", "P-101", "P-102", "P-104"],
    frozenset({"P-101", "P-104"}),
    k=2,
)
assert result.precision_at_k == 0.5
assert result.recall_at_k == 0.5
assert result.reciprocal_rank_at_k == 0.5
```

Precision's denominator is requested k, including when fewer results are returned.
Recall, reciprocal rank, and binary nDCG are null for queries with no labelled
relevant source. Keep those cases separate when aggregating; report candidate
counts and abstention/review behavior rather than converting undefined scores to
a claimed success. For relevant-labelled queries with no returned hit, the scores
are zero. Ranked IDs must be unique and use the same granularity as labels.

`queries.jsonl` is deliberately marked `practice`. Its four-document snapshot is
too small and too visible to certify model quality. Label rules require direct
support from the embedded text; broad topical similarity does not count. Missing
price, missing exact-code, and negation cases have empty relevance sets.
Create the separate, governed development/holdout collection described in the
lesson before selecting a model. Group near duplicates/paraphrases and record
adjudication, source versions, permissions, configuration, and denominators.

ANN neighbour overlap with the exact index is a different measurement from these
human-labelled relevance metrics. This lab does not implement ANN or report ANN
performance.

## Optional actual local-model run

This step requires an already-downloaded, reviewed, materialized text embedding
model in Sentence Transformers format. Model acquisition, license review, and
hardware selection are operator tasks. Keep this optional dependency out of the
base environment if its torch/transformers stack conflicts with your project:

```shell
python -m pip install -r labs/week_05/requirements-local-model.txt
python -m labs.week_05.demo --model-directory .runtime/embedding-model
```

The dependency is pinned to Sentence Transformers 6.1.0, as documented in its
[official release](https://github.com/huggingface/sentence-transformers/releases/tag/v6.1.0).
The adapter uses CPU, `local_files_only=True`, `trust_remote_code=False`, and
`token=False`. It does not download a missing model. Enable the
`HF_HUB_OFFLINE=1` environment setting before a real
run when enforcing offline dependency behavior. Never assume a local artifact is
safe or suitable merely because these options exist.

Pass `--query-prefix` and `--document-prefix` with the exact instructions required
by the selected model card. Defaults are empty and override saved prompt defaults;
they are appropriate only for a model requiring no prefix. Separate
`encode_query`/`encode_document` paths preserve task-specific routing. The adapter
assumes a text model where prefix-plus-text tokenization matches the encoder's
input preparation; models with custom chat preprocessing need a different
adapter and verification.

The adapter hashes filenames and bytes in the local directory before loading,
checks that the directory did not change during loading, records runtime and
preprocessing identity, and refuses symlinks to untracked files. Use a complete
materialized folder rather than a cache snapshot of symlinks. It checks prompted
token counts before encoding to avoid silent truncation, then checks vector batch
size, dimensions, numeric types, and finite values. The exact index handles
normalization and zero-vector rejection.

The included tests use a fake backend to exercise these contracts. No actual
model artifact, inference latency, semantic accuracy, or hardware-fit result is
claimed by those tests. Record such measurements separately when you run a real
model. Keep source text, queries, and vectors out of routine logs; the CLI prints
only this synthetic demo's source snippets for teaching.
