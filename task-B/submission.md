# Task B

## Slide answer

**Logistics: US$44.55 million raised in Q3 2026 (supplied tracker).**

## Note to the partner

I kept rounds dated 1 July–30 September 2026, parsed Dockside's date as 18 September, and standardised FinTech/Fintech. I converted SGD and INR at the supplied rates of US$0.77 and US$0.012 per unit. I counted PayLoom's two reports once and treated Kirana Fleet/Kirana Fleet Pte Ltd as the same US$12 million Series A, based on the matching names, stage, amount and adjacent dates. This leaves 18 distinct rounds, including five in Logistics. The Kirana match should be confirmed against the announcements; it affects the total but not the winning sector. This figure covers the supplied tracker, using its dates, rather than all market funding.

## Code used

[Python script](analyze.py), using the standard library only. From the project root:

```sh
python3 task-B/analyze.py
```

[Original data](rounds.csv) · [Cleaned rounds with source references](cleaned-rounds.csv)

The input was transcribed from the supplied Section B image because the separately mentioned CSV attachment was not available in this workspace. ChatGPT/Codex assisted with transcription, code and wording.

## Supporting calculations

| Sector | Distinct rounds | USD total |
|---|---:|---:|
| Logistics | 5 | 44,550,000 |
| Healthtech | 3 | 37,390,000 |
| Fintech | 4 | 30,170,000 |
| Climate | 3 | 13,680,000 |
| Agritech | 3 | 5,280,000 |

Logistics: Kirana Fleet **12m** + Portline **19.25m** + RouteNine **0.8m** + HaulHub **3.5m** + Dockside **9m** = **US$44.55m**.

Reconciliation: **22 input rows − 2 outside Q3 − 2 duplicate reports = 18 distinct Q3 rounds**, totalling **US$131.07m** across sectors.

If Kirana's reports represented separate rounds, Logistics would total **US$56.55m** and still rank first. The base case treats them as one round. No external source verification was performed.
