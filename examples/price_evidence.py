from __future__ import annotations

from typing import Any, Mapping


def price_comparison_row_is_publishable(
    *,
    source_type: str,
    evidence: Mapping[str, Any],
    destination_url: str,
    merchant_name: str,
    product_price: int,
    shipping_fee: int | None,
    final_price: int,
) -> bool:
    """Return whether one aggregator seller row proves a public price.

    A fully normalized seller table keeps the legacy behavior.  A partial
    table may publish only its cheapest complete row, and only when every
    unresolved row has a conservative price floor strictly above that winner.
    The merchant destination must be resolved explicitly; a comparison-site
    bridge URL is evidence, not a public purchase destination.
    """
    if str(source_type or "") != "price_comparison":
        return False
    if evidence.get("price_is_complete") is not True:
        return False
    if evidence.get("seller_table_has_price_conflict") is True:
        return False
    if evidence.get("seller_alias_conflict") is True:
        return False

    explicit_destination = str(evidence.get("destination_url") or "").strip()
    if not explicit_destination.startswith("https://"):
        return False
    if str(destination_url or "").strip() != explicit_destination:
        return False
    if not str(merchant_name or "").strip() or shipping_fee is None:
        return False

    table_is_complete = evidence.get("seller_table_complete") is True
    settled_partial_winner = (
        evidence.get("seller_table_winner_settled") is True
        and evidence.get("seller_table_unresolved_floor_complete") is True
        and evidence.get("seller_row_is_table_best") is True
    )
    if not table_is_complete and not settled_partial_winner:
        return False

    try:
        expected = (
            int(evidence.get("reported_product_price")),
            int(evidence.get("reported_shipping_fee")),
            int(evidence.get("reported_final_price")),
        )
        actual = (
            int(product_price),
            int(shipping_fee),
            int(final_price),
        )
    except (TypeError, ValueError):
        return False
    return (
        expected == actual
        and actual[0] > 0
        and actual[1] >= 0
        and actual[0] + actual[1] == actual[2]
    )
