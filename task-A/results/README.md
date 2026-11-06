# Results status

No live model results yet. OpenAI Platform key setup returned an authentication error and needs the connection restored. Do not interpret evaluator unit tests or the expected fixture answers as model outputs.

Prepared: five system prompts (84, 217, 448, 526 and 1,011 whitespace-delimited words), one shared user template, three supplied test cases and ten additional cases with expected facts frozen before model evaluation.

The planned comparison is three independent calls per prompt/case pair: 5 x 13 x 3 = 195 raw outputs, using a temperature-zero-compatible model. All task instructions go in the system message; the article goes in the user template. Save actual model/settings with each response. Report first-attempt validity separately from correctness, quote review and repeat consistency. Select a prompt from observed results, retaining its twelve required assessment outputs (the three supplied cases and the full-article stress case, each repeated three times).

Offline verification: `python3 -m unittest discover -s task-A/tests -v` passed 12 regression tests. These cover malformed JSON, extra prose, duplicate keys, invalid amounts/types, missing recipients, invented evidence, wrong amounts, participant/lead confusion, complete-grid persistence/resume/reporting, and stopping on authentication errors. This verifies code using synthetic responses in temporary directories; it does not measure LLM quality.

`run_evaluation.py` is prepared for the full 195-call comparison and `report_results.py` generates Markdown from an actual saved run. A plan-only check succeeded with temperature 0 and separate system/user messages. No live requests have been made. The planned model is `gpt-4.1-mini-2025-04-14`; actual returned model IDs will be recorded once testing runs. Model reference: [OpenAI GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini). Request reference: [Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create).

Semantic evidence review remains necessary: a verbatim substring check alone cannot establish that a quote supports a claim. Exact fact matching also penalizes synonyms unless explicitly accepted; inspect any such mismatch rather than silently changing expected answers after seeing model outputs.
