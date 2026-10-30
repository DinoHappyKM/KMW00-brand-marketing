import os,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(os.name=='nt','Native Windows launcher')
class NativeWindowsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kmw00-native-')
        self.base=Path(self.tmp.name).resolve()
    def tearDown(self):self.tmp.cleanup()
    def launch(self,dest=None):
        cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'Install-Windows-Interactive.ps1'),'-NonInteractive']
        if dest is not None:cmd+=['-Destination',str(dest)]
        return subprocess.run(cmd,capture_output=True,timeout=30)
    def test_native_install_direct_root(self):
        dest=self.base/'示範帽服 測試';result=self.launch(dest)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue((dest/'00_系統_System').is_dir())
        self.assertTrue((dest/'10_品牌_Brand').is_dir())
        self.assertTrue((dest/'20_行銷_Marketing').is_dir())
        self.assertFalse((dest/'template').exists())
    def test_native_repeat_keeps_private_data(self):
        dest=self.base/'既有品牌';self.assertEqual(self.launch(dest).returncode,0)
        private=dest/'01_品牌知識_Brand.md';private.write_text('使用者已確認資料',encoding='utf-8')
        before=private.read_bytes();self.assertEqual(self.launch(dest).returncode,0)
        self.assertEqual(before,private.read_bytes())
    def test_native_conflict_stops_without_overwrite(self):
        dest=self.base/'私有';dest.mkdir();private=dest/'私人.txt';private.write_bytes(b'keep')
        self.assertNotEqual(self.launch(dest).returncode,0)
        self.assertEqual(list(dest.iterdir()),[private])
    def test_native_missing_destination_does_not_prompt(self):
        self.assertNotEqual(self.launch().returncode,0)
    def test_native_relative_destination_rejected(self):
        self.assertNotEqual(self.launch('relative-brand').returncode,0)
    def test_native_special_characters_path(self):
        dest=self.base/'品牌 & (中文)';self.assertEqual(self.launch(dest).returncode,0)
        self.assertTrue((dest/'AGENTS.md').exists())

class DesktopFlowTests(unittest.TestCase):
    def test_release_version_is_platform_neutral(self):
        value=(ROOT/'VERSION').read_bytes()
        self.assertNotIn(b'\r',value)
        self.assertEqual(value.strip(),b'0.1.0-beta.4')

    def test_desktop_cloud_is_optional_and_error_recovery_bounded(self):
        prompt=(ROOT/'INSTALL_PROMPT.txt').read_text(encoding='utf-8')
        self.assertIn('只有我要求跨裝置保存時',prompt)
        self.assertIn('有界診斷',prompt);self.assertIn('未取得核准就不執行',prompt)
        self.assertIn('不修改全域設定',prompt)
    def test_launcher_is_user_process_not_global_policy(self):
        launcher=(ROOT/'Start-Windows.cmd').read_text(encoding='utf-8')
        code=(ROOT/'Install-Windows-Interactive.ps1').read_text(encoding='utf-8-sig')
        self.assertIn('%~dp0Install-Windows-Interactive.ps1',launcher)
        self.assertNotIn('Set-ExecutionPolicy',code)
        self.assertNotIn('Start-Process',code)
        self.assertIn('Install-Windows.ps1',code)

if __name__=='__main__':unittest.main()

