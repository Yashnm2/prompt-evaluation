"""Generate an honest Markdown report from an actual saved run, no model calls."""
import argparse
import hashlib
import json
from collections import defaultdict

from evaluate import ROOT, grade, load_cases


def ratio(n, d):
    return f'{n}/{d} ({100*n/d:.1f}%)' if d else 'N/A'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id')
    args = parser.parse_args()
    directory = ROOT / 'results' / args.run_id
    if directory.parent != ROOT / 'results':
        raise SystemExit('Invalid run directory')
    manifest = json.loads((directory / 'manifest.json').read_text())
    for filename, key in [('tests/cases.json', 'cases_hash'), ('evaluate.py', 'evaluator_hash')]:
        current = hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
        if current != manifest[key]:
            raise SystemExit(f'{filename} changed since the run; restore the frozen version before reporting.')
    cases = {c['id']: c for c in load_cases()}
    records = [json.loads(p.read_text()) for p in sorted(directory.glob('*__*__*.json'))]
    by_prompt = defaultdict(list)
    for record in records:
        if record['status'] == 'response':
            record['grade'] = grade(record['raw_output'], cases[record['case_id']])
        by_prompt[record['prompt_id']].append(record)
    returned_models = sorted({r.get('response', {}).get('model', 'not supplied') for r in records if r['status'] == 'response'})
    lines = [
        '# Task A prompt comparison', '',
        f"Requested model: `{manifest['model']}`. Temperature: **0**. Task instructions are in the **system message**; each article uses the shared user template in a separate **user message**.", '',
        'Returned model IDs: ' + (', '.join(returned_models) if returned_models else 'None yet') + '.', '',
        'No JSON response mode, schema-constrained decoding, retries or output repairs are used. This isolates prompt behavior. Temperature zero does not guarantee identical outputs.', '',
        f"Saved requests: {len(records)}/{manifest['planned_requests']}. Missing requests are untested, not successes. Refusals, truncations and transport errors are counted separately.", '',
        '| Prompt | Saved / planned | Complete responses | Valid / complete | Correct / saved | Correct / valid | Other outcomes |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for prompt_id in manifest['prompt_hashes']:
        rows = by_prompt[prompt_id]
        responses = [r for r in rows if r['status'] == 'response']
        valid = sum(r['grade']['valid'] for r in responses)
        correct = sum(r['grade']['correct'] for r in responses)
        lines.append(f'| {prompt_id} | {len(rows)}/39 | {len(responses)} | {ratio(valid, len(responses))} | {ratio(correct, len(rows))} | {ratio(correct, valid)} | {len(rows)-len(responses)} |')
    lines += ['', '## Per-case outcomes and repetition consistency', '',
              '| Prompt | Case | Saved / 3 | Valid | Correct | Distinct raw texts | Distinct fact outputs (excluding evidence) |',
              '|---|---|---:|---:|---:|---:|---:|']
    for prompt_id in manifest['prompt_hashes']:
        for case_id in cases:
            rows = [r for r in by_prompt[prompt_id] if r['case_id'] == case_id]
            responses = [r for r in rows if r['status'] == 'response']
            valid_rows = [r for r in responses if r['grade']['valid']]
            facts = set()
            for row in valid_rows:
                obj = json.loads(row['raw_output'])
                for c in obj['companies']:
                    c.pop('evidence')
                facts.add(json.dumps(obj, sort_keys=True))
            lines.append(f"| {prompt_id} | {case_id} | {len(rows)}/3 | {len(valid_rows)} | {sum(r['grade']['correct'] for r in responses)} | {len({r['raw_output'] for r in responses})} | {len(facts)} |")
    lines += ['', '## Failures', '']
    failures = 0
    for record in records:
        label = f"{record['prompt_id']} / {record['case_id']} / repeat {record['repeat']}"
        if record['status'] != 'response':
            lines.append(f"- {label}: {record['status']}.")
            failures += 1
        elif not record['grade']['correct']:
            errors = record['grade']['validity_errors'] + record['grade']['correctness_errors']
            lines.append(f"- {label}: " + '; '.join(errors).replace('\n', ' '))
            failures += 1
    if not failures:
        lines.append('No failures among saved records. Check coverage above before interpreting this statement.')
    lines += ['', '## Limits and outstanding review', '',
              'These are automated fixture scores, not proof of semantic correctness. Manually inspect evidence for claim support, quote brevity and conflicting facts before selecting a prompt. Semantic synonyms may require adjudication, documented separately from the frozen expectations. Results compare complete prompt designs, not length alone: the longer prompts also contain more guidance and examples.', '',
              'The fixture decisions allow unambiguous city-to-country mapping, treat bare $ as USD, normalize Series C and later to Series C+, and exclude historical background rounds. The brief does not settle all of these details. Ten added cases were authored alongside these prompts, so this is a development suite, not an independent hidden benchmark.', '',
              'Selection, the final twelve-output submission, the at-most-150-word failure note, the at-most-80-word AI log, and a genuine chat export/share link remain to be completed after the actual results and manual review. No raw chat export is fabricated here.', '']
    target = directory / 'results.md'
    target.write_text('\n'.join(lines))
    print(target)


if __name__ == '__main__':
    main()
