"""Offline regression checks; all prices, sellers and URLs are synthetic."""
import copy
import json
import sys
import unittest
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples'
sys.path.insert(0, str(EXAMPLES))
from demo import evaluate, run_examples
from price_evidence import price_comparison_row_is_publishable
from seller_table import parse_price_compare_sellers


class PriceGateTest(unittest.TestCase):
    def test_documented_scenarios(self):
        expected = json.loads((EXAMPLES / 'expected.json').read_text(encoding='utf-8'))
        actual = run_examples()
        self.assertEqual(set(actual), set(expected))
        for name in expected:
            with self.subTest(scenario=name):
                self.assertEqual(actual[name], expected[name])

    def test_price_evidence_must_agree(self):
        evidence = {
            'price_is_complete': True, 'seller_table_complete': True,
            'destination_url': 'https://shop.example.test/item/a',
            'reported_product_price': 12000, 'reported_shipping_fee': 3000,
            'reported_final_price': 15000,
        }
        args = dict(source_type='price_comparison', evidence=evidence,
                    destination_url=evidence['destination_url'], merchant_name='합성 판매처',
                    product_price=12000, shipping_fee=3000, final_price=15000)
        self.assertTrue(price_comparison_row_is_publishable(**args))
        for patch in (
            {'shipping_fee': None}, {'shipping_fee': -1}, {'product_price': 0},
            {'final_price': 14000}, {'merchant_name': ''}, {'source_type': 'community'},
            {'destination_url': 'https://shop.example.test/item/different'},
            {'evidence': {**evidence, 'reported_final_price': 'unknown'}},
            {'evidence': {**evidence, 'seller_alias_conflict': True}},
            {'evidence': {**evidence, 'seller_table_has_price_conflict': True}},
            {'evidence': {**evidence, 'price_is_complete': False}},
        ):
            with self.subTest(patch=patch):
                self.assertFalse(price_comparison_row_is_publishable(**{**args, **patch}))

    def test_conditional_row_does_not_hide_another_unknown_row(self):
        cases = json.loads((EXAMPLES / 'scenarios.json').read_text(encoding='utf-8'))
        payload = copy.deepcopy(next(c['payload'] for c in cases if c['id'] == 'exact_conditional'))
        unknown = next(c['payload']['openMarketList'][1] for c in cases if c['id'] == 'partial_lower')
        payload['openMarketList'].append(unknown)
        result = evaluate(payload)
        self.assertEqual(result['gate_eligible'], [])
        self.assertEqual(result['rows_preserved'], 3)

    def test_empty_unknown_and_duplicate_rows(self):
        self.assertEqual(evaluate({})['gate_eligible'], [])
        row = dict(shopName='합성 판매처', mobilePrice=12000, deliveryPrice=None)
        payload = {'openMarketList': [row, dict(row)]}
        before = copy.deepcopy(payload)
        parsed = parse_price_compare_sellers(payload)
        self.assertEqual(payload, before)
        self.assertEqual(len(parsed), 1)
        self.assertFalse(parsed[0]['priceIsComplete'])
        self.assertEqual(parsed[0]['normalizationReason'], 'shipping_fee_missing')
        self.assertEqual(evaluate(payload)['gate_eligible'], [])


if __name__ == '__main__':
    unittest.main()
