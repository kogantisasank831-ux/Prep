"""Required real PostgreSQL/pgvector checks. Run explicitly against the CI lab."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from dataclasses import replace
import json
import os
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb
import pytest

from labs.week_11.assistant import Limits, REFUSAL, SecuredResult
from labs.week_11.fixtures import NORTH, QUESTION, SOUTH
from labs.week_11.policy import SecurityContext
from labs.week_12.cli import bootstrap
from labs.week_12.config import Settings, read_secret
from labs.week_12.service import GuardedService, compute_answer
from labs.week_12.store import PostgresRepository, Snapshot

if os.environ.get("W12_INTEGRATION") != "1":
    raise RuntimeError(
        "Explicitly enable W12_INTEGRATION=1 for the real isolated Week 12 database; no skipped integration gate."
    )


def configured() -> Settings:
    settings = Settings.from_env()
    if settings.database != "rag_demo" or settings.host not in (
        "127.0.0.1",
        "localhost",
    ):
        raise RuntimeError(
            "Use the isolated loopback CI/Compose database, never a remote database."
        )
    return settings


@pytest.fixture
def admin() -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    settings = configured()
    with psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user="postgres",
        password=read_secret(Path(".runtime/week12-secrets/db_admin")),
        autocommit=True,
    ) as connection:
        yield connection


def ctx(tenant: str = NORTH, principal: str = "analyst") -> SecurityContext:
    return SecurityContext(tenant, principal, "postgres-check")


def test_actual_extension_schema_and_persisted_vectors(
    admin: psycopg.Connection[tuple[object, ...]],
) -> None:
    assert asyncio.run(PostgresRepository(configured()).ready()) is True
    version = admin.execute(
        "SELECT extversion FROM pg_extension WHERE extname='vector'"
    ).fetchone()
    assert version is not None and str(version[0]).startswith("0.8.")
    values = admin.execute(
        "SELECT vector_dims(embedding), embedding_contract FROM week12_chunks"
    ).fetchall()
    assert len(values) == 5 and all(row == (32, "token-hash32-l2/v1") for row in values)


def test_real_vector_query_keeps_tenants_and_grants_separate() -> None:
    async def run() -> None:
        repo = PostgresRepository(configured())
        north, south, denied = (
            await repo.snapshot(ctx(), QUESTION),
            await repo.snapshot(ctx(SOUTH), QUESTION),
            await repo.snapshot(ctx(principal="ungranted"), QUESTION),
        )
        assert north.chunks and south.chunks and denied.chunks == ()
        assert all(
            c.tenant_id == NORTH and c.document_id not in {"PRIVATE", "ADDENDUM"}
            for c in north.chunks
        )
        assert all(c.tenant_id == SOUTH for c in south.chunks)
        service = GuardedService(configured(), repo)
        try:
            a, _ = await service.ask(ctx(), QUESTION)
            b, _ = await service.ask(ctx(SOUTH), QUESTION)
            assert "Net 30" in a.answer and "Net 15" not in a.answer
            assert "Net 15" in b.answer and "Net 30" not in b.answer
        finally:
            await service.close()

    asyncio.run(run())


def test_reader_cannot_update_or_create_tables() -> None:
    async def run() -> None:
        repo = PostgresRepository(configured())
        async with await repo.connect() as connection:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                await connection.execute(
                    "UPDATE week12_documents SET state='quarantined' WHERE false"
                )
            await connection.rollback()
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                await connection.execute("CREATE TABLE week12_forbidden(value integer)")
            await connection.rollback()

    asyncio.run(run())


def test_question_cannot_become_sql_and_unknown_identity_denies(
    admin: psycopg.Connection[tuple[object, ...]],
) -> None:
    async def run() -> None:
        repo = PostgresRepository(configured())
        result = await repo.snapshot(ctx(), "invoice'; DROP TABLE week12_chunks; --")
        assert all(c.tenant_id == NORTH for c in result.chunks)
        assert (
            await repo.snapshot(ctx(principal="analyst_OR_true"), QUESTION)
        ).chunks == ()

    asyncio.run(run())
    assert admin.execute("SELECT count(*) FROM week12_chunks").fetchone() == (5,)


def test_metadata_tamper_is_removed_before_vector_selection(
    admin: psycopg.Connection[tuple[object, ...]],
) -> None:
    row = admin.execute(
        "SELECT representation FROM week12_chunks WHERE tenant_id=%s AND document_id='INVOICE'",
        (NORTH,),
    ).fetchone()
    assert row is not None
    original = row[0]
    changed = json.loads(json.dumps(original))
    changed["metadata"][0][1] = '["page:2/block:1"]'
    try:
        admin.execute(
            "UPDATE week12_chunks SET representation=%s WHERE tenant_id=%s AND document_id='INVOICE'",
            (Jsonb(changed), NORTH),
        )
        result = asyncio.run(PostgresRepository(configured()).snapshot(ctx(), QUESTION))
        assert all(c.document_id != "INVOICE" for c in result.chunks)
    finally:
        admin.execute(
            "UPDATE week12_chunks SET representation=%s WHERE tenant_id=%s AND document_id='INVOICE'",
            (Jsonb(original), NORTH),
        )


def test_committed_revocation_during_compute_is_seen_by_new_transaction(
    admin: psycopg.Connection[tuple[object, ...]],
) -> None:
    def revoke(
        context: SecurityContext, question: str, data: Snapshot, limits: Limits
    ) -> SecuredResult:
        result = compute_answer(context, question, data, limits)
        # The test admin is intentionally separate from the read-only service role.
        settings = configured()
        with psycopg.connect(
            host=settings.host,
            port=settings.port,
            dbname=settings.database,
            user="postgres",
            password=read_secret(".runtime/week12-secrets/db_admin"),
        ) as connection:
            connection.execute(
                "UPDATE week12_documents SET readers='{}' WHERE tenant_id=%s AND document_id='INVOICE'",
                (NORTH,),
            )
        return result

    async def run() -> None:
        service = GuardedService(
            configured(), PostgresRepository(configured()), compute=revoke
        )
        try:
            result, hit = await service.ask(ctx(), QUESTION)
            assert (
                result.answer == REFUSAL
                and result.reason == "source_changed"
                and hit is False
            )
        finally:
            await service.close()

    try:
        asyncio.run(run())
    finally:
        admin.execute(
            "UPDATE week12_documents SET readers=%s WHERE tenant_id=%s AND document_id='INVOICE'",
            (["analyst"], NORTH),
        )


def test_cached_success_does_not_survive_changed_grant(
    admin: psycopg.Connection[tuple[object, ...]],
) -> None:
    async def run() -> None:
        service = GuardedService(configured(), PostgresRepository(configured()))
        try:
            first, hit = await service.ask(ctx(), QUESTION)
            assert "Net 30" in first.answer and hit is False
            admin.execute(
                "UPDATE week12_documents SET readers='{}' WHERE tenant_id=%s AND document_id='INVOICE'",
                (NORTH,),
            )
            next_result, next_hit = await service.ask(ctx(), QUESTION)
            assert "Net 30" not in next_result.answer and next_hit is False
        finally:
            await service.close()

    try:
        asyncio.run(run())
    finally:
        admin.execute(
            "UPDATE week12_documents SET readers=%s WHERE tenant_id=%s AND document_id='INVOICE'",
            (["analyst"], NORTH),
        )


def test_bootstrap_repeat_is_idempotent_and_conflicts_preserve_state(
    admin: psycopg.Connection[tuple[object, ...]],
) -> None:
    directory = Path(".runtime/week12-secrets")
    bootstrap(directory / "db_admin", directory / "db_app")
    assert admin.execute("SELECT count(*) FROM week12_chunks").fetchone() == (5,)
    try:
        admin.execute(
            "UPDATE week12_documents SET state='quarantined' WHERE tenant_id=%s AND document_id='INVOICE'",
            (NORTH,),
        )
        with pytest.raises(ValueError, match="seed_policy_conflict"):
            bootstrap(directory / "db_admin", directory / "db_app")
        assert admin.execute(
            "SELECT state FROM week12_documents WHERE tenant_id=%s AND document_id='INVOICE'",
            (NORTH,),
        ).fetchone() == ("quarantined",)
    finally:
        admin.execute(
            "UPDATE week12_documents SET state='approved' WHERE tenant_id=%s AND document_id='INVOICE'",
            (NORTH,),
        )


def test_context_budget_and_refusal_still_hold_over_actual_storage() -> None:
    async def run() -> None:
        service = GuardedService(
            replace(configured(), context_chars=2), PostgresRepository(configured())
        )
        try:
            result, hit = await service.ask(ctx(), QUESTION)
            assert result.answer == REFUSAL and result.citation_ids == () and not hit
        finally:
            await service.close()

    asyncio.run(run())
