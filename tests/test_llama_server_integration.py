from __future__ import annotations

import json
import os

import pytest

from llm_comparison.models import AdapterConfig
from llm_comparison.transport import UrllibHttpTransport


def test_opt_in_llama_server_health_identity_and_smoke() -> None:
    """Opt-in contract/fit evidence for one externally managed model block."""
    if os.environ.get("LLM_COMPARISON_INTEGRATION") != "1":
        pytest.skip("set LLM_COMPARISON_INTEGRATION=1 for the local smoke contract")
    required = (
        "LLAMA_SERVER_ENDPOINT",
        "LLAMA_EXPECTED_MODEL",
        "LLAMA_RUNTIME_REVISION",
        "LLAMA_RUNTIME_SHA256",
        "LLAMA_MODEL_REVISION",
        "LLAMA_MODEL_SHA256",
    )
    values = {name: os.environ.get(name, "") for name in required}
    if any(not value for value in values.values()):
        pytest.fail("all integration provenance environment variables are required")
    for name in ("LLAMA_RUNTIME_SHA256", "LLAMA_MODEL_SHA256"):
        value = values[name]
        if len(value) != 64 or any(
            character not in "0123456789abcdef" for character in value
        ):
            pytest.fail(f"{name} must be a lowercase SHA-256")

    config = AdapterConfig(
        base_url=values["LLAMA_SERVER_ENDPOINT"],
        expected_model_identity=values["LLAMA_EXPECTED_MODEL"],
        adapter_version="integration-v1",
    )
    transport = UrllibHttpTransport()
    health = transport.request(
        method="GET",
        url=f"{config.base_url}/health",
        headers={"Accept": "application/json"},
        body=None,
        timeout_seconds=10.0,
    )
    assert health.status_code == 200
    models = transport.request(
        method="GET",
        url=f"{config.base_url}/v1/models",
        headers={"Accept": "application/json"},
        body=None,
        timeout_seconds=10.0,
    )
    assert models.status_code == 200
    model_data = json.loads(models.body)
    assert config.expected_model_identity in {item["id"] for item in model_data["data"]}
    body = json.dumps(
        {
            "model": config.expected_model_identity,
            "messages": [{"role": "user", "content": "Reply with OK."}],
            "max_tokens": 8,
            "stream": False,
            "temperature": 0.0,
        },
        separators=(",", ":"),
    ).encode()
    smoke = transport.request(
        method="POST",
        url=f"{config.base_url}/v1/chat/completions",
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        body=body,
        timeout_seconds=30.0,
    )
    assert smoke.status_code == 200
