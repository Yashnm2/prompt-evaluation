"""Offline JSON contract and fixture correctness checks. No model calls."""
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = {"name", "hq_country", "sector", "round", "amount_usd", "lead_investors", "evidence"}
ROUNDS = {"Pre-seed", "Seed", "Series A", "Series B", "Series C+", "Unknown"}


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate key: {key}")
        obj[key] = value
    return obj


def reject_constant(value):
    raise ValueError(f"Non-JSON numeric constant: {value}")


def validate(raw):
    """Return parsed response plus contract errors; never repair raw output."""
    if not isinstance(raw, str):
        return None, ["Response is not text"]
    try:
        data = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (ValueError, TypeError, RecursionError) as exc:
        return None, [f"Invalid JSON: {exc}"]
    if not isinstance(data, dict) or set(data) != {"companies"}:
        return data, ["Root must have exactly the companies key"]
    if not isinstance(data["companies"], list):
        return data, ["companies must be an array"]
    errors = []
    for i, company in enumerate(data["companies"]):
        prefix = f"companies[{i}]"
        if not isinstance(company, dict) or set(company) != FIELDS:
            errors.append(f"{prefix}: exact seven fields required")
            continue
        for key in ("name", "evidence"):
            if not isinstance(company[key], str) or not company[key].strip():
                errors.append(f"{prefix}.{key}: nonempty string required")
        for key in ("hq_country", "sector"):
            if company[key] is not None and (not isinstance(company[key], str) or not company[key].strip()):
                errors.append(f"{prefix}.{key}: nonempty string or null required")
        if not isinstance(company["round"], str) or company["round"] not in ROUNDS:
            errors.append(f"{prefix}.round: unsupported label")
        amount = company["amount_usd"]
        if amount is not None and (type(amount) not in (int, float) or not math.isfinite(amount) or amount < 0):
            errors.append(f"{prefix}.amount_usd: finite nonnegative number or null required")
        leads = company["lead_investors"]
        if not isinstance(leads, list) or any(not isinstance(x, str) or not x.strip() for x in leads):
            errors.append(f"{prefix}.lead_investors: array of nonempty strings required")
    return data, errors


def normalize(value):
    return re.sub(r"\s+", " ", value.strip()).casefold()


def check_correctness(data, case):
    """Compare fixture facts independently of format; evidence gets bounded checks.

    Evidence substring/anchor checks do not prove semantic entailment. Review
    quotes manually in the final report; no LLM-judge claim is made here.
    """
    actual = data["companies"]
    expected = case["expected_companies"]
    errors = []
    if len(actual) != len(expected):
        errors.append(f"Expected {len(expected)} recipients, got {len(actual)}")
    actual_names = [normalize(c["name"]) for c in actual]
    expected_names = [normalize(c["name"]) for c in expected]
    if Counter(actual_names) != Counter(expected_names):
        errors.append("Recipient names differ (missing, invented or duplicate recipient)")
    # Order is not a requirement of the assessment, so compare by identity.
    for gold in expected:
        matches = [c for c in actual if normalize(c["name"]) == normalize(gold["name"])]
        if len(matches) != 1:
            continue
        got = matches[0]
        for field, target in gold.items():
            value = got[field]
            if field == "lead_investors":
                equal = Counter(map(normalize, value)) == Counter(map(normalize, target))
            elif isinstance(target, str) and isinstance(value, str):
                equal = normalize(value) == normalize(target)
            else:
                equal = value == target
            if not equal:
                errors.append(f"{gold['name']}.{field}: expected {target!r}, got {value!r}")
        quote = got["evidence"]
        if quote not in case["article"]:
            errors.append(f"{gold['name']}.evidence: not an exact contiguous source excerpt")
        for alternatives in gold.get("evidence_anchors", []):
            if not any(normalize(a) in normalize(quote) for a in alternatives):
                errors.append(f"{gold['name']}.evidence: missing supporting anchor {alternatives!r}")
    return errors


def grade(raw, case):
    data, validity_errors = validate(raw)
    correctness_errors = check_correctness(data, case) if not validity_errors else []
    return {
        "valid": not validity_errors,
        "correct": not validity_errors and not correctness_errors,
        "validity_errors": validity_errors,
        "correctness_errors": correctness_errors,
        "evidence_review": "Manual semantic review required" if not validity_errors else "Not graded",
    }


def load_cases():
    return json.loads((ROOT / "tests/cases.json").read_text())
