---
layout: "week"
status: "review"
version: "0.1.0"
last_reviewed: "2026-11-09"
header_context: "Interview preparation"
back_label: "Interview prep"
back_url: "/interview-prep/"
toc_heading: "Interview sections"
pagination_label: "Interview prep hub"
pagination_url: "/interview-prep/"
title: "Python interview cheat sheet"
description: "Production Python revision for AI Engineer, ML Engineer, and senior Data Science interviews."
summary: "Revise Python semantics, data structures, concurrency, APIs, testing, reliability, and common coding-round traps."
permalink: "/interview-prep/cheat-sheets/python/"
kicker_primary: "Interview preparation"
kicker_secondary: "Batch 1 · Python"
current_label: "Revision guide"
alternate_label: "Interview prep hub"
alternate_url: "/interview-prep/"
---
> **Batch 1 source:** This page integrates the previously prepared revision artifact into the Prep site. It is separate from the Week 1–20 learning assessments.

**Target roles:** AI Engineer, ML Engineer, Senior/Lead Data Scientist  
**Goal:** explain, code, debug, test, and discuss production trade-offs—not merely recall syntax.

## 1. Thirty-second revision

- Python names reference objects; assignment normally does not copy an object.
- Prefer dictionaries/sets for average `O(1)` lookup, `deque` for queues, and `heapq` for top-K.
- Use generators for streaming; context managers for cleanup; type hints for contracts.
- Threads help I/O-bound work; processes help CPU-bound Python work; `asyncio` helps many waiting tasks.
- Production code needs validation, structured logging, timeouts, tests, and explicit error handling.
- In interviews: state assumptions, give complexity, test edge cases, then improve the solution.

## 2. Python object model

### Names, identity, equality, and mutability

```python
a = [1, 2]
b = a              # same list
c = a.copy()       # new outer list

assert a is b
assert a == c
assert a is not c
```

| Concept | Meaning | Interview trap |
|---|---|---|
| `is` | Same object identity | Do not use for value comparison except singletons such as `None` |
| `==` | Equal values | May call a custom `__eq__` method |
| Mutable | Object can change in place | Lists/dicts/sets cannot be safely shared as defaults |
| Immutable | Value cannot change in place | Tuple is only hashable if every element is hashable |
| Hashable | Stable hash and equality | Required for dictionary keys and set elements |

### Shallow versus deep copy

```python
from copy import deepcopy

original = [[1], [2]]
shallow = original.copy()
deep = deepcopy(original)

original[0].append(99)
assert shallow[0] == [1, 99]  # nested object shared
assert deep[0] == [1]         # nested object copied
```

### Never use a mutable default

```python
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    result = [] if items is None else items
    result.append(item)
    return result
```

Default arguments are evaluated once when the function is defined, not on every call.

## 3. Core collections and complexity

| Operation | List | Dict/Set average | `deque` | Heap |
|---|---:|---:|---:|---:|
| Index by position | `O(1)` | — | `O(n)` middle | — |
| Search by value/key | `O(n)` | `O(1)` | `O(n)` | `O(n)` |
| Append right | Amortized `O(1)` | `O(1)` insert | `O(1)` | `O(log n)` push |
| Remove right | `O(1)` | `O(1)` delete | `O(1)` | `O(log n)` pop-min |
| Insert/remove left | `O(n)` | — | `O(1)` | — |
| Sort | `O(n log n)` | — | — | — |

Use:

- `list`: ordered sequence and random access;
- `tuple`: immutable record/hashable key when all values are hashable;
- `dict`: key-value lookup and counting;
- `set`: membership and deduplication;
- `collections.deque`: queue and sliding-window operations;
- `heapq`: priority queue and top-K;
- `collections.Counter`: frequency table;
- `collections.defaultdict`: grouped accumulation.

```python
from collections import Counter, defaultdict, deque
import heapq

counts = Counter("mississippi")
groups: defaultdict[str, list[int]] = defaultdict(list)
queue: deque[int] = deque([1, 2, 3])
smallest_three = heapq.nsmallest(3, [8, 1, 5, 2, 9])
```

## 4. High-value syntax

