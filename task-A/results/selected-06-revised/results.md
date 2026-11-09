# Selected prompt results

Model: `gpt-4.1-2025-04-14`; temperature 0; four inputs, three independent calls each.

These are the original API answers rescored offline. No new model calls, answer repairs or answer retries were made.

| Input | Correct format | Expected facts |
|---|---:|---:|
| given-01 | 3/3 | 3/3 |
| given-02 | 3/3 | 3/3 |
| given-03 | 3/3 | 3/3 |
| extra-10 | 3/3 | 3/3 |
| **Total** | **12/12** | **12/12** |

Requirement revision: on 8 November 2026, the expected sector for StackFern changed from `robotics` to the article’s explicit `warehouse robotics`, at the user’s request. The original score was 9/12; the revised score is 12/12. This is a post-run change to expectations, not an improvement from rerunning the model.

The [original report](original-report.md), [original expectations](original-cases.json), unchanged raw JSON records and [change record with hashes](expectation-change.json) preserve that distinction.

[Exact assistant outputs](outputs.md) · [Source review and limitations](review-notes.md)
