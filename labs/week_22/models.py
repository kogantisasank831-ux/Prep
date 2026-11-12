"""Closed domain contracts for the Week 22 MCP server."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Identifier = Annotated[
    str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
]
RiskLevel = Literal["low", "medium", "high"]
SupplierStatus = Literal["approved", "conditional", "blocked"]
LookupStatus = Literal["found", "not_found", "forbidden"]


class StrictModel(BaseModel):
    """Reject coercion, unknown fields and mutation."""

    model_config = ConfigDict(
        allow_inf_nan=False, extra="forbid", frozen=True, strict=True
    )


class Principal(StrictModel):
    """Identity and scopes supplied by a trusted transport/authentication layer."""

    actor_id: Identifier
    tenant_id: Identifier
    scopes: tuple[Identifier, ...]


class SupplierRecord(StrictModel):
    """A deliberately small supplier view safe for the teaching tool."""

    supplier_id: Identifier
    display_name: Annotated[str, Field(min_length=1, max_length=120)]
    status: SupplierStatus
    risk: RiskLevel


class SupplierLookupResult(StrictModel):
    """Stable structured output that does not reveal another tenant's records."""

    status: LookupStatus
    supplier: SupplierRecord | None
    message: Annotated[str, Field(min_length=1, max_length=160)]

    @model_validator(mode="after")
    def supplier_matches_status(self) -> SupplierLookupResult:
        if self.status == "found" and self.supplier is None:
            raise ValueError("found_result_requires_supplier")
        if self.status != "found" and self.supplier is not None:
            raise ValueError("non_found_result_cannot_include_supplier")
        return self