### Comprehensions and generator expressions

```python
squares = [x * x for x in range(10) if x % 2 == 0]
square_by_value = {x: x * x for x in range(5)}
unique_lengths = {len(word) for word in ["AI", "model", "agent"]}

# Lazy; values are produced only as requested.
total = sum(x * x for x in range(1_000_000))
```

Avoid deeply nested comprehensions when a loop is easier to read and debug.

### `enumerate`, `zip`, unpacking, and sorting

```python
names = ["Ada", "Grace", "Geoffrey"]
scores = [92, 95, 90]

for position, (name, score) in enumerate(zip(names, scores), start=1):
    print(position, name, score)

records = [("b", 2), ("a", 2), ("c", 1)]
records.sort(key=lambda row: (row[1], row[0]))
```

Python sort is stable: records with equal keys retain their previous relative order.

### Useful idioms

```python
value = mapping.get("key", default_value)
first, *middle, last = [1, 2, 3, 4]
merged = {**defaults, **overrides}
unique_in_order = list(dict.fromkeys(items))
```

## 5. Functions, scope, closures, and decorators

### Arguments

```python
def predict(
    features: list[float],
    /,
    model_name: str = "baseline",
    *,
    threshold: float = 0.5,
) -> bool:
    """`features` is positional-only; `threshold` is keyword-only."""
    score = sum(features) / max(len(features), 1)
    return score >= threshold
```

### Closures

```python
from collections.abc import Callable

def make_threshold(threshold: float) -> Callable[[float], bool]:
    def classify(score: float) -> bool:
        return score >= threshold
    return classify
```

### Decorator with preserved metadata

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def log_call(function: Callable[P, R]) -> Callable[P, R]:
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling={function.__name__}")
        return function(*args, **kwargs)
    return wrapper
```

## 6. Iterators and generators

An **iterable** can produce an iterator. An **iterator** implements `__next__()` and is consumed once. A generator is a convenient iterator created with `yield`.

```python
from collections.abc import Iterable, Iterator

def batches(values: Iterable[int], size: int) -> Iterator[list[int]]:
    if size <= 0:
        raise ValueError("size must be positive")

    batch: list[int] = []
    for value in values:
        batch.append(value)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch
```

Use generators for large files, database cursors, model batches, or streaming responses. Do not use one if you need repeated random access.

## 7. Context managers and resource safety

```python
from contextlib import contextmanager
from collections.abc import Iterator
from time import perf_counter

@contextmanager
def timer(label: str) -> Iterator[None]:
    started = perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (perf_counter() - started) * 1_000
        print(f"{label}: {elapsed_ms:.2f} ms")

with timer("inference"):
    result = sum(range(100_000))
```

`finally` runs even when the managed block raises an exception. This is why context managers are appropriate for files, database sessions, locks, and temporary resources.

## 8. Object-oriented design and typing

Prefer composition over deep inheritance. Use:

- `dataclass` for plain internal data;
- Pydantic models at untrusted boundaries such as APIs/configuration;
- `Protocol` for structural interfaces and easy testing;
- abstract base classes when runtime inheritance contracts are genuinely needed.

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True, slots=True)
class Prediction:
    label: str
    probability: float

class Predictor(Protocol):
    def predict(self, text: str) -> Prediction: ...

class PredictionService:
    def __init__(self, predictor: Predictor) -> None:
        self._predictor = predictor

    def classify(self, text: str) -> Prediction:
        if not text.strip():
            raise ValueError("text cannot be empty")
        return self._predictor.predict(text)
```

The service depends on behavior, not a concrete model library. A fake predictor can be injected in unit tests.

## 9. Exceptions, logging, and cleanup

### Exception rules

- Catch the narrowest exception you can handle.
- Add useful context and preserve the cause with `raise ... from error`.
- Do not log and re-raise at every layer; that creates duplicate logs.
- Use domain exceptions when callers need to make different decisions.
- Never silently return a normal-looking value after an unexpected failure.

```python
class ModelLoadError(RuntimeError):
    pass

def load_model(path: str) -> object:
    try:
        return open_model(path)
    except OSError as error:
        raise ModelLoadError(f"could not load model from {path}") from error
```

