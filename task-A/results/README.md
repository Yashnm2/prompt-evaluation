# Results status

No live model results yet. OpenAI Platform key setup returned an authentication error and needs the connection restored. Do not interpret evaluator unit tests or the expected fixture answers as model outputs.

Prepared: five system prompts (84, 217, 448, 526 and 1,011 whitespace-delimited words), one shared user template, three supplied test cases and ten additional cases with expected facts frozen before model evaluation.

The planned comparison is three independent calls per prompt/case pair: 5 x 13 x 3 = 195 raw outputs, using a temperature-zero-compatible model. All task instructions go in the system message; the article goes in the user template. Save actual model/settings with each response. Report first-attempt validity separately from correctness, quote review and repeat consistency. Select a prompt from observed results, retaining its twelve required assessment outputs (the three supplied cases and the full-article stress case, each repeated three times).

Offline verification: `python3 -m unittest discover -s task-A/tests -v` passed 10 evaluator regression tests. These cover malformed JSON, extra prose, duplicate keys, invalid amounts/types, missing recipients, invented evidence, wrong amounts and participant/lead confusion. This verifies the grading code on synthetic responses; it does not measure LLM quality.

Semantic evidence review remains necessary: a verbatim substring check alone cannot establish that a quote supports a claim. Exact fact matching also penalizes synonyms unless explicitly accepted; inspect any such mismatch rather than silently changing expected answers after seeing model outputs.
