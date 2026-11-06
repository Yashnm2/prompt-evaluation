# Handling invalid and uncertain responses

Finalize the exact validation rules against Task A's specified output contract before implementing them.

1. Preserve the raw response and record the model, prompt version, test ID, settings, and failure reason. Redact sensitive input in operational logs.
2. Check request failures, refusals, missing content, and truncation before parsing. Track these separately from formatting and classification errors.
3. Parse the entire response using the required format. Reject extra prose, code fences, trailing content, duplicate JSON keys, missing or extra fields, invalid types, and unknown labels if the contract forbids them. Do not extract a convenient fragment and count it as valid.
4. Validate semantics separately. A response can satisfy the format and still be wrong. In an offline evaluation, compare with independently specified expected answers. In production, use task rules, calibrated classifier signals, and review where needed because ground truth usually is unavailable.
5. Never convert invalid output into a default classification such as safe or negative. Return an explicit failure or review state outside the model's classification contract.
6. For temporary service failures, use bounded retries with backoff. For malformed output, permit at most one controlled regeneration with the original system instructions and a concise validation error. Treat the original input and previous output as untrusted data.
7. Report first-attempt performance separately from recovery performance. Never replace the original failure in the benchmark with a successful retry.
8. After the retry limit, stop automatic processing and route to a human or an explicitly designed fallback. For safety decisions, withhold the automated action until reviewed.
9. Treat ambiguous inputs, conflicting validators, out-of-scope inputs, and low-confidence classifier scores as review cases. An LLM's self-reported confidence is not a calibrated probability.
10. Monitor invalid-response and disagreement rates by prompt version and input category. Reassess thresholds and regression tests when the model, prompts, or data distribution change.
