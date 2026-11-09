# Source review and limitations

ChatGPT reviewed all six distinct output texts against the source articles, including their quotations. This is AI-assisted review, not independent human validation.

- Example 1: correct recipient, country, sector, stage, USD amount and lead; the participant is excluded.
- Example 2: undisclosed funding is retained with Unknown stage, null amount and no invented lead.
- Example 3: recipients remain separate, INR is not converted, missing sectors/stages stay missing and the injection is ignored.
- Stress article: both real recipients are retained; valuation, cumulative funding, acquisitions, historical rounds, future plans and the injected FakeCo are excluded. Warehouse robotics is explicitly supported.

The original exact-fact score was 9/12. The user's sector requirement revision produces 12/12 on the same saved answers. Both scores remain traceable through the original report, original cases, raw grades and change record. The tested prompt itself is unchanged.

The earlier trial used a smaller model and an earlier prompt. Both changed before final validation, so improvement cannot be attributed to the prompt alone. That trial and abandoned infrastructure runs are retained in the external pre-cleanup backup. The current repository keeps the final submission. The broader six-prompt comparison was incomplete.

## Failure/consistency note (under 150 words)

The selected prompt on `gpt-4.1-2025-04-14`, temperature 0, produced twelve valid JSON responses. Originally nine matched the expected facts exactly; three used the article-supported sector `warehouse robotics` rather than `robotics`. On 8 November 2026 the user revised that expectation, making the same twelve answers pass. This is post-run rescoring, not a new model result. Facts were consistent across repetitions; evidence excerpts varied on two inputs. Bare $ is treated as USD; named, unambiguous recipient cities may map to countries; unnamed recipients are omitted. Four development inputs do not establish general reliability or a comparative winner.

## AI disclosure (under 80 words)

ChatGPT helped generate thirty additional test articles, develop six prompt variants, implement validation, and review outputs against source articles. The selected prompt was refined after a development trial. The final four inputs are development checks, not a held-out benchmark. Raw final responses and original grades remain unchanged. A genuine chat export/share link remains a separate submission item.
