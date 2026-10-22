"""Optional scalar raw-text CrossEncoder for a reviewed, materialized local model."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from importlib import import_module
from importlib.metadata import version
from math import isfinite
from pathlib import Path
from typing import Protocol, cast

from labs.week_05.local_model import directory_digest
from labs.week_08.pipeline import PipelineError, RerankerIdentity


class ArrayResult(Protocol):
    def tolist(self) -> object: ...


class PairTokenizer(Protocol):
    model_max_length: int

    def __call__(
        self,
        first: list[str],
        second: list[str],
        *,
        add_special_tokens: bool,
        truncation: bool,
    ) -> Mapping[str, object]: ...


class CrossBackend(Protocol):
    num_labels: int
    max_seq_length: int
    tokenizer: PairTokenizer

    def predict(
        self,
        pairs: list[list[str]],
        *,
        prompt: str,
        batch_size: int,
        show_progress_bar: bool,
        convert_to_numpy: bool,
        apply_softmax: bool,
    ) -> ArrayResult: ...


class CrossFactory(Protocol):
    def __call__(
        self,
        path: str,
        *,
        local_files_only: bool,
        trust_remote_code: bool,
        token: bool,
        device: str,
        max_length: int,
        prompts: dict[str, str],
        default_prompt_name: str | None,
    ) -> CrossBackend: ...


class LocalCrossEncoder:
    """Narrow plain-text pair adapter, not a universal reranker loader.

    Requires one scalar label, ordinary paired tokenization and no model-specific
    instructions. Caller must review that compatibility and the artifact/license.
    The default lab does not import or install its optional model dependencies.
    """

    def __init__(
        self,
        *,
        backend: CrossBackend,
        model_id: str,
        artifact_digest: str,
        runtime: str,
        token_limit: int,
    ) -> None:
        if type(token_limit) is not int or not 1 <= token_limit <= 8192:
            raise PipelineError("explicit reviewed joint token limit required")
        tokenizer_limit = backend.tokenizer.model_max_length
        if (
            type(tokenizer_limit) is not int
            or not token_limit <= tokenizer_limit <= 1_000_000
        ):
            raise PipelineError("tokenizer requires a known compatible token limit")
        if not all(value.strip() for value in (model_id, artifact_digest, runtime)):
            raise PipelineError("complete model identity required")
        self._backend = backend
        self._token_limit = token_limit
        self._identity = RerankerIdentity(
            model_id,
            "local-cross-encoder/1.0.0",
            artifact_digest,
            runtime,
            f"raw-text-pairs/empty-prompts/default-activation/joint-limit-{token_limit}/v1",
        )
        self._check_backend()

    @property
    def identity(self) -> RerankerIdentity:
        self._check_backend()
        return self._identity

    def _check_backend(self) -> None:
        if (
            type(self._backend.num_labels) is not int
            or self._backend.num_labels != 1
            or type(self._backend.max_seq_length) is not int
            or self._backend.max_seq_length != self._token_limit
            or type(self._backend.tokenizer.model_max_length) is not int
            or not self._token_limit
            <= self._backend.tokenizer.model_max_length
            <= 1_000_000
        ):
            raise PipelineError(
                "requires an unchanged scalar backend and reviewed joint limit"
            )

    @classmethod
    def from_directory(
        cls,
        directory: Path,
        *,
        model_id: str,
        token_limit: int,
    ) -> LocalCrossEncoder:
        before = directory_digest(directory)
        factory = cast(
            CrossFactory, import_module("sentence_transformers").CrossEncoder
        )
        backend = factory(
            str(directory.resolve()),
            local_files_only=True,
            trust_remote_code=False,
            token=False,
            device="cpu",
            max_length=token_limit,
            prompts={"query": "", "document": "", "passage": ""},
            default_prompt_name=None,
        )
        if before != directory_digest(directory):
            raise PipelineError("model artifact changed during loading")
        return cls(
            backend=backend,
            model_id=model_id,
            artifact_digest=before,
            runtime=f"sentence-transformers/{version('sentence-transformers')};torch/{version('torch')}",
            token_limit=token_limit,
        )

    def score_pairs(self, pairs: Sequence[tuple[str, str]]) -> tuple[float, ...]:
        self._check_backend()
        if len(pairs) > 32 or any(
            not query.strip()
            or not passage.strip()
            or len(query) > 1000
            or len(passage) > 4000
            for query, passage in pairs
        ):
            raise PipelineError("requires at most 32 bounded nonblank text pairs")
        if not pairs:
            return ()
        tokenized = self._backend.tokenizer(
            [query for query, _ in pairs],
            [passage for _, passage in pairs],
            add_special_tokens=True,
            truncation=False,
        )
        ids = tokenized.get("input_ids")
        if (
            not isinstance(ids, list)
            or len(ids) != len(pairs)
            or any(
                not isinstance(row, list)
                or not 1 <= len(row) <= self._token_limit
                or any(type(token) is not int or token < 0 for token in row)
                for row in ids
            )
        ):
            raise PipelineError(
                "pair exceeds reviewed joint token limit or has invalid token IDs"
            )
        raw = self._backend.predict(
            [[query, passage] for query, passage in pairs],
            prompt="",
            batch_size=8,
            show_progress_bar=False,
            convert_to_numpy=True,
            apply_softmax=False,
        ).tolist()
        self._check_backend()
        if (
            not isinstance(raw, list)
            or len(raw) != len(pairs)
            or any(
                type(value) not in (int, float) or not isfinite(value) for value in raw
            )
        ):
            raise PipelineError("model output must contain one finite scalar per pair")
        return tuple(float(value) for value in raw)
