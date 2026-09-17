"""Offline excerpts of existing seller-price validation; see docs/PROVENANCE.md."""
from __future__ import annotations

import json
from typing import Any

FREE_NPAY_SENTINEL = 16_777_215

def _seller_price(seller: dict[str, Any]) -> tuple[int, int, int] | None:
    try:
        product_price = int(seller.get("mobilePrice") or seller.get("minPrice") or 0)
        raw_shipping_fee = seller.get("deliveryPrice")
        if raw_shipping_fee is None:
            return None
        shipping_fee = int(raw_shipping_fee)
        price_order = int(seller.get("priceOrder") or 0)
    except (TypeError, ValueError):
        return None
    if product_price <= 0 or shipping_fee < 0 or shipping_fee == FREE_NPAY_SENTINEL:
        return None
    final_price = product_price + shipping_fee
    if price_order not in (0, final_price):
        return None
    return product_price, shipping_fee, final_price


def parse_price_compare_sellers(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every seller row, including rows that cannot be normalized."""
    sellers: list[dict[str, Any]] = []
    seen: set[str] = set()
    for key in (
        "openMarketList",
        "largeMallList",
        "shopDanawaList",
        "specialMallList",
        "generalMallList",
    ):
        rows = payload.get(key) or []
        if not isinstance(rows, list):
            continue
        for seller in rows:
            if not isinstance(seller, dict):
                continue
            fingerprint = json.dumps(
                seller, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            row = {**seller, "sellerListName": key}
            price = _seller_price(seller)
            if price is None:
                raw_shipping = seller.get("deliveryPrice")
                if raw_shipping is None:
                    reason = "shipping_fee_missing"
                elif str(raw_shipping) == str(FREE_NPAY_SENTINEL):
                    reason = "shipping_fee_npay_sentinel"
                else:
                    reason = "invalid_price_components"
                row.update({"priceIsComplete": False, "normalizationReason": reason})
            else:
                product_price, shipping_fee, final_price = price
                row.update(
                    {
                        "priceIsComplete": True,
                        "normalizationReason": "accepted",
                        "parsedProductPrice": product_price,
                        "parsedShippingFee": shipping_fee,
                        "parsedFinalPrice": final_price,
                    }
                )
            sellers.append(row)
    return sellers


def _seller_identity(seller: dict[str, Any], ordinal: int) -> tuple[str, str]:
    company_code = str(seller.get("companyCode") or "").strip()
    seller_code = str(
        seller.get("linkProdCode") or seller.get("goodsCode") or ""
    ).strip()
    if company_code or seller_code:
        return company_code, seller_code
    shop_name = "".join(str(seller.get("shopName") or "").casefold().split())
    if shop_name:
        return "__merchant__", shop_name
    return "__row__", str(ordinal)


def _incomplete_price_floor(seller: dict[str, Any]) -> int | None:
    if seller.get("priceIsComplete") is True:
        return None
    if str(seller.get("normalizationReason") or "") not in {
        "shipping_fee_missing",
        "shipping_fee_npay_sentinel",
    }:
        return None
    try:
        floor = int(seller.get("mobilePrice") or seller.get("minPrice") or 0)
    except (TypeError, ValueError):
        return None
    return floor if floor > 0 else None


def _is_conditional_shipping_sentinel(seller: dict[str, Any]) -> bool:
    if (
        seller.get("priceIsComplete") is True
        or str(seller.get("normalizationReason") or "")
        != "shipping_fee_npay_sentinel"
        or seller.get("differentialPostYN") != "Y"
    ):
        return False
    floor = _incomplete_price_floor(seller)
    try:
        shipping_fee = int(seller.get("deliveryPrice"))
        price_order = int(seller.get("priceOrder"))
    except (TypeError, ValueError):
        return False
    return (
        shipping_fee == FREE_NPAY_SENTINEL
        and floor is not None
        and price_order == floor
    )


def _seller_table_settlement(
    sellers: list[dict[str, Any]],
) -> tuple[dict[str, Any], set[tuple[str, str]]]:
    complete_rows = [
        seller for seller in sellers if seller.get("priceIsComplete") is True
    ]
    complete_prices = [int(seller["parsedFinalPrice"]) for seller in complete_rows]
    best_complete_final_price = min(complete_prices) if complete_prices else None
    incomplete_rows = [
        seller for seller in sellers if seller.get("priceIsComplete") is not True
    ]
    conditional_shipping_count = 0
    competing_incomplete_rows: list[dict[str, Any]] = []
    for seller in incomplete_rows:
        if _is_conditional_shipping_sentinel(seller):
            conditional_shipping_count += 1
        else:
            competing_incomplete_rows.append(seller)
    incomplete_floors = [
        _incomplete_price_floor(seller) for seller in competing_incomplete_rows
    ]
    unresolved_floor_complete = all(
        floor is not None for floor in incomplete_floors
    )
    lowest_unresolved_floor = (
        min(int(floor) for floor in incomplete_floors if floor is not None)
        if incomplete_floors and any(floor is not None for floor in incomplete_floors)
        else None
    )
    prices_by_seller: dict[tuple[str, str], set[tuple[int, int, int]]] = {}
    for ordinal, seller in enumerate(sellers):
        if seller.get("priceIsComplete") is not True:
            continue
        prices_by_seller.setdefault(_seller_identity(seller, ordinal), set()).add(
            (
                int(seller["parsedProductPrice"]),
                int(seller["parsedShippingFee"]),
                int(seller["parsedFinalPrice"]),
            )
        )
    conflicting_seller_keys = {
        key for key, prices in prices_by_seller.items() if len(prices) > 1
    }
    has_price_conflict = bool(conflicting_seller_keys)
    winner_settled = bool(
        best_complete_final_price is not None
        and not has_price_conflict
        and unresolved_floor_complete
        and all(
            int(floor) > int(best_complete_final_price)
            for floor in incomplete_floors
            if floor is not None
        )
    )
    return (
        {
            "seller_table_row_count": len(sellers),
            "complete_seller_count": len(complete_rows),
            "incomplete_seller_count": len(incomplete_rows),
            "seller_table_conditional_shipping_count": conditional_shipping_count,
            "seller_table_competing_incomplete_count": len(competing_incomplete_rows),
            "seller_table_complete": len(complete_rows) == len(sellers),
            "seller_table_best_complete_final_price": best_complete_final_price,
            "seller_table_unresolved_floor_complete": unresolved_floor_complete,
            "seller_table_lowest_unresolved_price_floor": lowest_unresolved_floor,
            "seller_table_has_price_conflict": has_price_conflict,
            "seller_table_winner_settled": winner_settled,
        },
        conflicting_seller_keys,
    )
