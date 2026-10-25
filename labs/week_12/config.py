"""Validated local settings; credentials enter through bounded mounted files."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
import os
import re

from labs.week_11.assistant import Limits

SECRET = re.compile(r"[A-Za-z0-9_-]{32,128}")
NAME = re.compile(r"[A-Za-z0-9_.-]{1,128}")


def read_secret(path: str | Path) -> str:
    """Accept a generated URL-safe secret, with an optional final newline."""
    try:
        with Path(path).open("rb") as handle:
            value = handle.read(130).decode("ascii").removesuffix("\n")
    except (OSError, UnicodeError) as error:
        raise ValueError("configuration_invalid") from error
    if SECRET.fullmatch(value) is None:
        raise ValueError("configuration_invalid")
    return value


@dataclass(frozen=True)
class Settings:
    password: str = field(repr=False)
    north_token: str = field(repr=False)
    south_token: str = field(repr=False)
    host: str = "db"
    port: int = 5432
    database: str = "rag_demo"
    user: str = "rag_reader"
    context_chars: int = 1400
    requests_per_minute: int = 12
    cache_seconds: int = 15

    def __post_init__(self) -> None:
        for secret in (self.password, self.north_token, self.south_token):
            if not isinstance(secret, str) or SECRET.fullmatch(secret) is None:
                raise ValueError("configuration_invalid")
        if self.north_token == self.south_token:
            raise ValueError("configuration_invalid")
        for name in (self.host, self.database, self.user):
            if not isinstance(name, str) or NAME.fullmatch(name) is None:
                raise ValueError("configuration_invalid")
        for value, minimum, maximum in (
            (self.port, 1, 65535),
            (self.requests_per_minute, 1, 120),
            (self.cache_seconds, 1, 60),
        ):
            if type(value) is not int or not minimum <= value <= maximum:
                raise ValueError("configuration_invalid")
        Limits(self.context_chars)

    @classmethod
    def from_env(cls, values: Mapping[str, str] | None = None) -> Settings:
        """Load only the documented W12 variables; never print the settings."""
        env = os.environ if values is None else values

        def integer(name: str, default: int) -> int:
            value = env.get(name, str(default))
            if re.fullmatch(r"[0-9]{1,5}", value) is None:
                raise ValueError("configuration_invalid")
            return int(value)

        return cls(
            password=read_secret(
                env.get("W12_DB_PASSWORD_FILE", ".runtime/week12-secrets/db_app")
            ),
            north_token=read_secret(
                env.get("W12_NORTH_TOKEN_FILE", ".runtime/week12-secrets/north_token")
            ),
            south_token=read_secret(
                env.get("W12_SOUTH_TOKEN_FILE", ".runtime/week12-secrets/south_token")
            ),
            host=env.get("W12_DB_HOST", "db"),
            port=integer("W12_DB_PORT", 5432),
            database=env.get("W12_DB_NAME", "rag_demo"),
            user=env.get("W12_DB_USER", "rag_reader"),
            context_chars=integer("W12_CONTEXT_CHARS", 1400),
            requests_per_minute=integer("W12_REQUESTS_PER_MINUTE", 12),
            cache_seconds=integer("W12_CACHE_SECONDS", 15),
        )
