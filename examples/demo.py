"""Portfolio-only wiring over synthetic rows; no collector, database, or LLM."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from price_evidence import price_comparison_row_is_publishable
from seller_table import (
    _seller_identity,
    _seller_table_settlement,
    parse_price_compare_sellers,
)


def evaluate(payload: dict) -> dict:
    """Adapt the original collector's evidence wiring to fixed offline URLs."""
    sellers = parse_price_compare_sellers(payload)
    table, conflicts = _seller_table_settlement(sellers)
    eligible = []
    for ordinal, seller in enumerate(sellers):
        complete = seller['priceIsComplete'] is True
        destination = f'https://shop.example.test/item/{ordinal}'
        product = seller.get('parsedProductPrice', 0)
        shipping = seller.get('parsedShippingFee')
        final = seller.get('parsedFinalPrice', 0)
        evidence = {
            **table,
            'destination_url': destination,
            'price_is_complete': complete,
            'seller_row_is_table_best': complete and final == table['seller_table_best_complete_final_price'],
            'seller_alias_conflict': _seller_identity(seller, ordinal) in conflicts,
            'reported_product_price': product,
            'reported_shipping_fee': shipping,
            'reported_final_price': final,
        }
        if price_comparison_row_is_publishable(
            source_type='price_comparison', evidence=evidence,
            destination_url=destination, merchant_name=seller.get('shopName', ''),
            product_price=product, shipping_fee=shipping, final_price=final,
        ):
            eligible.append(seller['shopName'])
    return {
        'rows_preserved': len(sellers),
        'complete_rows': table['complete_seller_count'],
        'winner_settled': table['seller_table_winner_settled'],
        'gate_eligible': eligible,
    }


def run_examples() -> dict:
    scenarios = json.loads(Path(__file__).with_name('scenarios.json').read_text(encoding='utf-8'))
    return {case['id']: evaluate(case['payload']) for case in scenarios}


if __name__ == '__main__':
    print(json.dumps(run_examples(), ensure_ascii=False, indent=2))
