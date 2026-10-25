"""FastAPI transport with bounded raw input and validated-result SSE framing."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import hmac
import json
import logging
from typing import Annotated, Literal, cast
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.base import RequestResponseEndpoint

from labs.week_11.fixtures import NORTH, SOUTH
from labs.week_11.policy import SecurityContext, SecurityViolation, parse_question
from labs.week_12.config import Settings
from labs.week_12.service import Busy, GuardedService
from labs.week_12.store import PostgresRepository, Repository, RepositoryUnavailable

logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)


class QuestionBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    question: str = Field(min_length=1, max_length=1000)


class PublicAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    request_id: str
    status: Literal["answered", "refused"]
    answer: str
    citation_ids: tuple[str, ...]
    cache_hit: bool


class PublicError(BaseModel):
    error: str
    request_id: str


ERROR_RESPONSES: dict[int | str, dict[str, object]] = {
    code: {"model": PublicError, "description": description}
    for code, description in (
        (400, "Invalid strict question envelope"),
        (401, "Missing or invalid bearer credential"),
        (408, "Body read deadline exceeded"),
        (413, "Raw UTF-8 body exceeds 4096 bytes"),
        (415, "Content-Type must be application/json"),
        (429, "Per-principal process-local rate exhausted; Retry-After supplied"),
        (500, "Unexpected application failure"),
        (503, "Busy or dependency unavailable; Retry-After supplied"),
    )
}


async def read_question(request: Request) -> str:
    if (
        request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        != "application/json"
    ):
        raise HTTPException(415, "unsupported_media_type")
    data = bytearray()
    try:
        async with asyncio.timeout(3):
            async for chunk in request.stream():
                if len(data) + len(chunk) > 4096:
                    raise HTTPException(413, "request_too_large")
                data.extend(chunk)
    except TimeoutError as error:
        raise HTTPException(408, "body_timeout") from error
    try:
        return parse_question(data.decode("utf-8"))
    except (UnicodeError, SecurityViolation) as error:
        raise HTTPException(400, "invalid_request") from error


def create_app(
    settings: Settings | None = None,
    repository: Repository | None = None,
) -> FastAPI:
    """Create the app without import-time credentials or database connections."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configured = settings or Settings.from_env()
        app.state.settings = configured
        service = GuardedService(
            configured, repository or PostgresRepository(configured)
        )
        app.state.service = service
        try:
            yield
        finally:
            await service.close()

    app = FastAPI(
        title="Week 12 guarded RAG service",
        version="1.0.0",
        lifespan=lifespan,
        description="Local synthetic demo. Bearer secrets choose fixed identities; question JSON cannot choose scope.",
    )

    @app.middleware("http")
    async def request_metadata(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.request_id = uuid4().hex
        try:
            response = await call_next(request)
        except Exception as error:
            # Return a real failure without handing raw exception payload to an
            # outer server error logger. Cancellation (BaseException) propagates.
            logger.error(
                "rag_unexpected_error",
                extra={
                    "request_id": request.state.request_id,
                    "error_type": type(error).__name__,
                },
            )
            response = JSONResponse(
                {"error": "internal_error", "request_id": request.state.request_id},
                status_code=500,
            )
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        logger.info(
            "rag_response_prepared",
            extra={
                "request_id": request.state.request_id,
                "status_code": response.status_code,
            },
        )
        return response

    @app.exception_handler(HTTPException)
    async def expected_error(request: Request, error: HTTPException) -> JSONResponse:
        return JSONResponse(
            {"error": error.detail, "request_id": request.state.request_id},
            status_code=error.status_code,
            headers=error.headers,
        )

    async def identity(
        request: Request,
        credential: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    ) -> SecurityContext:
        configured = cast(Settings, request.app.state.settings)
        token = "" if credential is None else credential.credentials
        if len(token) <= 128 and token.isascii():
            north = hmac.compare_digest(token, configured.north_token)
            south = hmac.compare_digest(token, configured.south_token)
            if north or south:
                return SecurityContext(
                    NORTH if north else SOUTH, "analyst", request.state.request_id
                )
        raise HTTPException(401, "unauthorized", headers={"WWW-Authenticate": "Bearer"})

    async def answer(request: Request, context: SecurityContext) -> PublicAnswer:
        service = cast(GuardedService, request.app.state.service)
        retry = service.rate.consume(context)
        if retry:
            raise HTTPException(
                429, "rate_limited", headers={"Retry-After": str(retry)}
            )
        question = await read_question(request)
        try:
            result, hit = await service.ask(context, question)
        except Busy as error:
            raise HTTPException(503, "busy", headers={"Retry-After": "1"}) from error
        except (RepositoryUnavailable, TimeoutError) as error:
            raise HTTPException(
                503, "dependency_unavailable", headers={"Retry-After": "1"}
            ) from error
        return PublicAnswer(
            request_id=context.request_id,
            status="answered" if result.reason == "ok" else "refused",
            answer=result.answer,
            citation_ids=result.citation_ids,
            cache_hit=hit,
        )

    body_schema = {
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": QuestionBody.model_json_schema(),
                    "example": {
                        "question": "What are the invoice payment terms for CW-1000?"
                    },
                }
            },
        }
    }

    @app.post(
        "/v1/ask",
        response_model=PublicAnswer,
        openapi_extra=body_schema,
        responses=ERROR_RESPONSES,
    )
    async def ask(
        request: Request,
        context: Annotated[SecurityContext, Depends(identity)],
    ) -> PublicAnswer:
        return await answer(request, context)

    @app.post(
        "/v1/ask/stream",
        response_class=StreamingResponse,
        openapi_extra=body_schema,
        responses={
            **ERROR_RESPONSES,
            200: {
                "description": "Validated-result SSE: meta, result, done",
                "content": {"text/event-stream": {"schema": {"type": "string"}}},
            },
        },
    )
    async def stream(
        request: Request,
        context: Annotated[SecurityContext, Depends(identity)],
    ) -> StreamingResponse:
        result = await answer(request, context)

        async def events() -> AsyncIterator[str]:
            frames = (
                (
                    "meta",
                    {"request_id": context.request_id, "mode": "validated-result"},
                ),
                ("result", result.model_dump(mode="json")),
                ("done", {"request_id": context.request_id, "complete": True}),
            )
            for event, data in frames:
                if await request.is_disconnected():
                    return
                yield f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/health/ready")
    async def ready(request: Request) -> dict[str, str]:
        service = cast(GuardedService, request.app.state.service)
        try:
            async with asyncio.timeout(3):
                available = await service.repository.ready()
        except (RepositoryUnavailable, TimeoutError) as error:
            logger.warning(
                "rag_readiness_failed:%s", type(error.__cause__ or error).__name__
            )
            available = False
        if not available:
            raise HTTPException(503, "not_ready")
        return {"status": "ready"}

    return app
