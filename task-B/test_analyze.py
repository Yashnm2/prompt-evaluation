import csv
import unittest
from decimal import Decimal

from analyze import HERE, analyze


def record(**changes):
    row = dict(date="2026-07-01", company="Example", sector="Fintech",
               round="Seed", amount="100", currency="USD", source="TechWire")
    return {**row, **changes}


class TaskBTests(unittest.TestCase):
    def test_supplied_export_totals_and_reconciliation(self):
        with (HERE / "rounds.csv").open(newline="", encoding="utf-8") as handle:
            events, removed, totals, counts = analyze(csv.DictReader(handle))
        self.assertEqual(totals, {
            "Logistics": Decimal("44550000"), "Healthtech": Decimal("37390000"),
            "Fintech": Decimal("30170000"), "Climate": Decimal("13680000"),
            "Agritech": Decimal("5280000"),
        })
        self.assertEqual(counts["Logistics"], 5)
        self.assertEqual(len(events), 18)
        self.assertEqual(removed, {"duplicate": [4, 7], "outside_q3": [2, 23]})
        self.assertEqual(len(events) + sum(map(len, removed.values())), 22)

    def test_dates_and_quarter_boundaries(self):
        rows = [record(date=value) for value in (
            "2026-06-30", "2026-07-01", "18/09/2026", "2026-09-30", "2026-10-01"
        )]
        events, removed, totals, _ = analyze(rows)
        self.assertEqual([event["date"] for event in events],
                         ["2026-07-01", "2026-09-18", "2026-09-30"])
        self.assertEqual(totals["Fintech"], Decimal("300"))
        self.assertEqual(len(removed["outside_q3"]), 2)

    def test_repeat_reports_merge_but_distinct_rounds_remain(self):
        events, _, totals, _ = analyze([
            record(sector="FinTech"), record(source="Press release"),
            record(round="Series A"), record(date="2026-09-01"),
        ])
        self.assertEqual(len(events), 3)
        self.assertEqual(totals["Fintech"], Decimal("300"))
        self.assertEqual(events[0]["sources"], ["TechWire", "Press release"])

    def test_fixed_currency_rates(self):
        _, _, totals, _ = analyze([record(currency="SGD"), record(currency="INR")])
        self.assertEqual(totals["Fintech"], Decimal("78.20"))

    def test_invalid_values_fail_instead_of_being_dropped(self):
        for changes in (dict(currency="EUR"), dict(date="2026-02-30"),
                        dict(amount="-1"), dict(amount="NaN"), dict(sector="Other")):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                analyze([record(**changes)])

    def test_partner_note_meets_word_limit(self):
        submission = (HERE / "submission.md").read_text(encoding="utf-8")
        note = submission.split("## Note to the partner\n", 1)[1].split("\n## ", 1)[0]
        self.assertGreater(len(note.split()), 0)
        self.assertLessEqual(len(note.split()), 150)

    def test_kirana_merge_preserves_both_reports_regardless_of_order(self):
        rows = [
            record(company="Kirana Fleet Pte Ltd", date="2026-07-04", sector="Logistics",
                   round="Series A", amount="12000000", source="AsiaDeals"),
            record(company="Kirana Fleet", date="2026-07-03", sector="Logistics",
                   round="Series A", amount="12000000"),
        ]
        events, _, totals, _ = analyze(rows)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["date"], "2026-07-03")
        self.assertEqual(events[0]["reported_dates"], ["2026-07-04", "2026-07-03"])
        self.assertEqual(events[0]["input_rows"], [2, 3])
        self.assertEqual(events[0]["sources"], ["AsiaDeals", "TechWire"])
        self.assertEqual(totals["Logistics"], Decimal("12000000"))


if __name__ == "__main__":
    unittest.main()
