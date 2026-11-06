"""Run the frozen 5 x 13 x 3 comparison; preserve every HTTP response.

No retries or output repair: this measures first-attempt prompt performance.
An interrupted run resumes only where no record exists. Errors are retained.
"""
import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

from evaluate import ROOT, grade, load_cases

ENDPOINT = 'https://api.openai.com/v1/chat/completions'


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def load_key():
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if key:
        return key
    # Read only the project's ignored file. Never print its contents.
    path = ROOT.parent / '.env.local'
    if path.is_file():
        for line in path.read_text().splitlines():
            name, sep, value = line.partition('=')
            if sep and name.strip() == 'OPENAI_API_KEY':
                return value.strip().strip('\"\'')
    return ''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='gpt-4.1-mini-2025-04-14')
    parser.add_argument('--run-id', required=True, help='New result directory name; reuse only to resume')
    parser.add_argument('--plan-only', action='store_true', help='Check inputs without network or credentials')
    args = parser.parse_args()
    if not args.run_id or any(x not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for x in args.run_id):
        parser.error('run-id must contain only letters, digits, hyphens and underscores')
    cases = load_cases()
    prompts = [(p.stem, p.read_text()) for p in sorted((ROOT / 'prompts').glob('*.txt'))]
    template = (ROOT / 'user-template.txt').read_text()
    if template.count('{article}') != 1 or len(prompts) != 5 or len(cases) != 13:
        raise SystemExit('Unexpected prompt, template or case inventory')
    plan = {
        'model': args.model, 'temperature': 0, 'max_completion_tokens': 2500,
        'repetitions': 3, 'planned_requests': len(prompts) * len(cases) * 3,
        'prompt_hashes': {name: digest(text) for name, text in prompts},
        'cases_hash': digest((ROOT / 'tests/cases.json').read_text()),
        'evaluator_hash': digest((ROOT / 'evaluate.py').read_text()),
        'template_hash': digest(template), 'endpoint': ENDPOINT,
        'structured_output_mode': False, 'automatic_retries': 0,
    }
    if args.plan_only:
        print(json.dumps(plan, indent=2))
        return
    key = load_key()
    if not key:
        raise SystemExit('No API credential found. Secure key setup must be completed first.')
    directory = ROOT / 'results' / args.run_id
    directory.mkdir(exist_ok=True)
    manifest = directory / 'manifest.json'
    if manifest.exists():
        if json.loads(manifest.read_text()) != plan:
            raise SystemExit('Inputs/settings changed; use a new run-id rather than mixing results.')
    else:
        save(manifest, plan)
    completed = 0
    for prompt_id, system in prompts:
        for case in cases:
            for repeat in range(1, 4):
                target = directory / f'{prompt_id}__{case["id"]}__{repeat}.json'
                if target.exists():
                    completed += 1
                    continue
                payload = {
                    'model': args.model, 'temperature': 0, 'max_completion_tokens': 2500,
                    'messages': [
                        {'role': 'system', 'content': system},
                        {'role': 'user', 'content': template.replace('{article}', case['article'])},
                    ],
                }
                record = {
                    'prompt_id': prompt_id, 'case_id': case['id'], 'repeat': repeat,
                    'started_at_utc': datetime.now(timezone.utc).isoformat(),
                    'request': payload, 'status': 'pending',
                }
                request = urllib.request.Request(ENDPOINT, json.dumps(payload).encode(), {
                    'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json',
                })
                started = time.monotonic()
                http_code = None
                try:
                    with urllib.request.urlopen(request, timeout=60) as response:
                        body = response.read().decode('utf-8')
                        record['http_status'] = response.status
                        record['raw_http_body'] = body
                        record['request_id'] = response.headers.get('x-request-id')
                    decoded = json.loads(body)
                    record['response'] = decoded
                    choice = decoded['choices'][0]
                    message = choice['message']
                    raw = message.get('content')
                    record['raw_output'] = raw
                    record['finish_reason'] = choice.get('finish_reason')
                    if message.get('refusal'):
                        record['status'] = 'refusal'
                    elif choice.get('finish_reason') != 'stop':
                        record['status'] = 'incomplete'
                    elif not isinstance(raw, str) or not raw.strip():
                        record['status'] = 'empty'
                    else:
                        record['status'] = 'response'
                        record['grade'] = grade(raw, case)
                except urllib.error.HTTPError as exc:
                    http_code = exc.code
                    record['status'] = 'http_error'
                    record['http_status'] = exc.code
                    # Preserve error response, but never request headers/credentials.
                    record['raw_http_body'] = exc.read().decode('utf-8', errors='replace')
                    exc.close()
                except (urllib.error.URLError, TimeoutError, OSError) as exc:
                    record['status'] = 'transport_error'
                    record['error_type'] = type(exc).__name__
                except (ValueError, KeyError, IndexError, TypeError) as exc:
                    record['status'] = 'unexpected_response'
                    record['error_type'] = type(exc).__name__
                record['elapsed_seconds'] = round(time.monotonic() - started, 3)
                save(target, record)
                completed += 1
                print(f'{completed}/195 {prompt_id} {case["id"]} repeat {repeat}: {record["status"]}', flush=True)
                if http_code in (400, 401, 403, 404, 429):
                    raise SystemExit('API rejected request; error preserved. Resolve access/settings before a new run.')
    print('Raw run complete. Generate the report and review evidence before selecting a prompt.')


if __name__ == '__main__':
    main()
