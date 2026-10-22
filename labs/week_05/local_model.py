"""Optional in-process adapter for an already reviewed, materialized model folder.

The normal teaching demo does not import Sentence Transformers. Real integration
requires the optional dependency and a compatible local artifact; nothing here
downloads a model or calls a hosted endpoint.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from hashlib import sha256
from importlib import import_module
from importlib.metadata import version
import json
from pathlib import Path
from typing import Protocol, cast

from labs.week_05.retrieval import (
    EmbeddingModelIdentity,
    EmbeddingRuntimeError,
    Vector,
    digest_text,
    validate_vector,
)


class ArrayResult(Protocol):
    def tolist(self) -> object: ...


class Tokenizer(Protocol):
    def __call__(
        self, texts: list[str], *, add_special_tokens: bool, truncation: bool
    ) -> Mapping[str, object]: ...


class EncoderBackend(Protocol):
    max_seq_length: int
    tokenizer: Tokenizer

    def get_sentence_embedding_dimension(self) -> int | None: ...

    def encode_query(
        self,
        texts: list[str],
        *,
        prompt: str,
        precision: str,
        convert_to_numpy: bool,
        normalize_embeddings: bool,
        show_progress_bar: bool,
    ) -> ArrayResult: ...

    def encode_document(
        self,
        texts: list[str],
        *,
        prompt: str,
        precision: str,
        convert_to_numpy: bool,
        normalize_embeddings: bool,
        show_progress_bar: bool,
    ) -> ArrayResult: ...


class BackendFactory(Protocol):
    def __call__(
        self,
        model_name_or_path: str,
        *,
        local_files_only: bool,
        trust_remote_code: bool,
        token: bool,
        device: str,
    ) -> EncoderBackend: ...


def directory_digest(directory: Path) -> str:
    """Digest relative filenames and bytes; reject links to untracked artifacts."""
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("use an existing materialized model directory")
    files = sorted(directory.rglob("*"))
    if any(path.is_symlink() for path in files):
        raise ValueError("materialize model files instead of using symlinks")
    hasher = sha256()
    count = 0
    for path in files:
        if not path.is_file():
            continue
        name = path.relative_to(directory).as_posix().encode("utf-8")
        hasher.update(len(name).to_bytes(8, "big"))
        hasher.update(name)
        file_hasher = sha256()
        with path.open("rb") as handle:
            while block := handle.read(1024 * 1024):
                file_hasher.update(block)
        hasher.update(file_hasher.digest())
        count += 1
    if count == 0:
        raise ValueError("model directory must contain files")
    return hasher.hexdigest()


class LocalSentenceTransformer:
    """Keep model loading and role-specific encoding outside the exact index."""

    def __init__(
        self,
        *,
        backend: EncoderBackend,
        model_id: str,
        artifact_digest: str,
        runtime_version: str,
        query_prefix: str,
        document_prefix: str,
    ) -> None:
        dimension = backend.get_sentence_embedding_dimension()
        if type(dimension) is not int or dimension < 1:
            raise ValueError("encoder must expose a positive embedding dimension")
        if type(backend.max_seq_length) is not int or backend.max_seq_length < 1:
            raise ValueError("encoder must expose a positive token limit")
        self._backend = backend
        self._query_prefix = query_prefix
        self._document_prefix = document_prefix
        self._identity = EmbeddingModelIdentity(
            model_id=model_id,
            artifact_digest=artifact_digest,
            runtime_version=runtime_version,
            preprocessing_version="role-api-float32/v1:"
            + digest_text(
                json.dumps(
                    {
                        "query_prefix": query_prefix,
                        "document_prefix": document_prefix,
                        "max_seq_length": backend.max_seq_length,
                    },
                    sort_keys=True,
                )
            ),
            dimension=dimension,
            metric="cosine",
            asymmetric=True,
        )

    @classmethod
    def from_directory(
        cls, directory: Path, *, model_id: str, query_prefix: str, document_prefix: str
    ) -> LocalSentenceTransformer:
        artifact = directory_digest(directory)
        # This cast contains the optional dependency's untyped import boundary.
        factory = cast(
            BackendFactory,
            getattr(import_module("sentence_transformers"), "SentenceTransformer"),
        )
        backend = factory(
            str(directory.resolve()),
            local_files_only=True,
            trust_remote_code=False,
            token=False,
            device="cpu",
        )
        if directory_digest(directory) != artifact:
            raise ValueError("model directory changed during loading")
        return cls(
            backend=backend,
            model_id=model_id,
            artifact_digest=artifact,
            runtime_version=f"sentence-transformers/{version('sentence-transformers')};torch/{version('torch')}",
            query_prefix=query_prefix,
            document_prefix=document_prefix,
        )

    @property
    def identity(self) -> EmbeddingModelIdentity:
        return self._identity

    def _embed(self, texts: Sequence[str], *, query: bool) -> tuple[Vector, ...]:
        if not texts:
            return ()
        prefix = self._query_prefix if query else self._document_prefix
        try:
            # Explicit prompts avoid hidden saved prompt defaults. Check complete
            # prompted inputs without truncation before calling the encoder.
            tokenized = self._backend.tokenizer(
                [prefix + text for text in texts],
                add_special_tokens=True,
                truncation=False,
            )
            ids = tokenized.get("input_ids")
            if not isinstance(ids, list) or len(ids) != len(texts):
                raise EmbeddingRuntimeError("tokenizer returned an invalid batch")
            if any(
                not isinstance(row, list) or len(row) > self._backend.max_seq_length
                for row in ids
            ):
                raise EmbeddingRuntimeError("input would be truncated by encoder")
            method = (
                self._backend.encode_query if query else self._backend.encode_document
            )
            raw = method(
                list(texts),
                prompt=prefix,
                precision="float32",
                convert_to_numpy=True,
                normalize_embeddings=False,
                show_progress_bar=False,
            ).tolist()
        except (OSError, RuntimeError, ValueError) as exc:
            raise EmbeddingRuntimeError(
                "local encoder did not return usable vectors"
            ) from exc
        if not isinstance(raw, list) or len(raw) != len(texts):
            raise EmbeddingRuntimeError("encoder returned an invalid batch")
        result: list[Vector] = []
        for row in raw:
            if not isinstance(row, list) or len(row) != self.identity.dimension:
                raise EmbeddingRuntimeError("encoder returned an invalid dimension")
            if any(type(value) not in (int, float) for value in row):
                raise EmbeddingRuntimeError("encoder returned non-numeric values")
            vector = tuple(float(value) for value in row)
            validate_vector(vector)
            result.append(vector)
        return tuple(result)

    def embed_documents(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        return self._embed(texts, query=False)

    def embed_queries(self, texts: Sequence[str]) -> tuple[Vector, ...]:
        return self._embed(texts, query=True)
