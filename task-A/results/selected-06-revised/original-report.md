# Task A prompt comparison

Requested model: `gpt-4.1-2025-04-14`. Temperature: **0**. Task instructions are in the **system message**; each article uses the shared user template in a separate **user message**.

Returned model IDs: gpt-4.1-2025-04-14.

No JSON response mode, schema-constrained decoding, retries or output repairs are used. This isolates prompt behavior. Temperature zero does not guarantee identical outputs.

Saved requests: 12/12. Missing requests are untested, not successes. Refusals, truncations and transport errors are counted separately.

Archived failed attempts from explicit recovery: 1. Model answers are never retried or replaced.

| Prompt | Saved / planned | Complete responses | Valid / complete | Correct / saved | Correct / valid | Other outcomes |
|---|---:|---:|---:|---:|---:|---:|
| 06-handwritten | 12/12 | 12 | 12/12 (100.0%) | 9/12 (75.0%) | 9/12 (75.0%) | 0 |

## Per-case outcomes and repetition consistency

| Prompt | Case | Saved / 3 | Valid | Correct | Distinct raw texts | Distinct fact outputs (excluding evidence) |
|---|---|---:|---:|---:|---:|---:|
| 06-handwritten | given-01 | 3/3 | 3 | 3 | 1 | 1 |
| 06-handwritten | given-02 | 3/3 | 3 | 3 | 2 | 1 |
| 06-handwritten | given-03 | 3/3 | 3 | 3 | 1 | 1 |
| 06-handwritten | extra-10 | 3/3 | 3 | 0 | 2 | 1 |

## Failures

- 06-handwritten / extra-10 / repeat 1: StackFern.sector: expected 'robotics', got 'warehouse robotics'
- 06-handwritten / extra-10 / repeat 2: StackFern.sector: expected 'robotics', got 'warehouse robotics'
- 06-handwritten / extra-10 / repeat 3: StackFern.sector: expected 'robotics', got 'warehouse robotics'

## Limits and outstanding review

These are automated fixture scores, not proof of semantic correctness. Manually inspect evidence for claim support, quote brevity and conflicting facts before selecting a prompt. Semantic synonyms may require adjudication, documented separately from the frozen expectations. Results compare complete prompt designs, not length alone: the longer prompts also contain more guidance and examples.

The fixture decisions allow city-to-country mapping only for explicitly attributed recipient locations; landmarks, datelines, venues, investor addresses and customer locations do not establish headquarters. Unnamed recipients are omitted under the required company-name contract. Bare $ means USD; Series C and later map to Series C+; historical background rounds are excluded. The brief does not settle all of these details. The added cases were authored alongside these prompts, so this is a development suite, not an independent hidden benchmark.

Metrics alone do not establish a winning prompt or complete the assessment submission. Review evidence and package the required twelve outputs, failure note, AI disclosure and genuine chat export/share link separately; consult any accompanying review notes for completed manual checks. No raw chat export is fabricated here.

See [source review and methodology](review-notes.md) for documented adjudication and limitations.

[Exact assistant outputs](outputs.md).
