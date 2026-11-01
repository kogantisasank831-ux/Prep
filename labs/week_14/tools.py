"""Shared synthetic tools used by both Week 14 controllers."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from labs.week_14.models import (
    Action,
    ContractTerms,
    Fact,
    InvestigationState,
    PriceVariance,
    ProcurementCase,
    PurchaseOrder,
    ReferencePrice,
    Supplier,
)


class ToolFailure(Exception):
    """A controlled fixture-tool failure."""


CASES: dict[str, ProcurementCase] = {
    "price-spike": ProcurementCase("price-spike", "PO-1401"),
    "stable-price": ProcurementCase("stable-price", "PO-1402"),
    "missing-terms": ProcurementCase("missing-terms", "PO-1403"),
}

ORDERS: dict[str, PurchaseOrder] = {
    "PO-1401": PurchaseOrder(
        "PO-1401", "SUP-014", "STEEL-A", Decimal("2.20"), "USD", "kg"
    ),
    "PO-1402": PurchaseOrder(
        "PO-1402", "SUP-015", "RESIN-B", Decimal("2.04"), "USD", "kg"
    ),
    "PO-1403": PurchaseOrder(
        "PO-1403", "SUP-016", "COPPER-C", Decimal("3.30"), "USD", "kg"
    ),
}

SUPPLIERS: dict[str, Supplier] = {
    "SUP-014": Supplier("SUP-014", "North Demo Metals", "active"),
    "SUP-015": Supplier("SUP-015", "Blue Demo Resins", "active"),
    "SUP-016": Supplier("SUP-016", "Copper Demo Works", "active"),
}

REFERENCE_PRICES: dict[str, ReferencePrice] = {
    "STEEL-A": ReferencePrice("STEEL-A", Decimal("2.00"), "USD", "kg", "2026-10-01"),
    "RESIN-B": ReferencePrice("RESIN-B", Decimal("2.00"), "USD", "kg", "2026-10-01"),
    "COPPER-C": ReferencePrice("COPPER-C", Decimal("3.00"), "USD", "kg", "2026-10-01"),
}

CONTRACT_TERMS: dict[str, ContractTerms] = {
    "PO-1401": ContractTerms(
        "PO-1401",
        True,
        Decimal("5.00"),
        "Unit-price changes above 5.00% require procurement review.",
    ),
    "PO-1402": ContractTerms(
        "PO-1402",
        True,
        Decimal("5.00"),
        "Unit-price changes above 5.00% require procurement review.",
    ),
    "PO-1403": ContractTerms("PO-1403", False, None, ""),
}

MODELED_TOOL_LATENCY_MS: dict[Action, int] = {
    Action.LOAD_ORDER: 5,
    Action.LOOKUP_SUPPLIER: 3,
    Action.GET_REFERENCE_PRICE: 4,
    Action.CALCULATE_VARIANCE: 2,
    Action.SEARCH_CONTRACT_TERMS: 6,
}


@dataclass
class FixtureTools:
    """A shared executor with deterministic call/latency accounting."""

    calls: int = 0
    modeled_latency_ms: int = 0

    def execute(self, action: Action, state: InvestigationState) -> Fact:
        if action not in MODELED_TOOL_LATENCY_MS:
            raise ToolFailure("unsupported_tool_action")
        self.calls += 1
        self.modeled_latency_ms += MODELED_TOOL_LATENCY_MS[action]
        if action is Action.LOAD_ORDER:
            try:
                return ORDERS[state.case.purchase_order_id]
            except KeyError as error:
                raise ToolFailure("order_not_found") from error
        if state.order is None:
            raise ToolFailure("order_required")
        if action is Action.LOOKUP_SUPPLIER:
            try:
                return SUPPLIERS[state.order.supplier_id]
            except KeyError as error:
                raise ToolFailure("supplier_not_found") from error
        if action is Action.GET_REFERENCE_PRICE:
            try:
                return REFERENCE_PRICES[state.order.commodity_id]
            except KeyError as error:
                raise ToolFailure("reference_price_not_found") from error
        if action is Action.SEARCH_CONTRACT_TERMS:
            return CONTRACT_TERMS.get(
                state.order.purchase_order_id,
                ContractTerms(state.order.purchase_order_id, False, None, ""),
            )
        if action is Action.CALCULATE_VARIANCE:
            return self._variance(state)
        raise ToolFailure("unsupported_tool_action")

    @staticmethod
    def _variance(state: InvestigationState) -> PriceVariance:
        order = state.order
        reference = state.reference_price
        if order is None or reference is None:
            raise ToolFailure("order_and_reference_required")
        if order.currency != reference.currency or order.unit != reference.unit:
            raise ToolFailure("prices_not_comparable")
        if reference.amount <= 0:
            raise ToolFailure("reference_price_invalid")
        with localcontext() as context:
            context.prec = 28
            absolute = order.current_price - reference.amount
            percent = (absolute / reference.amount) * Decimal("100")
            quantizer = Decimal("0.01")
            return PriceVariance(
                absolute.quantize(quantizer, rounding=ROUND_HALF_EVEN),
                percent.quantize(quantizer, rounding=ROUND_HALF_EVEN),
                order.currency,
                order.unit,
            )


def apply_fact(state: InvestigationState, action: Action, fact: Fact) -> None:
    """Assign a typed tool result to the matching state slot."""
    if action is Action.LOAD_ORDER and isinstance(fact, PurchaseOrder):
        state.order = fact
    elif action is Action.LOOKUP_SUPPLIER and isinstance(fact, Supplier):
        state.supplier = fact
    elif action is Action.GET_REFERENCE_PRICE and isinstance(fact, ReferencePrice):
        state.reference_price = fact
    elif action is Action.CALCULATE_VARIANCE and isinstance(fact, PriceVariance):
        state.variance = fact
    elif action is Action.SEARCH_CONTRACT_TERMS and isinstance(fact, ContractTerms):
        state.contract_terms = fact
    else:
        raise ToolFailure("tool_result_mismatch")
    state.completed.add(action)
    state.last_error = None
