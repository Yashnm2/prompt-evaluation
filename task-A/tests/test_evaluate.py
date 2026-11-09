"""Regression checks for meaningful grading failures, not model evaluations."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluate import grade, load_cases, validate


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.case = load_cases()[0]
        self.company = dict(self.case['expected_companies'][0], evidence=self.case['article'])

    def raw(self, **changes):
        return json.dumps({'companies': [dict(self.company, **changes)]})

    def test_accepts_correct_response(self):
        result = grade(self.raw(), self.case)
        self.assertTrue(result['valid'])
        self.assertTrue(result['correct'])

    def test_rejects_extra_text_and_fences(self):
        for raw in ('```json\n' + self.raw() + '\n```', self.raw() + ' done'):
            self.assertFalse(grade(raw, self.case)['valid'])

    def test_rejects_duplicate_keys(self):
        self.assertTrue(validate('{"companies":[],"companies":[]}')[1])

    def test_rejects_bool_amount_and_nonfinite(self):
        for amount in (True, float('nan'), float('inf'), -1):
            self.assertFalse(grade(self.raw(amount_usd=amount), self.case)['valid'])

    def test_rejects_unknown_fields_and_wrong_types(self):
        for changes in ({'confidence': 1}, {'round': 'Series D'}, {'lead_investors': None}, {'sector': 5}):
            self.assertFalse(grade(self.raw(**changes), self.case)['valid'])

    def test_valid_but_wrong_amount(self):
        result = grade(self.raw(amount_usd=999999999), self.case)
        self.assertTrue(result['valid'])
        self.assertFalse(result['correct'])

    def test_valid_but_participant_mislabelled_lead(self):
        result = grade(self.raw(lead_investors=['Northbridge Capital', 'Lumen Ventures']), self.case)
        self.assertTrue(result['valid'])
        self.assertFalse(result['correct'])

    def test_rejects_fabricated_evidence_as_incorrect_not_invalid(self):
        result = grade(self.raw(evidence='An invented quotation'), self.case)
        self.assertTrue(result['valid'])
        self.assertFalse(result['correct'])

    def test_missing_and_duplicate_recipients(self):
        for companies in ([], [self.company, self.company]):
            self.assertFalse(grade(json.dumps({'companies': companies}), self.case)['correct'])

    def test_all_fixture_facts_can_pass(self):
        for case in load_cases():
            companies = [dict(c, evidence=case['article']) for c in case['expected_companies']]
            self.assertTrue(grade(json.dumps({'companies': companies}), case)['correct'], case['id'])

    def test_rejects_headquarters_inferred_from_landmark(self):
        case = next(c for c in load_cases() if c['category'] == 'landmark-clue')
        company = dict(case['expected_companies'][0], evidence=case['article'], hq_country='Singapore')
        result = grade(json.dumps({'companies': [company]}), case)
        self.assertTrue(result['valid'])
        self.assertFalse(result['correct'])
        self.assertTrue(any('hq_country' in e for e in result['correctness_errors']))

    def test_rejects_invented_name_for_anonymous_recipient(self):
        case = next(c for c in load_cases() if c['category'] == 'unnamed-only')
        company = dict(self.company, name='Unnamed startup', evidence=case['article'])
        result = grade(json.dumps({'companies': [company]}), case)
        self.assertTrue(result['valid'])
        self.assertFalse(result['correct'])

    def test_rejects_facts_swapped_between_recipients(self):
        case = next(c for c in load_cases() if c['category'] == 'clean-multiple')
        companies = [dict(c, evidence=case['article']) for c in case['expected_companies']]
        companies[0]['amount_usd'], companies[1]['amount_usd'] = companies[1]['amount_usd'], companies[0]['amount_usd']
        result = grade(json.dumps({'companies': companies}), case)
        self.assertTrue(result['valid'])
        self.assertFalse(result['correct'])

    def test_specific_warehouse_sector_is_required_only_when_stated(self):
        case = next(c for c in load_cases() if c['id'] == 'extra-10')
        companies = [dict(c, evidence=case['article']) for c in case['expected_companies']]
        self.assertTrue(grade(json.dumps({'companies': companies}), case)['correct'])
        companies[0]['sector'] = 'robotics'
        result = grade(json.dumps({'companies': companies}), case)
        self.assertFalse(result['correct'])
        self.assertTrue(any('sector' in e for e in result['correctness_errors']))

    def test_large_integer_amount_does_not_crash_validator(self):
        self.assertTrue(grade(self.raw(amount_usd=10**400), self.case)['valid'])

    def test_all_twelve_saved_answers_pass_revised_expectations(self):
        cases = {c['id']: c for c in load_cases()}
        paths = list((Path(__file__).resolve().parents[1] / 'results/selected-06-revised').glob('*__*__*.json'))
        self.assertEqual(len(paths), 12)
        for path in paths:
            record = json.loads(path.read_text())
            self.assertTrue(grade(record['raw_output'], cases[record['case_id']])['correct'], path.name)


if __name__ == '__main__':
    unittest.main()
