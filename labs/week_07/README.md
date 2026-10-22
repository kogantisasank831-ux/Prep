# Week 7: sparse and hybrid retrieval

Compare BM25, a teaching dense boundary, and reciprocal rank fusion (RRF) on
one authorized snapshot. Inspect product-code, supplier, commercial-term, and
paraphrase failures before selecting a policy.

- [Main lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-07/)
- [Beginner lesson](https://kogantisasank831-ux.github.io/Prep/weeks/week-07/beginner/)

## Run

From the repository root in its Python environment:

```shell
python -m pip install -r requirements-dev.txt
python -m labs.week_07.compare --summary
python -m labs.week_07.compare
python -m labs.week_07.compare --candidate-depth 3 --summary
python -m labs.week_07.compare --candidate-depth 8 --summary
python -m pytest tests/test_week07_hybrid.py -q
```

The default run uses the standard library and earlier lab contracts. It makes
no model/network call and needs no credential or GPU. `DemoDenseAdapter` is a
hand-written procurement feature/Jaccard scorer that deliberately ignores codes.
It is not a dense embedding model or a measurement of real semantic retrieval.
Its runtime/preprocessing identity is explicit.

## Files and continuity

| File | Responsibility |
| --- | --- |
| `retrieval.py` | Token/BM25 contracts, authorized corpus, ranking, score floors, RRF provenance, manifests |
| `fixtures.py` | Exact Week 6 accepted source/chunk reuse, new separately identified code notes, denied distractor |
| `queries.jsonl` | Fourteen visible practice queries and source-scoped evidence labels |
| `compare.py` | Same-corpus metrics, subgroup results, full ranking diagnostics, optional local cosine bridge |
| `sample-comparison.json` | Executed default `--summary` output with configuration and fingerprints |
| `tests/test_week07_hybrid.py` (repository root) | Arithmetic, bounds, source continuity, permissions, fusion, metrics |

P-101–P-105 reuse Week 6 parsed text, versions, structure-chunk IDs, and source
locations unchanged. P-106 remains the ambiguous OCR fixture and is excluded.
P-107 is a new Atlas catalogue note with `CW-1000`; P-108 is a new Beacon code
note with `PP-20`. There are seven accepted documents and eleven chunks.
Supplier/document-type labels are curated synthetic metadata under the explicit
`curated-synthetic-fixture-labels/1.0.0` policy, not automatically inferred facts.
Parsed representation and chunk-policy fingerprints remain attached. The
shortened standalone fixture passages in the lesson are an independent teaching
snapshot; they must not overwrite the actual Week 6 source versions.

Practice labels use `document/version/body-block` keys resolved to immutable
chunk IDs within each authorized/filter snapshot. Any missing or ambiguous key,
or substring absent from its declared source chunk, fails evaluation. The corpus
has one tenant/version per evidence key. A real multi-tenant label store needs
fully scoped keys and governed active-version rules.

## Retrieval contracts

The fixed ASCII tokenizer lowercases and preserves internal `-`, `_`, and `/`.
`CW-1000`, `CW1000`, `CW-100O`, and `CW-1000-ALT` are distinct terms. It does not
provide literal Unicode identity, aliases, spelling correction, stemming, entity
resolution, or abbreviation expansion. Token equality does not enforce every
constraint in a longer query; a BM25 candidate need not match all query tokens.

BM25 uses the displayed positive log1p-IDF variant with unique query terms,
`k1=1.2`, and `b=0.75`. Its dictionaries are read-only snapshots. This is exact
scoring over a small corpus, not optimized postings or bit-for-bit Lucene output.
An analyzer/field/shard implementation may have different scores and behavior.
The reference bounds requests to 1,000 Python characters, source chunks to 4,000
characters, and corpora/depth/k to at most 256 chunks. These are lab input limits,
not model token budgets. Invalid UTF-8, duplicate IDs/metadata, nonfinite numbers,
and boolean numeric parameters fail explicitly.

A trusted principal's object grants are applied before the two allowed exact
metadata predicates (`supplier`, `document_type`). Filters narrow access; they
cannot grant it. BM25 statistics are built only over that eligible partition,
and dense scoring sees the same records. Corpus reuse requires the same
principal and canonical filters. Adding the denied exact-code distractor changes
neither eligible content, BM25 statistics, dense results, nor fusion output.
These tests do not establish constant-time behavior or production side-channel
resistance. A public-background-statistics design would need a separate declared
contract; this reference intentionally uses partition-local private statistics.

Sparse scores must be strictly positive. Teaching dense scores must exceed zero;
a real cosine adapter uses its recorded floor. Zero-score padding cannot gain
RRF votes. This is a narrow accepted-candidate policy, not calibrated confidence
or a general abstention detector. Empty corpus and no accepted matches yield an
empty tuple; permissions and query terms are never silently broadened.

Each standalone baseline returns at most k=3 accepted chunks. Hybrid retrieves
at most depth=5 accepted chunks per path, then fuses down to three. That union is
additional configured work. RRF uses equal weights and constant 60 by default,
retains raw ranks/scores per contributor, rejects duplicate/conflicting
contributions, and breaks ties by chunk ID. Input ranks are contiguous per
retriever starting at one. It deduplicates the same chunk ID across lists; it
does not deduplicate overlapping or related chunks by source meaning.

The manifest records the source representation, full-precision BM25 settings,
algorithm/token/dense/fusion identities, principal/filter partition, depth and
output k. Corpus fingerprints bind actual text and metadata as well as supplied
source hashes. Compatibility hashes require trusted manifests; they are not
signatures or proof of authenticity. No existing durable index is migrated.

## Measurements and limits

The fourteen queries include ten with direct-support labels and four no-gold
cases: an unmapped alias, an OCR-like variant, an undefined abbreviation, and a
denied identifier. All are visible `practice` cases, not a held-out benchmark.

P@k divides by requested k even for short lists. Recall, reciprocal rank, and
binary nDCG use the same chunk granularity as the labels; undefined no-gold
metrics stay null. Quality means use only the ten labelled queries. No-gold
candidate/empty counts are reported separately. Required substring atoms must
occur in their specific labelled source chunks; support is not entailment or
answer correctness. `same_source_repeat_fraction` counts repeated document/version
hits, which can be complementary evidence rather than redundant text.

Default mean Recall@3 is 0.967 for sparse, 0.467 for teaching dense, and 0.967
for RRF. The fake's absent code features explain its identifier misses. All paths
miss one of Q09's three evidence units. Tiny visible labels and a fake dense
scorer cannot establish a production winner. No latency, actual sparse/vector
index memory, generated answers, or real-model quality was measured.

Run without `--summary` for raw scores/ranks, source locations, evidence keys,
manifest/corpus fingerprints, and fusion contributors. Full diagnostic output is
appropriate here because the fixtures are synthetic; do not put sensitive
queries, source text, or unrestricted diagnostics in general production logs.

## Optional actual local model

Follow [Week 5's optional model instructions](../week_05/README.md#optional-actual-local-model-run)
for the pinned dependency, reviewed materialized artifact, required prefixes,
offline settings, and token/input preparation limits. Then run:

```shell
python -m labs.week_07.compare --model-directory .runtime/embedding-model --model-id reviewed-local-model --summary
```

Pass exact `--query-prefix` and `--document-prefix` values required by the chosen
model. The reused adapter uses CPU/local-files-only/no remote code and checks
prompted token limits before encoding. No model artifact was loaded for this
sample. No flag makes an arbitrary artifact trustworthy.

`LocalCosineAdapter` invokes separate query/document APIs and checks batch shape,
dimensions, finite/nonzero vectors, and observable backend identity drift. Its
pairwise recomputation is an inspectable reference, not an efficient vector
index. `--dense-min-score` defaults to zero; valid cosine scores can be negative,
so tune that selection floor using development evidence and record missed
positives. Changing the floor changes its manifest. The wrapper is tested with
the deterministic Week 5 encoder, not actual model inference.
