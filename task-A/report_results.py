"""Regrade the twelve saved API answers offline; never modify raw records."""
import hashlib
import json

from evaluate import ROOT, grade, load_cases

RESULTS = ROOT / 'results' / 'selected-06-revised'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((RESULTS / 'manifest.json').read_text())
    change = json.loads((RESULTS / 'expectation-change.json').read_text())
    if sha(ROOT / 'tests/cases.json') != change['current_cases_sha256']:
        raise ValueError('Current test expectations differ from the documented revision')
    original_hash = sha(RESULTS / 'original-cases.json')
    if original_hash != manifest['cases_hash'] or original_hash != change['original_cases_sha256']:
        raise ValueError('Original test expectations changed')
    if sha(ROOT / 'prompts/06-handwritten.txt') != manifest['prompt_hashes']['06-handwritten']:
        raise ValueError('The selected prompt differs from the tested prompt')
    records = sorted(RESULTS.glob('*__*__*.json'))
    if {p.name for p in records} != set(change['raw_record_sha256']):
        raise ValueError('Raw response inventory changed')
    cases = {c['id']: c for c in load_cases()}
    expected = {(c, n) for c in manifest['case_ids'] for n in range(1, 4)}
    seen = set()
    scores = []
    for path in records:
        if sha(path) != change['raw_record_sha256'][path.name]:
            raise ValueError(f'Raw record changed: {path.name}')
        record = json.loads(path.read_text())
        identity = (record['case_id'], record['repeat'])
        if identity in seen or identity not in expected or record['status'] != 'response':
            raise ValueError(f'Unexpected or incomplete response: {path.name}')
        seen.add(identity)
        scores.append((record['case_id'], grade(record['raw_output'], cases[record['case_id']])))
    if seen != expected:
        raise ValueError('The four-case, three-repeat submission is incomplete')
    lines = [
        '# Selected prompt results', '',
        f"Model: `{manifest['model']}`; temperature 0; four inputs, three independent calls each.", '',
        'These are the original API answers rescored offline. No new model calls, answer repairs or answer retries were made.', '',
        '| Input | Correct format | Expected facts |',
        '|---|---:|---:|',
    ]
    for case_id in manifest['case_ids']:
        rows = [score for cid, score in scores if cid == case_id]
        lines.append(f"| {case_id} | {sum(s['valid'] for s in rows)}/3 | {sum(s['correct'] for s in rows)}/3 |")
    valid = sum(s['valid'] for _, s in scores)
    correct = sum(s['correct'] for _, s in scores)
    lines += [
        f'| **Total** | **{valid}/12** | **{correct}/12** |', '',
        'Requirement revision: on 8 November 2026, the expected sector for StackFern changed from `robotics` to the article’s explicit `warehouse robotics`, at the user’s request. The original score was 9/12; the revised score is 12/12. This is a post-run change to expectations, not an improvement from rerunning the model.', '',
        'The [original report](original-report.md), [original expectations](original-cases.json), unchanged raw JSON records and [change record with hashes](expectation-change.json) preserve that distinction.', '',
        '[Exact assistant outputs](outputs.md) · [Source review and limitations](review-notes.md)', '',
    ]
    (RESULTS / 'results.md').write_text('\n'.join(lines))
    print(f'Correct format: {valid}/12; expected facts under revised requirements: {correct}/12')


if __name__ == '__main__':
    main()
