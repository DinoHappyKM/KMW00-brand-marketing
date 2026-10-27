import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cloud_workspace', ROOT / 'tools/cloud_workspace.py')
cloud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloud)


class CloudWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='kmw00-cloud-test-')
        self.base = Path(self.tmp.name).resolve()
        self.workspace = self.base / '私人品牌 測試'

    def tearDown(self):
        cloud.PACKAGE = ROOT
        self.tmp.cleanup()

    def init(self):
        return cloud.initialize(self.workspace, 'a' * 40)

    def test_cloud_init_and_cli(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/cloud_workspace.py'),
                                 'init', str(self.workspace), '--source-commit', 'a' * 40],
                                capture_output=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual(status['status'], 'WORKSPACE_INITIALIZED')
        self.assertEqual(status['drive_status'], 'not_saved')
        self.assertEqual(cloud.checked_workspace(self.workspace), self.workspace)
        marker = json.loads((self.workspace / '.kmw00-install.json').read_text(encoding='utf-8'))
        self.assertEqual(marker['source_commit'], 'a' * 40)

    def test_repeat_preserves_private_edits(self):
        self.init()
        private = self.workspace / '01_品牌知識_Brand.md'
        private.write_text('已填品牌資料', encoding='utf-8')
        self.assertEqual(self.init()['status'], 'ALREADY_INSTALLED')
        self.assertEqual(private.read_text(encoding='utf-8'), '已填品牌資料')

    def test_nonempty_and_package_destinations_rejected(self):
        self.workspace.mkdir()
        private = self.workspace / '私人.txt'
        private.write_text('keep', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.init()
        self.assertEqual(list(self.workspace.iterdir()), [private])
        with self.assertRaises(ValueError):
            cloud.initialize(ROOT / 'do-not-create')

    def test_invalid_commit_rejected(self):
        with self.assertRaises(ValueError):
            cloud.initialize(self.workspace, 'main')
        self.assertFalse(self.workspace.exists())

    def altered_package(self):
        target = self.base / 'package'
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '__pycache__', 'artifacts'))
        cloud.PACKAGE = target
        return target

    def test_tampered_template_rejected_before_writes(self):
        package = self.altered_package()
        (package / 'template/README.md').write_text('tampered', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.init()
        self.assertFalse(self.workspace.exists())

    def test_duplicate_and_unlisted_payload_rejected(self):
        package = self.altered_package()
        manifest = package / 'payload.sha256'
        original = manifest.read_text(encoding='utf-8')
        manifest.write_text(original + original.splitlines()[0] + '\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.init()
        manifest.write_text(original, encoding='utf-8')
        (package / 'template/extra.txt').write_text('unlisted', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.init()
        self.assertFalse(self.workspace.exists())

    def test_private_handoff_round_trip(self):
        self.init()
        private = self.workspace / '90_專案_Project/補充資料.md'
        private.write_text('中文私人筆記與已確認價格；不可送回公開倉庫。', encoding='utf-8')
        archive = self.base / '私人企劃.zip'
        result = cloud.export_workspace(self.workspace, archive)
        self.assertEqual(result['drive_status'], 'not_saved')
        plan = json.loads(Path(result['drive_plan']).read_text(encoding='utf-8'))
        self.assertIn('90_專案_Project', plan['directories'])
        self.assertTrue(any(e['path'] == '90_專案_Project/補充資料.md' for e in plan['files']))
        self.assertIn('中文私人筆記', Path(result['handoff']).read_text(encoding='utf-8'))
        restored = self.base / '另一裝置'
        cloud.restore_workspace(archive, restored)
        for name, source in cloud.scan(self.workspace).items():
            self.assertEqual(source.read_bytes(), (restored / name).read_bytes())
        with self.assertRaises(ValueError):
            cloud.restore_workspace(archive, restored)

    def test_export_never_overwrites_or_recurses(self):
        self.init()
        with self.assertRaises(ValueError):
            cloud.export_workspace(self.workspace, self.workspace / 'recursive.zip')
        output = self.base / 'exists.zip'
        output.write_bytes(b'keep')
        with self.assertRaises(ValueError):
            cloud.export_workspace(self.workspace, output)
        self.assertEqual(output.read_bytes(), b'keep')

    def test_corrupt_backup_rejected_before_writes(self):
        self.init()
        archive = self.base / 'backup.zip'
        cloud.export_workspace(self.workspace, archive)
        corrupt = self.base / 'corrupt.zip'
        with zipfile.ZipFile(archive) as source, zipfile.ZipFile(corrupt, 'w') as target:
            for name in source.namelist():
                target.writestr(name, b'tampered' if name == 'workspace/README.md' else source.read(name))
        destination = self.base / 'should-not-exist'
        with self.assertRaises(ValueError):
            cloud.restore_workspace(corrupt, destination)
        self.assertFalse(destination.exists())

    def test_archive_traversal_and_extra_files_rejected(self):
        self.init()
        for extra in ('../outside.txt', 'workspace/unlisted.txt'):
            archive = self.base / ('bad-' + str(len(extra)) + '.zip')
            cloud.export_workspace(self.workspace, archive)
            with zipfile.ZipFile(archive, 'a') as target:
                target.writestr(extra, 'bad')
            with self.assertRaises(ValueError):
                cloud.restore_workspace(archive, self.base / 'unsafe')
        self.assertFalse((self.base / 'outside.txt').exists())

    @unittest.skipIf(sys.platform == 'win32', 'Native symlink fixture tested on Linux and macOS')
    def test_source_and_destination_symlinks_rejected(self):
        self.init()
        (self.workspace / 'linked.md').symlink_to(ROOT / 'README.md')
        with self.assertRaises(ValueError):
            cloud.export_workspace(self.workspace, self.base / 'linked.zip')
        link = self.base / 'alias'
        link.symlink_to(self.workspace, target_is_directory=True)
        with self.assertRaises(ValueError):
            cloud.initialize(link)


if __name__ == '__main__':
    unittest.main()
