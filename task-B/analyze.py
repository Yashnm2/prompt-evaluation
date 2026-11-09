"""Task B: clean the funding export and find the leading sector in Q3 2026."""

import csv
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


# ---- 1. Constraints and assumptions ----

HERE = Path(__file__).resolve().parent
START = date(2026, 7, 1)
END = date(2026, 9, 30)
FX = {"USD": Decimal("1"), "SGD": Decimal("0.77"), "INR": Decimal("0.012")}
SECTORS = {
    "fintech": "Fintech", "logistics": "Logistics", "healthtech": "Healthtech",
    "agritech": "Agritech", "climate": "Climate",
}
# Manual decisions for this export: same company and same round, reported twice.
ALIASES = {"Kirana Fleet Pte Ltd": "Kirana Fleet"}
DUPLICATE_REPORTS = {
    ("Kirana Fleet", "Series A", Decimal("12000000"), "USD",
     date(2026, 7, 4)): date(2026, 7, 3),
}


# ---- 2. Data input ----

def load_data():
    with (HERE / "rounds.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---- 3. Data cleaning ----

def parse_date(value):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unsupported date: {value!r}")


def clean_data(rows):
    cleaned = []
    # CSV row numbers include the header, so the first data row is 2.
    for n, raw in enumerate(rows, start=2):
        row = {key: value.strip() for key, value in raw.items()}
        amount = Decimal(row["amount"])
        currency = row["currency"].upper()
        if not amount.is_finite() or amount < 0:
            raise ValueError(f"Invalid amount on CSV row {n}")
        if currency not in FX:
            raise ValueError(f"Unsupported currency: {currency}")
        if row["sector"].casefold() not in SECTORS:
            raise ValueError(f"Unknown sector on CSV row {n}: {row['sector']}")

        cleaned.append({
            "input_row": n, "reported_date": row["date"],
            "date": parse_date(row["date"]),
            "company": ALIASES.get(row["company"], row["company"]),
            "sector": SECTORS[row["sector"].casefold()],
            "round": row["round"], "amount": amount,
            "currency": currency, "source": row["source"],
        })
    return cleaned


# ---- 4. Data processing ----

def analyze(rows):
    events = {}
    removed = {"outside_q3": [], "duplicate": []}
    for row in clean_data(rows):
        # 4a. Keep only Q3, including both boundary dates.
        if not START <= row["date"] <= END:
            removed["outside_q3"].append(row["input_row"])
            continue

        # 4b. Count rounds, not reports. Sources do not define separate rounds.
        event_date = DUPLICATE_REPORTS.get(
            (row["company"], row["round"], row["amount"], row["currency"], row["date"]),
            row["date"],
        )
        key = (row["company"], row["sector"], row["round"], row["amount"],
               row["currency"], event_date)
        if key in events:
            kept = events[key]
            kept["input_rows"].append(row["input_row"])
            kept["reported_dates"].append(row["reported_date"])
            kept["sources"].append(row["source"])
            removed["duplicate"].append(row["input_row"])
            continue

        # 4c. Convert each distinct round using the supplied fixed rates.
        usd = (row["amount"] * FX[row["currency"]]).quantize(Decimal("0.01"))
        events[key] = {
            "date": event_date.isoformat(), "company": row["company"],
            "sector": row["sector"], "round": row["round"],
            "amount": row["amount"], "currency": row["currency"], "amount_usd": usd,
            "input_rows": [row["input_row"]],
            "reported_dates": [row["reported_date"]], "sources": [row["source"]],
        }

    # 4d. Sum distinct rounds by sector.
    totals = {}
    counts = {}
    for row in events.values():
        sector = row["sector"]
        totals[sector] = totals.get(sector, Decimal("0")) + row["amount_usd"]
        counts[sector] = counts.get(sector, 0) + 1
    return list(events.values()), removed, totals, counts


# ---- 5. Results and cleaned data ----

def save_cleaned(events):
    output = []
    for row in events:
        row = row.copy()
        for field in ("input_rows", "reported_dates", "sources"):
            row[field] = "; ".join(str(value) for value in row[field])
        output.append(row)
    with (HERE / "cleaned-rounds.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)


def show_results(totals, counts):
    if not totals:
        raise ValueError("No Q3 rounds to analyse")
    ranking = sorted(totals, key=lambda sector: (-totals[sector], sector))
    winners = [sector for sector in ranking if totals[sector] == totals[ranking[0]]]
    if len(winners) != 1:
        raise ValueError(f"No single winning sector: {winners}")
    winner = winners[0]
    print(f"{winner} raised the most in Q3 2026: US${totals[winner]:,.0f}.")
    for sector in ranking:
        print(f"{sector:12} {counts[sector]} rounds  US${totals[sector]:>14,.2f}")


# ---- 6. Run everything ----

def main():
    rows = load_data()
    N = len(rows)
    events, removed, totals, counts = analyze(rows)
    show_results(totals, counts)
    save_cleaned(events)
    print(f"{N} input rows - {len(removed['outside_q3'])} outside Q3 "
          f"- {len(removed['duplicate'])} duplicate reports = {len(events)} rounds.")
    print(f"Total across sectors: US${sum(totals.values()):,.2f}.")


if __name__ == "__main__":
    main()
