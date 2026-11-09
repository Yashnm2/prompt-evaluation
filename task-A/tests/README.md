# Tests

`cases.json` contains three supplied articles and thirty additional development cases. Coverage includes clean and messy wording, multiple recipients, unnamed companies, misleading geographic clues, missing fields, currencies, historical rounds, valuations, corrections and prompt injection.

Only four articles have complete final model runs: `given-01`, `given-02`, `given-03` and `extra-10`, each repeated three times. The other cases support development; no live accuracy score is claimed for them.

On 8 November 2026 the expected StackFern sector in `extra-10` changed to `warehouse robotics`. Other robotics cases retain their article-supported sector. Original expectations are preserved in `../results/selected-06-revised/original-cases.json`.

Run offline regression checks from the project root:

```sh
python3 -m unittest discover -s task-A/tests -v
python3 task-A/report_results.py
```

The report command verifies the saved answers and expectation hashes, then rescores without calling an API. Exact expected-fact matching and verbatim quotation checks do not replace semantic evidence review.
