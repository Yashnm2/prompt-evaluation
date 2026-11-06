"""Exercise persistence/reporting using synthetic HTTP responses, never live API."""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluate
import report_results
import run_evaluation


class FakeResponse:
    status = 200
    headers = {'x-request-id': 'synthetic-request'}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({'model': 'synthetic-model', 'choices': [
            {'finish_reason': 'stop', 'message': {'content': '{"companies":[]}'}}
        ]}).encode()


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'task-A'
        self.root.mkdir()
        for folder in ('prompts', 'tests'):
            shutil.copytree(evaluate.ROOT / folder, self.root / folder)
        shutil.copy(evaluate.ROOT / 'user-template.txt', self.root)
        shutil.copy(evaluate.ROOT / 'evaluate.py', self.root)
        (self.root / 'results').mkdir()
        for module in (evaluate, run_evaluation, report_results):
            patcher = patch.object(module, 'ROOT', self.root)
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_mock(self, transport):
        with patch.object(sys, 'argv', ['run_evaluation.py', '--run-id', 'synthetic']), \
             patch.object(run_evaluation, 'load_key', return_value='synthetic-not-a-real-key'), \
             patch.object(run_evaluation.urllib.request, 'urlopen', side_effect=transport), \
             contextlib.redirect_stdout(io.StringIO()):
            run_evaluation.main()

    def test_full_grid_persistence_resume_and_report(self):
        calls = []

        def transport(request, timeout):
            payload = json.loads(request.data)
            self.assertEqual(payload['temperature'], 0)
            self.assertEqual([m['role'] for m in payload['messages']], ['system', 'user'])
            self.assertNotIn('response_format', payload)
            calls.append(payload)
            return FakeResponse()

        self.run_mock(transport)
        self.assertEqual(len(calls), 195)
        self.run_mock(transport)
        self.assertEqual(len(calls), 195, 'Resuming must not repeat saved requests')
        files = list((self.root / 'results/synthetic').glob('*__*__*.json'))
        self.assertEqual(len(files), 195)
        for p in files:
            text = p.read_text()
            self.assertNotIn('synthetic-not-a-real-key', text)
            self.assertEqual(json.loads(text)['status'], 'response')
        with patch.object(sys, 'argv', ['report_results.py', 'synthetic']), contextlib.redirect_stdout(io.StringIO()):
            report_results.main()
        report = (self.root / 'results/synthetic/results.md').read_text()
        self.assertIn('195/195', report)
        self.assertIn('Expected 1 recipients, got 0', report)
        self.assertIn('Temperature: **0**', report)

    def test_auth_error_is_saved_and_stops_without_retry(self):
        calls = []

        def transport(request, timeout):
            calls.append(request)
            raise urllib.error.HTTPError(request.full_url, 401, 'Unauthorized', {}, io.BytesIO(b'{"error":"synthetic"}'))

        with self.assertRaises(SystemExit):
            self.run_mock(transport)
        self.assertEqual(len(calls), 1)
        records = list((self.root / 'results/synthetic').glob('*__*__*.json'))
        self.assertEqual(len(records), 1)
        self.assertEqual(json.loads(records[0].read_text())['status'], 'http_error')


if __name__ == '__main__':
    unittest.main()
