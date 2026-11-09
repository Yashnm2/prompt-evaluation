from copy import deepcopy
from datetime import datetime, timedelta, timezone
from itertools import permutations

import pytest
import fix

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


def test_calls_are_independent_and_input_is_unchanged():
    deals = [make_deal("First", "2026-09-01T09:00:00+08:00")]
    original = deepcopy(deals)
    assert deals_needing_followup(deals, TODAY) == ["First"]
    assert deals_needing_followup([], TODAY) == []
    assert deals_needing_followup([make_deal("Second", None)], TODAY) == ["Second"]
    assert deals == original


def test_equivalent_instants_retain_input_order():
    deals = [
        make_deal("Singapore", "2026-10-01T09:00:00+08:00"),
        make_deal("India", "2026-10-01T06:30:00+05:30"),
    ]
    assert deals_needing_followup(deals, TODAY) == ["Singapore", "India"]


def test_today_can_use_a_different_offset():
    deal = make_deal("Deal", (TODAY - timedelta(days=14, seconds=1)).isoformat())
    local_today = TODAY.astimezone(timezone(timedelta(hours=5, minutes=30)))
    assert deals_needing_followup([deal], local_today) == ["Deal"]


def test_naive_today_is_rejected_clearly():
    with pytest.raises(ValueError, match="today must include a timezone"):
        deals_needing_followup([], TODAY.replace(tzinfo=None))


def test_naive_contact_is_rejected_clearly():
    with pytest.raises(ValueError, match="last_contact must include a timezone"):
        deals_needing_followup([make_deal("Deal", "2026-09-01T09:00:00")], TODAY)


def test_mixed_pipeline_returns_only_names_in_stale_order_without_mutation():
    deals = [
        make_deal("Recent", "2026-10-31T08:00:00+08:00"),
        make_deal("Newer stale", "2026-10-01T08:00:00+05:30", "Diligence"),
        make_deal("Won", None, "Closed - Won"),
        make_deal("Never contacted", None),
        make_deal("Older stale", "2026-10-01T09:00:00+08:00"),
        make_deal("Lost", "2026-08-01T00:00:00+08:00", "Closed - Lost"),
        make_deal("Exactly 14 days", "2026-10-18T08:00:00+08:00"),
        make_deal("Future contact", "2026-11-02T00:00:00+08:00"),
    ]
    original = deepcopy(deals)

    result = deals_needing_followup(deals, TODAY)

    assert isinstance(result, list)
    assert all(isinstance(name, str) for name in result)
    assert result == ["Never contacted", "Older stale", "Newer stale"]
    assert deals == original


def test_stale_order_is_correct_for_every_input_permutation():
    deals = [
        make_deal("Oldest", "2026-10-01T09:00:00+08:00"),
        make_deal("Middle", "2026-10-01T08:00:00+05:30"),
        make_deal("Newest", "2026-10-02T00:00:00+08:00"),
    ]
    for ordering in permutations(deals):
        assert deals_needing_followup(list(ordering), TODAY) == [
            "Oldest", "Middle", "Newest"
        ]


@pytest.mark.parametrize("last_contact, expected", [
    ("2026-10-18T07:59:59+08:00", ["Deal"]),
    ("2026-10-18T08:00:00+08:00", []),
    ("2026-10-18T08:00:01+08:00", []),
    ("2026-10-18T05:29:59+05:30", ["Deal"]),
    ("2026-10-18T05:30:00+05:30", []),
    ("2026-10-18T05:30:01+05:30", []),
])
def test_cutoff_uses_actual_instant_across_offsets(last_contact, expected):
    assert deals_needing_followup([make_deal("Deal", last_contact)], TODAY) == expected


def test_default_today_uses_a_fixed_utc_clock(monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            assert tz == timezone.utc
            return TODAY

    monkeypatch.setattr(fix, "datetime", FixedDatetime)
    deals = [
        make_deal("Stale", "2026-10-18T07:59:59+08:00"),
        make_deal("Boundary", "2026-10-18T08:00:00+08:00"),
        make_deal("Never", None),
    ]
    assert deals_needing_followup(deals) == ["Never", "Stale"]
    assert deals_needing_followup(deals, today=None) == ["Never", "Stale"]


def test_duplicate_names_are_preserved_as_separate_deals():
    deals = [
        make_deal("Same name", "2026-09-01T00:00:00+08:00"),
        make_deal("Same name", "2026-10-01T00:00:00+08:00"),
    ]
    assert deals_needing_followup(deals, TODAY) == ["Same name", "Same name"]
