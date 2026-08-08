from __future__ import annotations

import json
import math
import socket
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
from typing import Literal, Mapping, cast

from llm_comparison.models import (
    BaselineRequest,
    FailedObservation,
    FailureCategory,
    Metric,
    RunManifest,
    SuccessfulObservation,
    TrialResult,
)
from llm_comparison.ports import Clock, HttpResponse, HttpTransport


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{field} must be an object")
    return value


def _list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    return value


def _string(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


def _nonnegative_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    converted = float(value)
    if not math.isfinite(converted) or converted < 0:
        raise ValueError(f"{field} must be finite and nonnegative")
    return converted


def _nonnegative_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


@dataclass(frozen=True, slots=True)
class _Failure:
    category: FailureCategory
    detail: str


class LlamaServerClient:
    """Adapter for a pre-started, loopback-only llama-server process."""

    def __init__(
        self,
        *,
        manifest: RunManifest,
        transport: HttpTransport,
        clock: Clock,
    ) -> None:
        self._manifest = manifest
        self._transport = transport
        self._clock = clock

    def generate(self, request: BaselineRequest) -> TrialResult:
        readiness_started_at = self._clock.utc_now()
        failure = self._configuration_failure(request)
        if failure is not None:
            return self._failed(
                request,
                readiness_started_at,
                0.0,
                failure,
                metric_name="configuration_validation_time",
                metric_boundary="local request and manifest invariant validation",
            )

        readiness_started = self._clock.monotonic()
        try:
            failure = self._check_server(request.timeout_seconds)
        except (TimeoutError, socket.timeout) as exc:
            failure = _Failure("timeout", type(exc).__name__)
        except OSError as exc:
            failure = _Failure("transport", type(exc).__name__)
        except (JSONDecodeError, UnicodeDecodeError, ValueError, KeyError) as exc:
            failure = _Failure("protocol", type(exc).__name__)
        readiness_elapsed = max(0.0, self._clock.monotonic() - readiness_started)
        if failure is not None:
            return self._failed(
                request,
                readiness_started_at,
                readiness_elapsed,
                failure,
                metric_name="readiness_attempt_time",
                metric_boundary="health and model-identity consistency checks",
            )

        started_at = self._clock.utc_now()
        started = self._clock.monotonic()
        try:
            response = self._completion(request)
            return self._parse_completion(response, request, started_at, started)
        except (TimeoutError, socket.timeout) as exc:
            failure = _Failure("timeout", type(exc).__name__)
        except OSError as exc:
            failure = _Failure("transport", type(exc).__name__)
        except (JSONDecodeError, UnicodeDecodeError, ValueError, KeyError) as exc:
            failure = _Failure("protocol", type(exc).__name__)
        elapsed = max(0.0, self._clock.monotonic() - started)
        return self._failed(request, started_at, elapsed, failure)

    def _configuration_failure(self, request: BaselineRequest) -> _Failure | None:
        manifest = self._manifest
        if (
            request.experiment_id != manifest.experiment_id
            or request.run_id != manifest.run_id
        ):
            return _Failure("configuration", "request_manifest_identity_mismatch")
        generation = manifest.generation
        if (
            request.context_size != generation.context_size
            or request.max_output_tokens != generation.max_output_tokens
            or request.stream != generation.stream
        ):
            return _Failure(
                "configuration", "request_generation_configuration_mismatch"
            )
        if not manifest.model.artifacts:
            return _Failure("configuration", "artifact_attestation_missing")
        return None

    def _check_server(self, timeout_seconds: float) -> _Failure | None:
        base = self._manifest.adapter.base_url
        health = self._transport.request(
            method="GET",
            url=f"{base}/health",
            headers={"Accept": "application/json"},
            body=None,
            timeout_seconds=timeout_seconds,
        )
        if health.status_code != 200:
            return _Failure("not_ready", f"health_status_{health.status_code}")
        models = self._transport.request(
            method="GET",
            url=f"{base}/v1/models",
            headers={"Accept": "application/json"},
            body=None,
            timeout_seconds=timeout_seconds,
        )
        if models.status_code != 200:
            return _Failure("not_ready", f"models_status_{models.status_code}")
        parsed: object = json.loads(models.body.decode("utf-8"))
        items = _list(_mapping(parsed, "models").get("data"), "models.data")
        identities = {
            _string(_mapping(item, "model").get("id"), "model.id") for item in items
        }
        if self._manifest.adapter.expected_model_identity not in identities:
            return _Failure("configuration", "reported_model_identity_mismatch")
        return None

    def _completion(self, request: BaselineRequest) -> HttpResponse:
        payload: dict[str, object] = {
            "model": self._manifest.adapter.expected_model_identity,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "top_k": request.top_k,
            "top_p": request.top_p,
            "seed": request.seed,
            "max_tokens": request.max_output_tokens,
            "stream": request.stream,
        }
        if request.stop:
            payload["stop"] = list(request.stop)
        body = json.dumps(
            payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode("utf-8")
        return self._transport.request(
            method="POST",
            url=f"{self._manifest.adapter.base_url}{self._manifest.adapter.api_route}",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            body=body,
            timeout_seconds=request.timeout_seconds,
        )

    def _parse_completion(
        self,
        response: HttpResponse,
        request: BaselineRequest,
        started_at: datetime,
        started: float,
    ) -> TrialResult:
        if response.status_code != 200:
            elapsed = max(0.0, self._clock.monotonic() - started)
            return self._failed(
                request,
                started_at,
                elapsed,
                _Failure("server", f"completion_status_{response.status_code}"),
            )
        root: object = json.loads(response.body.decode("utf-8"))
        data = _mapping(root, "completion")
        reported_model = _string(data.get("model"), "model")
        if reported_model != self._manifest.adapter.expected_model_identity:
            raise ValueError("completion model identity mismatch")
        choices = _list(data.get("choices"), "choices")
        if len(choices) != 1:
            raise ValueError("exactly one completion choice is required")
        choice = _mapping(choices[0], "choice")
        message = _mapping(choice.get("message"), "choice.message")
        text = _string(message.get("content"), "choice.message.content")
        raw_finish_value = choice.get("finish_reason")
        raw_finish = raw_finish_value if isinstance(raw_finish_value, str) else None
        finish = (
            cast(
                "Literal['stop', 'length', 'content_filter', 'unknown']",
                raw_finish
                if raw_finish in {"stop", "length", "content_filter"}
                else "unknown",
            )
            if raw_finish is not None
            else None
        )
        metrics = [
            Metric(
                name="time_to_first_token",
                value=None,
                unit="seconds",
                boundary="non-streaming protocol",
                source="client_observed",
                unavailable_reason="non_streaming_response_has_no_first_token_boundary",
            ),
        ]
        metrics.extend(self._usage_metrics(data.get("usage")))
        metrics.extend(self._timing_metrics(data.get("timings")))
        elapsed = max(0.0, self._clock.monotonic() - started)
        metrics.insert(
            0,
            Metric(
                name="request_wall_time",
                value=elapsed,
                unit="seconds",
                boundary="HTTP dispatch through validated complete response",
                source="client_observed",
            ),
        )
        return SuccessfulObservation(
            experiment_id=request.experiment_id,
            run_id=request.run_id,
            trial_id=request.trial_id,
            prompt_suite_id=request.prompt_suite_id,
            prompt_case_id=request.prompt_case_id,
            prompt_hash=request.prompt_hash,
            generation_fingerprint=request.generation_fingerprint(),
            model_identity=self._manifest.adapter.expected_model_identity,
            started_at=started_at,
            elapsed_seconds=max(0.0, elapsed),
            generated_text=text,
            finish_reason=finish,
            raw_finish_reason=raw_finish,
            finish_reason_unavailable_reason=(
                None
                if raw_finish is not None
                else "runtime_did_not_expose_string_finish_reason"
            ),
            metrics=tuple(metrics),
        )

    @staticmethod
    def _usage_metrics(value: object) -> tuple[Metric, ...]:
        fields = ("prompt_tokens", "completion_tokens", "total_tokens")
        usage = value if isinstance(value, dict) else None
        metrics: list[Metric] = []
        for name in fields:
            try:
                measured = _nonnegative_integer(
                    usage.get(name) if usage is not None else None, f"usage.{name}"
                )
            except ValueError:
                metrics.append(
                    Metric(
                        name=name,
                        value=None,
                        unit="tokens",
                        boundary="runtime usage object",
                        source="runtime_reported",
                        unavailable_reason=f"runtime_missing_or_invalid_{name}",
                    )
                )
            else:
                metrics.append(
                    Metric(
                        name=name,
                        value=measured,
                        unit="tokens",
                        boundary="runtime usage object",
                        source="runtime_reported",
                    )
                )
        return tuple(metrics)

    @staticmethod
    def _timing_metrics(value: object) -> tuple[Metric, ...]:
        fields = (("prompt_ms", "milliseconds"), ("predicted_ms", "milliseconds"))
        timings = value if isinstance(value, dict) else None
        metrics: list[Metric] = []
        for name, unit in fields:
            try:
                measured = _nonnegative_number(
                    timings.get(name) if timings is not None else None,
                    f"timings.{name}",
                )
            except ValueError:
                metrics.append(
                    Metric(
                        name=name,
                        value=None,
                        unit=unit,
                        boundary="runtime timings object",
                        source="runtime_reported",
                        unavailable_reason=f"runtime_missing_or_invalid_{name}",
                    )
                )
            else:
                metrics.append(
                    Metric(
                        name=name,
                        value=measured,
                        unit=unit,
                        boundary="runtime timings object",
                        source="runtime_reported",
                    )
                )
        return tuple(metrics)

    def _failed(
        self,
        request: BaselineRequest,
        started_at: datetime,
        elapsed: float,
        failure: _Failure,
        metric_name: str = "request_wall_time",
        metric_boundary: str = "HTTP dispatch through failed response validation",
    ) -> FailedObservation:
        return FailedObservation(
            experiment_id=request.experiment_id,
            run_id=request.run_id,
            trial_id=request.trial_id,
            prompt_suite_id=request.prompt_suite_id,
            prompt_case_id=request.prompt_case_id,
            prompt_hash=request.prompt_hash,
            generation_fingerprint=request.generation_fingerprint(),
            model_identity=self._manifest.adapter.expected_model_identity,
            started_at=started_at,
            elapsed_seconds=max(0.0, elapsed),
            category=failure.category,
            sanitized_detail=failure.detail,
            metrics=(
                Metric(
                    name=metric_name,
                    value=max(0.0, elapsed),
                    unit="seconds",
                    boundary=metric_boundary,
                    source="client_observed",
                ),
            ),
        )
