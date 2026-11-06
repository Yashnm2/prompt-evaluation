# Prompt evaluation

## Status

Repository initialized on 6 November 2026. The assessment has been read; see `task-A/requirements.md` for the extraction contract and submission requirements. Task A is funding-news extraction, rather than general classification. No model evaluations have run, and no accuracy results are claimed. Secure API-key creation currently requires the OpenAI Platform connection to be reauthenticated.

## Layout

- `task-A/`: five system prompts of different lengths, original tests plus ten additional cases, validation code, saved model responses, and a Markdown results report.
- `task-B/`: reserved for Task B.
- `task-C/`: reserved for Task C.

## Prepared artifacts

- Five system prompts in `task-A/prompts/`, ranging from 84 to 1,011 words; lengths are recorded in `manifest.json`.
- Shared `task-A/user-template.txt` with the required `{article}` placeholder.
- `task-A/tests/cases.json`: all three supplied snippets plus exactly ten additional tests, including a full-article stress test.
- `task-A/evaluate.py`: strict JSON validity checks and independent comparison with expected facts. Quote entailment still requires manual review.
- `task-A/invalid-response-policy.md` and `task-A/production-notes.md`: operational guidance and sourced discussion of classifiers and LLM validation.
- `task-A/results/README.md`: honest evaluation status; no live output has been generated.

Offline evaluator checks passed: `python3 -m unittest discover -s task-A/tests -v` (10 tests). These are tests of the evaluator, not prompt performance.

## Evaluation plan

1. Extract the task rules, output contract, and original examples from the brief.
2. Write five prompts with different lengths while preserving the same task and output contract. Report their lengths.
3. Add ten distinct tests with expected answers established before running the prompts. Cover normal inputs, boundaries, ambiguous inputs, and adversarial instructions where relevant.
4. Put all task instructions in the system message and each test input in a separate user message. Set `temperature=0` on a compatible model; record the actual model and request settings. Temperature zero reduces sampling variability but does not guarantee identical outputs across runs.
5. Save raw responses and check validity with code: parse the complete output and enforce the required schema, types, keys, and allowed values. Check correctness separately against the expected answers, including valid but wrong responses.
6. Report validity, correctness across all tests, correctness among valid responses, per-case failures, and limitations in Markdown. Do not treat transport failures as model answers or silently omit them.

Keep this README current as requirements, implementation, and results change. Commit meaningful milestones locally. Do not commit API keys or private credentials.

## Production considerations to verify

See `task-A/production-notes.md` for source-checked discussion of TypeSafe AI Jev and OpenAI moderation. Dedicated classification may help filtering and safety review, but it does not by itself replace the structured extraction required by Task A. Lower cost, higher accuracy, and better uncertainty handling are hypotheses to measure on this task, not established results. Thresholds and abstention need calibration on representative held-out data.

An additional LLM may review semantic correctness and safety after deterministic validation. This adds cost and latency and may share the primary model's blind spots. Its output must also be validated; disagreements and uncertainty should go to review rather than automatically overriding deterministic checks.
