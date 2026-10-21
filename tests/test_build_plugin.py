import importlib.util
import json
from pathlib import Path, PurePosixPath
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

FILE = Path(__file__).parents[1] / 'scripts/build_plugin.py'


class BuildPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('build_plugin', FILE)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plugin = self.root / 'big-repo'
        for folder in ('.codex-plugin', '.claude-plugin', 'skills/demo', 'scripts', '__pycache__', 'work'):
            (self.plugin / folder).mkdir(parents=True)
        for name in ('.codex-plugin', '.claude-plugin'):
            (self.plugin / name / 'plugin.json').write_text(json.dumps({'name': 'big-repo', 'version': '0.2.0'}))
        (self.plugin / 'skills/demo/SKILL.md').write_bytes(b'---\r\nname: demo\r\n---\r\n')
        (self.plugin / 'scripts/explore.py').write_text('print(1)\n')
        (self.plugin / '__pycache__/test.pyc').write_bytes(b'cache')
        (self.plugin / 'work/secret.txt').write_text('must not ship')

    def test_archive_reproducible_and_filtered(self):
        first = self.m.build(self.plugin, self.root / 'out1')
        second = self.m.build(self.plugin, self.root / 'out2')
        self.assertEqual(Path(first['archive']).read_bytes(), Path(second['archive']).read_bytes())
        self.assertEqual(first['sha256'], second['sha256'])
        self.assertEqual(Path(first['archive']).name, 'Big-Repo-0.2.0.zip')
        with zipfile.ZipFile(first['archive']) as archive:
            self.assertIsNone(archive.testzip())
            self.assertFalse(any('secret' in name or '__pycache__' in name for name in archive.namelist()))
            self.assertNotIn(b'\r', archive.read('Big-Repo/skills/demo/SKILL.md'))
        self.assertTrue(Path(first['checksum']).exists())

    def test_version_mismatch_and_output_inside_plugin_blocked(self):
        with self.assertRaises(ValueError):
            self.m.build(self.plugin, self.plugin / 'dist')
        (self.plugin / '.claude-plugin/plugin.json').write_text('{"name":"big-repo","version":"0.1.0"}')
        with self.assertRaises(ValueError):
            self.m.build(self.plugin, self.root / 'out')

    def test_existing_predictable_temporary_file_is_preserved(self):
        output = self.root / 'out'
        output.mkdir()
        sentinel = output / '.big-repo-0.2.0.zip.tmp'
        sentinel.write_bytes(b'unrelated file')
        self.m.build(self.plugin, output)
        self.assertTrue(sentinel.exists())
        self.assertEqual(sentinel.read_bytes(), b'unrelated file')

    def test_archive_write_failure_preserves_previous_outputs_and_cleans_staging(self):
        self.check_failed_build_preserves_outputs(
            patch.object(zipfile.ZipFile, 'writestr', side_effect=OSError('injected write failure')),
            OSError,
        )

    def test_digest_failure_does_not_publish_new_archive(self):
        self.check_failed_build_preserves_outputs(
            patch.object(self.m.hashlib, 'sha256', side_effect=OSError('injected digest failure')),
            OSError,
        )

    def test_keyboard_interrupt_cleans_staging(self):
        self.check_failed_build_preserves_outputs(
            patch.object(zipfile.ZipFile, 'writestr', side_effect=KeyboardInterrupt),
            KeyboardInterrupt,
        )

    def test_publish_failure_cleans_staging(self):
        self.check_failed_build_preserves_outputs(
            patch.object(Path, 'replace', side_effect=OSError('injected publish failure')),
            OSError,
        )

    def check_failed_build_preserves_outputs(self, failure, error):
        output = self.root / 'out'
        self.m.build(self.plugin, output)
        previous = {p.name: p.read_bytes() for p in output.iterdir()}
        (self.plugin / 'scripts/explore.py').write_text('print(2)\n')
        with failure, self.assertRaises(error):
            self.m.build(self.plugin, output)
        self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, previous)

    def test_checksum_symlink_target_is_preserved(self):
        self.check_output_symlink_target_is_preserved('.sha256')

    def test_archive_symlink_target_is_preserved(self):
        self.check_output_symlink_target_is_preserved('')

    def check_output_symlink_target_is_preserved(self, suffix):
        output = self.root / 'out'
        output.mkdir()
        target = self.root / 'outside.txt'
        target.write_bytes(b'must remain unchanged')
        link = output / ('Big-Repo-0.2.0.zip' + suffix)
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest('Creating symlinks is unavailable in this environment')
        self.m.build(self.plugin, output)
        self.assertEqual(target.read_bytes(), b'must remain unchanged')
        self.assertFalse(link.is_symlink())

    def test_sort_order_portable_with_mixed_case(self):
        references = self.plugin / 'skills/demo/references'
        references.mkdir()
        (references / 'Z.md').write_text('Uppercase resource')
        (references / 'a.md').write_text('Lowercase resource')
        result = self.m.build(self.plugin, self.root / 'out')
        with zipfile.ZipFile(result['archive']) as archive:
            self.assertEqual(archive.namelist(), sorted(archive.namelist()))

    def test_unsafe_archive_names_rejected(self):
        for name in ['scripts/a\\b.txt', 'scripts/a:b.txt', 'scripts/CON.txt', 'scripts/trailing.']:
            with self.assertRaises(ValueError):
                self.m.portable_member(PurePosixPath(name))

    def test_resolved_resource_must_stay_inside_plugin(self):
        resource = self.plugin / 'scripts/explore.py'
        original = Path.resolve
        def resolve(path, *args, **kwargs):
            return self.root / 'outside.txt' if path == resource else original(path, *args, **kwargs)
        with patch.object(Path, 'resolve', resolve):
            with self.assertRaises(ValueError):
                self.m.checked_path(resource, self.plugin)

    def test_default_cli_output_is_outside_source_root(self):
        with patch('sys.argv', ['build']), patch.object(self.m, 'build', return_value={}) as build, redirect_stdout(StringIO()):
            self.assertEqual(self.m.main(), 0)
        plugin, output = build.call_args.args
        self.assertFalse(output.resolve().is_relative_to(plugin.resolve()))

    def test_cli_success_and_invalid_input(self):
        with patch('sys.argv', ['build', '--plugin', str(self.plugin), '--output', str(self.root / 'out')]), redirect_stdout(StringIO()):
            self.assertEqual(self.m.main(), 0)
        with patch('sys.argv', ['build', '--plugin', str(self.plugin), '--output', str(self.plugin / 'out')]), redirect_stdout(StringIO()):
            self.assertEqual(self.m.main(), 2)