### Structured logging

```python
import logging

logger = logging.getLogger(__name__)

def record_prediction(request_id: str, latency_ms: float) -> None:
    logger.info(
        "prediction_completed",
        extra={"request_id": request_id, "latency_ms": latency_ms},
    )
```

Do not put secrets, full prompts, PII, or tokens into logs.

## 10. Concurrency decision table

| Need | Best starting point | Why |
|---|---|---|
| Many HTTP/database waits | `asyncio` | One thread can interleave many waiting tasks |
| Blocking I/O library | Thread pool | Simple integration without rewriting library |
| CPU-heavy pure Python | Multiprocessing/process pool | Bypasses the CPython GIL using processes |
| NumPy/PyTorch compute | Library-native parallelism | Native code/GPU often releases the GIL |
| Distributed jobs | Queue/Ray/Spark/Celery | Work exceeds one process or machine |

### Bounded asynchronous concurrency

```python
import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")

async def bounded_map(
    function: Callable[[T], Awaitable[R]],
    values: Iterable[T],
    limit: int,
) -> list[R]:
    semaphore = asyncio.Semaphore(limit)

    async def run(value: T) -> R:
        async with semaphore:
            return await function(value)

    return await asyncio.gather(*(run(value) for value in values))
```

Production additions: timeouts, retries only for transient/idempotent work, cancellation handling, rate limits, and partial-failure policy.

## 11. Testing essentials

Test observable behavior and important failure paths—not private implementation details.

```python
import pytest

@pytest.mark.parametrize(
    ("values", "size", "expected"),
    [
        ([1, 2, 3], 2, [[1, 2], [3]]),
        ([], 3, []),
        ([1, 2], 1, [[1], [2]]),
    ],
)
def test_batches(values: list[int], size: int, expected: list[list[int]]) -> None:
    assert list(batches(values, size)) == expected

def test_batches_rejects_nonpositive_size() -> None:
    with pytest.raises(ValueError, match="positive"):
        list(batches([1], 0))
```

For AI services, test:

- validation and malformed input;
- model/retriever/tool adapters with fakes;
- deterministic preprocessing/postprocessing;
- timeouts, retries and fallbacks;
- schema compatibility;
- idempotency and duplicate requests;
- regression examples from production failures.

## 12. Interview problem patterns

### Pattern 1: frequency map — top-K frequent values

```python
from collections import Counter
import heapq

def top_k_frequent(values: list[int], k: int) -> list[int]:
    if k < 0:
        raise ValueError("k cannot be negative")
    counts = Counter(values)
    return [value for value, _ in heapq.nlargest(k, counts.items(), key=lambda x: x[1])]
```

Time: `O(n + u log k)`, where `u` is the number of unique values. Space: `O(u)`.

### Pattern 2: sliding window — longest substring without repetition

```python
def longest_unique_substring(text: str) -> int:
    latest: dict[str, int] = {}
    left = 0
    best = 0

    for right, character in enumerate(text):
        if character in latest and latest[character] >= left:
            left = latest[character] + 1
        latest[character] = right
        best = max(best, right - left + 1)
    return best
```

Time: `O(n)`. Space: `O(min(n, alphabet size))`.

### Pattern 3: merge intervals

```python
def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []

    ordered = sorted(intervals)
    merged = [ordered[0]]

    for start, end in ordered[1:]:
        previous_start, previous_end = merged[-1]
        if start <= previous_end:
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))
    return merged
```

Time: `O(n log n)` due to sorting. Space: `O(n)` for output/sorted copy.

### Pattern 4: LRU cache

```python
from collections import OrderedDict
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._data: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> V | None:
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: K, value: V) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self._capacity:
            self._data.popitem(last=False)
```

Average `get`/`put`: `O(1)`. Discuss thread safety and cache invalidation in a production extension.

## 13. Performance and memory

