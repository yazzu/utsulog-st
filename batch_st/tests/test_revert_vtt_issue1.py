import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = Path(__file__).resolve().parent
if SCRIPT_DIR.name == 'tests':
    SCRIPT_DIR = SCRIPT_DIR.parent


class RevertVttTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vtt = self.root / 'vtt'
        self.fixed = self.root / 'fixed'
        self.output = self.fixed
        for directory in (self.vtt, self.fixed):
            directory.mkdir()
        (self.vtt / 'video.vtt').write_text(
            'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nOriginal\n\n'
            '00:00:01.000 --> 00:00:02.000\nSecond\n', encoding='utf-8')
        (self.fixed / 'video_strip.txt').write_text('0001-Original\n0002-Second\n', encoding='utf-8')
        (self.fixed / 'video_fixed.txt').write_text('0001-Corrected\n', encoding='utf-8')

    def run_batch(self, threshold='100'):
        return subprocess.run(
            [sys.executable, str(SCRIPT_DIR / 'batch_revert_vtt.py'),
             str(self.fixed), str(self.vtt)],
            env={**os.environ, 'RESTORED_COUNT_THRESHOLD': threshold},
            capture_output=True, text=True)

    def report(self):
        return json.loads((self.output / 'revert_vtt_failures.json').read_text())

    def test_success_and_threshold_boundary(self):
        result = self.run_batch('1')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (self.output / 'video_fixed.vtt').read_text()
        self.assertIn('Corrected', text)
        self.assertIn('Second', text)
        self.assertEqual(self.report(), [])

    def test_threshold_failure_and_retry_clear_report(self):
        result = self.run_batch('0')
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.output / 'video_fixed.vtt').exists())
        failure, = self.report()
        self.assertEqual(failure['original_vtt'], str(self.vtt / 'video.vtt'))
        self.assertEqual(failure['fixed_txt'], str(self.fixed / 'video_fixed.txt'))
        self.assertIn('Too many restored lines', failure['reason'])
        self.assertEqual(self.run_batch().returncode, 0)
        self.assertEqual(self.report(), [])

    def test_unmatched_line(self):
        (self.fixed / 'video_strip.txt').write_text('0001-Original\n')
        self.assertEqual(self.run_batch().returncode, 1)
        self.assertIn('Unmatched lines', self.report()[0]['reason'])
        self.assertFalse((self.output / 'video_fixed.vtt').exists())

    def test_missing_input_and_continue(self):
        (self.fixed / 'missing_fixed.txt').write_text('0001-Test\n')
        self.assertEqual(self.run_batch().returncode, 1)
        self.assertTrue((self.output / 'video_fixed.vtt').exists())
        self.assertEqual(len(self.report()), 1)
        self.assertIn('Strip text file not found', self.report()[0]['reason'])

    def test_missing_vtt(self):
        (self.vtt / 'video.vtt').unlink()
        self.assertEqual(self.run_batch().returncode, 1)
        self.assertIn('VTT file not found', self.report()[0]['reason'])

    def test_existing_output_is_skipped(self):
        output = self.output / 'video_fixed.vtt'
        output.write_text('Existing output')
        (self.fixed / 'video_strip.txt').unlink()
        self.assertEqual(self.run_batch().returncode, 0)
        self.assertEqual(output.read_text(), 'Existing output')
        self.assertEqual(self.report(), [])

    def test_empty_run_clears_report(self):
        (self.output / 'revert_vtt_failures.json').write_text('[{}]')
        (self.fixed / 'video_fixed.txt').unlink()
        self.assertEqual(self.run_batch().returncode, 0)
        self.assertEqual(self.report(), [])

    def test_invalid_cli_arguments(self):
        for script in ('revert_vtt.py', 'batch_revert_vtt.py'):
            result = subprocess.run([sys.executable, str(SCRIPT_DIR / script)], capture_output=True)
            self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
