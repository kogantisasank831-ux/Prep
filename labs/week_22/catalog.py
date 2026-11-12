"""Synthetic tenant-scoped supplier catalog used by the MCP lab."""

from __future__ import annotations

from labs.week_22.models import Principal, SupplierLookupResult, SupplierRecord


_RECORDS: dict[tuple[str, str], SupplierRecord] = {
    ("tenant-acme", "supplier-101"): SupplierRecord(
        supplier_id="supplier-101",
        display_name="Northwind Components",
        status="approved",
        risk="low",
    ),
    ("tenant-acme", "supplier-202"): SupplierRecord(
        supplier_id="supplier-202",
        display_name="Contoso Industrial",
        status="conditional",
        risk="medium",
    ),
    ("tenant-bravo", "supplier-909"): SupplierRecord(
        supplier_id="supplier-909",
        display_name="Fabrikam Logistics",
        status="blocked",
        risk="high",
    ),
}


class SupplierCatalog:
    """Authorize every lookup and filter by the authenticated tenant."""

    def lookup(self, principal: Principal, supplier_id: str) -> SupplierLookupResult:
        if "supplier:read" not in principal.scopes:
            return SupplierLookupResult(
                status="forbidden",
                supplier=None,
                message="The authenticated principal lacks supplier:read.",
            )
        supplier = _RECORDS.get((principal.tenant_id, supplier_id))
        if supplier is None:
            return SupplierLookupResult(
                status="not_found",
                supplier=None,
                message="No supplier is visible for this identifier.",
            )
        return SupplierLookupResult(
            status="found",
            supplier=supplier,
            message="Supplier record returned for the authenticated tenant.",
        )