- Measure first with `timeit`, `cProfile`, `py-spy`, or memory profilers.
- Pick the right algorithm before micro-optimizing syntax.
- Vectorize numeric operations with NumPy/PyTorch when appropriate.
- Avoid repeated concatenation of immutable strings; use `"".join(parts)`.
- Stream large inputs with iterators instead of materializing everything.
- Batch external calls to reduce network/model overhead.
- Beware accidental `O(n²)` work in nested loops, repeated list membership, or repeated DataFrame concatenation.
- Cache only when keys are stable, memory is bounded, and invalidation is defined.

## 14. Common traps

| Trap | Safer approach |
|---|---|
| Mutable default argument | Use `None`, then create the collection inside |
| `is` for strings/numbers | Use `==` for values |
| `except Exception: pass` | Catch expected exceptions and handle explicitly |
| List used as queue | Use `collections.deque` |
| Modifying a collection while iterating | Iterate over a copy or construct a new result |
| Late-bound loop variable in closure | Bind it as a default or use a factory function |
| Blocking call inside async route | Use async client or offload to a thread pool |
| Unbounded `gather`/thread pool | Apply concurrency limits/backpressure |
| Pickle from an untrusted source | Use a safe data format; Pickle can execute code |
| Notebook-only global state | Extract deterministic functions/services with tests |

## 15. Rapid interview questions and answers

1. **List versus tuple?** Lists are mutable; tuples are immutable and may be hashable. Use tuples for fixed records/keys and lists for changing sequences.
2. **Why are dictionary lookups usually `O(1)`?** A hash maps the key to a table location; collisions and resizing make this average, not absolute worst-case, complexity.
3. **Generator benefit?** Lazy production reduces peak memory and supports streaming, but a generator is normally one-pass and lacks random access.
4. **`__new__` versus `__init__`?** `__new__` creates/returns the instance; `__init__` initializes an already-created instance.
5. **What does the GIL mean?** In standard CPython it restricts simultaneous execution of Python bytecode in a process; I/O threads can still overlap waiting and native libraries may release it.
6. **Thread versus process?** Threads share memory and are lighter; processes isolate memory and enable parallel CPU-bound Python at higher serialization/startup cost.
7. **Why use `Protocol`?** It allows structural typing: any object with the required behavior satisfies the contract, improving decoupling and testability.
8. **What is a context manager?** A construct that guarantees entry/exit behavior, commonly cleanup, around a block—even when an exception occurs.
9. **How do you make retries safe?** Retry only transient failures, cap attempts, add jitter/backoff, enforce timeouts, and ensure the operation is idempotent or protected by an idempotency key.
10. **How would you reduce Python service latency?** Profile; reduce algorithmic work and serialization; batch/cache carefully; use async for I/O; move numeric work to optimized libraries; scale workers only after measuring bottlenecks.

## 16. Lead-level case

**Question:** Design a Python service that classifies 1,000 emails per second using an external model API while protecting the provider from overload.

**Strong answer structure:**

1. Define latency SLO, peak/average rate, payload size, error budget, and classification quality.
2. Use a thin FastAPI route, validated Pydantic request, service layer, and provider adapter.
3. Apply bounded async concurrency, connection pooling, per-request timeout, and global/provider rate limit.
4. Batch requests only if the provider and latency target allow it.
5. Add an idempotency key for client retries; never blindly repeat a possibly completed side effect.
6. Retry transient errors with exponential backoff/jitter; do not retry validation/authentication failures.
7. Use a queue when accepted asynchronous processing is allowed; define backpressure and dead-letter handling.
8. Cache only stable classifications and include model/prompt/version in the key.
9. Record latency percentiles, queue depth, provider errors, retry count, token/cost use, and model-quality samples.
10. Load test, deploy with canary rollout, and define fallback/degradation behavior.

## 17. Final revision checklist

- [ ] I can explain references, mutability, copying, equality and hashability.
- [ ] I know collection-operation complexity.
- [ ] I can use generators, decorators and context managers.
- [ ] I can design typed, testable classes using composition.
- [ ] I understand threads, processes, async and bounded concurrency.
- [ ] I can solve hash-map, sliding-window, interval, heap and graph problems.
- [ ] I state complexity and test edge cases without being prompted.
- [ ] I can turn notebook logic into a tested production service.
