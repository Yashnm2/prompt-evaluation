# Task A

The first thing I did was build a test suite with ChatGPT: 33 articles covering clean and messy wording, multiple startups, missing names, misleading locations and prompt injection.

I explored six ChatGPT-assisted variants: minimal, concise, procedural, example-based, detailed, and `06-handwritten`, combining prompts 3–5. The repository keeps the selected [06-handwritten](task-A/prompts/06-handwritten.txt): a clear role, exact JSON example, field-specific rules and injection defenses. An initial mini-model trial exposed missing-detail and currency errors, which informed the revision.

Final validation used `gpt-4.1-2025-04-14`, temperature 0, with three independent calls per input:

| Input | Correct format | Expected facts |
|---|---:|---:|
| Supplied example 1 | 3/3 | 3/3 |
| Supplied example 2 | 3/3 | 3/3 |
| Supplied example 3 | 3/3 | 3/3 |
| Original messy article | 3/3 | 3/3 |

On 8 November I revised the expected sector to the article’s specific “warehouse robotics”. Rescoring the unchanged outputs gives **12/12 expected-fact matches**, up from 9/12 under the original expectations. This is a requirement change, not a new model result. Facts were consistent across repetitions. These four development cases do not establish a comparative winner.

For production, I would evaluate [TypeSafe AI’s Jev](https://docs.typesafe.ai/introduction) for funding classification or claim checks, while retaining extraction for names, amounts and quotations. I kept this assessment limited to the supplied text; web search would be a separate enrichment step.

[Raw outputs](task-A/results/selected-06-revised/outputs.md) · [Results and review](task-A/results/selected-06-revised/results.md) · [Test coverage](task-A/tests/README.md)

Offline checks: `python3 -m unittest discover -s task-A/tests -v`. Reproduce the report: `python3 task-A/report_results.py`.

# Task B

**Slide answer: Logistics raised the most in Q3 2026: US$44.55 million.**

## Message to the partner

Logistics raised the most in the supplied Q3 2026 tracker, with US$44.55 million across five rounds. I filtered for July–September, standardised names and sectors, removed duplicate reports, and converted amounts using the supplied exchange rates. This left 18 distinct rounds overall. I treated Kirana Fleet's two reports as the same US$12 million round based on their matching details. That assumption should be confirmed against the original announcements, but Logistics still leads if they are separate rounds. The result covers the supplied tracker only.

## How I did it

I transcribed the supplied image and wrote a [Python script](task-B/analyze.py) to clean the data, filter Q3 rounds, remove duplicate reports, convert funding to USD, and calculate the totals by sector. I checked the results with automated tests and saved the cleaned data for review.

[Input data](task-B/rounds.csv) · [Cleaned data](task-B/cleaned-rounds.csv) · [Full answer and calculations](task-B/submission.md)

# Task C

## 1. Every problem you find, ranked by severity, one line each.

- **High:** `last_contact=None` crashes because the fallback datetime is timezone-naive while `today` is timezone-aware.
- **High:** Sorting ISO timestamps as strings can return the wrong chronological order when timezone offsets differ.
- **Medium:** `.days > 14` truncates elapsed time, excluding contacts older than 14 days until they reach 15 days.
- **Medium:** The tests are not comprehensive enough to catch missing contacts, mixed timezone offsets and cutoff errors.

## 2. Merge, merge with changes, or reject, and why.

**Merge with changes.** I would update the tests to cover the missing cases and make three targeted fixes: handle never-contacted deals explicitly, sort by parsed UTC datetimes, and compare the full elapsed time against 14 days. The [updated code](task-C/fix.py) implements these changes; I would merge once the tests pass.

## 3. The tests you would add, as runnable pytest code.

These core regression tests use the function in [fix.py](task-C/fix.py). Save them as `task-C/test_review.py` and run `python3 -m pytest task-C/test_review.py -v`. The [full test suite](task-C/test_fix.py) also checks input mutation, ties and other edge cases.

```python
from datetime import datetime, timedelta, timezone

import pytest

from fix import deals_needing_followup


TODAY = datetime(2026, 11, 1, tzinfo=timezone.utc)


def make_deal(name, last_contact, stage="Sourcing"):
    return {"name": name, "stage": stage, "last_contact": last_contact}


def test_never_contacted_comes_before_old_contacts():
    deals = [
        make_deal("Old", "2026-09-01T09:00:00+08:00"),
        make_deal("Never", None),
    ]
    assert deals_needing_followup(deals, TODAY) == ["Never", "Old"]


def test_mixed_offsets_sort_by_actual_time():
    deals = [
        make_deal("India", "2026-10-01T08:00:00+05:30"),
        make_deal("Singapore", "2026-10-01T09:00:00+08:00"),
    ]
    assert deals_needing_followup(deals, TODAY) == ["Singapore", "India"]


@pytest.mark.parametrize("age, expected", [
    (timedelta(days=14, microseconds=1), ["Deal"]),
    (timedelta(days=14), []),
    (timedelta(days=14) - timedelta(microseconds=1), []),
    (timedelta(days=1), []),
    (timedelta(days=-1), []),
])
def test_contact_cutoff(age, expected):
    deal = make_deal("Deal", (TODAY - age).isoformat())
    assert deals_needing_followup([deal], TODAY) == expected


@pytest.mark.parametrize("stage", ["Closed - Won", "Closed - Lost"])
@pytest.mark.parametrize("last_contact", [None, "2026-09-01T09:00:00+08:00"])
def test_closed_deals_are_excluded(stage, last_contact):
    assert deals_needing_followup([make_deal("Closed", last_contact, stage)], TODAY) == []


@pytest.mark.parametrize("stage", ["Sourcing", "Diligence"])
def test_open_stale_deals_are_returned(stage):
    deal = make_deal("Open", "2026-09-01T09:00:00+08:00", stage)
    assert deals_needing_followup([deal], TODAY) == ["Open"]
```

## 4. Any behaviour the spec leaves open that you'd ask the teammate about.

- Does a contact exactly 14 days old qualify for follow-up?
- Where should never-contacted deals appear in the ordering?
- Should timestamps without a timezone be rejected or assigned a default timezone?
- How should deals with equal contact times be ordered?

The [current fix](task-C/fix.py) excludes exactly 14 days, places never-contacted deals first, rejects timezone-naive timestamps and preserves input order for ties.
