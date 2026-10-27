import importlib.util,json,shutil,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('readable',ROOT/'tools/readable_workspace.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class ReadableTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kmw00-readable-')
        self.base=Path(self.tmp.name).resolve();self.root=self.base/'品牌 中文'
        shutil.copytree(ROOT/'template',self.root)
    def tearDown(self): self.tmp.cleanup()
    def prepare(self): return r.prepare(self.root)
    def export(self): self.prepare();return r.export(self.root,self.base/'私人快照.zip')
    def no_json(self):
        for p in self.root.rglob('*.json'): p.unlink()
    def test_no_json_prepare_export_restore(self):
        self.no_json();result=self.export();dest=self.base/'另一端'
        r.restore(result['zip'],dest)
        self.assertEqual(r.compare(self.root,dest)['status'],'IDENTICAL')
        self.assertFalse(list(dest.rglob('*.json')))
        self.assertTrue((dest/'00_系統_System').is_dir())
        self.assertFalse((dest/'KMW00-readable').exists())
    def test_every_legacy_field_preserved(self):
        p=self.root/'90_專案_Project/開案資料_ProjectProfile.json'
        value=json.loads(p.read_text(encoding='utf-8'))
        value['brand']['name']='真實品牌甲';value['assumptions']=[dict(item='成本',value=123.45,status='estimated')]
        value['confirmed_decisions']=['使用者確認售價'];p.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
        self.prepare();text=(self.root/r.STATE).read_text(encoding='utf-8')
        for line in r.flatten(value):self.assertIn(line,text)
        self.assertIn('123.45',text);self.assertIn('estimated',text);self.assertIn('使用者確認售價',text)
    def test_repeat_preserves_identity_and_edits(self):
        self.prepare();p=self.root/r.STATE
        p.write_text(p.read_text(encoding='utf-8')+'\n已答問題不再問。\n',encoding='utf-8')
        before=r.text_files(self.root);self.prepare();self.assertEqual(before,r.text_files(self.root))
    def test_bad_json_is_not_blocking(self):
        p=self.root/'90_專案_Project/開案資料_ProjectProfile.json';p.write_text('{broken',encoding='utf-8')
        self.prepare();self.assertEqual(p.read_text(encoding='utf-8'),'{broken')
        self.assertIn('無法解析',(self.root/r.STATE).read_text(encoding='utf-8'));self.export()
    def test_json_removed_after_migration(self):
        self.prepare();before=(self.root/r.STATE).read_bytes();self.no_json()
        self.export();self.assertEqual(before,(self.root/r.STATE).read_bytes())
    def test_plan_has_direct_root_and_no_json_files(self):
        result=self.export();plan=Path(result['drive_plan']).read_text(encoding='utf-8')
        self.assertIn('目的根目錄: 使用者指定資料夾本身',plan)
        self.assertIn('- 00_系統_System',plan);self.assertIn('- 10_品牌_Brand',plan)
        paths=[line[2:] for line in plan.splitlines() if line.startswith('- ')]
        self.assertTrue(all(not p.endswith('.json') for p in paths))
        self.assertTrue(all(not p.startswith(('workspace/','template/','KMW00-')) for p in paths))
    def test_txt_handoff_contains_complete_state(self):
        result=self.export();text=Path(result['handoff']).read_text(encoding='utf-8')
        self.assertIn((self.root/r.STATE).read_text(encoding='utf-8'),text)
        self.assertEqual(result['drive_status'],'not_saved')
    def test_desktop_phone_desktop_roundtrip(self):
        result=self.export();phone=self.base/'手機';r.restore(result['zip'],phone)
        p=phone/'01_品牌知識_Brand.md';p.write_text('品牌更新：目標客群已確認；成本仍為估算。',encoding='utf-8')
        state=phone/r.STATE;state.write_text(state.read_text(encoding='utf-8').replace('修訂: 1','修訂: 2')+'\n下一步：完成成交路徑。\n',encoding='utf-8')
        second=r.export(phone,self.base/'回電腦.zip');desktop=self.base/'新電腦副本';r.restore(second['zip'],desktop)
        self.assertEqual(r.compare(phone,desktop)['status'],'IDENTICAL')
        self.assertEqual((desktop/'01_品牌知識_Brand.md').read_text(encoding='utf-8'),p.read_text(encoding='utf-8'))
        self.assertEqual(r.compare(self.root,desktop)['status'],'REVIEW_REQUIRED')
    def test_nonempty_destination_unchanged(self):
        result=self.export();target=self.base/'已有';target.mkdir();(target/'私有.txt').write_text('keep',encoding='utf-8')
        with self.assertRaises(ValueError):r.restore(result['zip'],target)
        self.assertEqual(list(target.iterdir()),[target/'私有.txt'])
    def test_conflict_detected_even_same_revision(self):
        result=self.export();other=self.base/'其他副本';r.restore(result['zip'],other)
        p=other/'01_品牌知識_Brand.md';p.write_text('另一裝置修改',encoding='utf-8')
        before=r.text_files(self.root);self.assertEqual(r.compare(self.root,other)['status'],'REVIEW_REQUIRED')
        self.assertEqual(before,r.text_files(self.root))
    def test_different_brand_rejected(self):
        self.prepare();other=self.base/'不同品牌';shutil.copytree(ROOT/'template',other);r.prepare(other)
        with self.assertRaises(ValueError):r.compare(self.root,other)
    def test_missing_core_rejected_without_json(self):
        self.no_json();self.prepare();(self.root/r.CORE[1]).unlink()
        with self.assertRaises(ValueError):r.export(self.root,self.base/'bad.zip')
        self.assertFalse((self.base/'bad.zip').exists())
    def test_invalid_identity_or_revision(self):
        self.prepare();p=self.root/r.STATE;before=p.read_text(encoding='utf-8')
        for bad in [before.replace('修訂: 1','修訂: 0'),before.replace('企劃ID:','失去識別:')]:
            p.write_text(bad,encoding='utf-8')
            with self.assertRaises(ValueError):r.verify(self.root)
    def test_corrupt_archive_rejected_before_write(self):
        result=self.export();bad=self.base/'broken.zip'
        with zipfile.ZipFile(result['zip']) as old,zipfile.ZipFile(bad,'w') as new:
            for name in old.namelist():new.writestr(name,b'changed' if name.endswith('/AGENTS.md') else old.read(name))
        with self.assertRaises(ValueError):r.restore(bad,self.base/'不可建立')
        self.assertFalse((self.base/'不可建立').exists())
    def test_traversal_and_unlisted_rejected(self):
        result=self.export()
        for i,extra in enumerate(['../escape.md','KMW00-readable/extra.md']):
            bad=self.base/f'bad{i}.zip';shutil.copyfile(result['zip'],bad)
            with zipfile.ZipFile(bad,'a') as z:z.writestr(extra,'bad')
            with self.assertRaises(ValueError):r.restore(bad,self.base/f'target{i}')
    def test_export_conflict_and_recursive_rejected(self):
        self.prepare()
        with self.assertRaises(ValueError):r.export(self.root,self.root/'recursive.zip')
        self.export();before=(self.base/'私人快照.zip').read_bytes()
        with self.assertRaises(ValueError):r.export(self.root,self.base/'私人快照.zip')
        self.assertEqual(before,(self.base/'私人快照.zip').read_bytes())
    def test_cli_without_json(self):
        self.no_json()
        for command in ['prepare','verify']:
            result=subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'tools/readable_workspace.py'),command,str(self.root)],capture_output=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    @unittest.skipIf(sys.platform=='win32','Native links tested on macOS/Linux')
    def test_symlink_rejected(self):
        self.prepare();(self.root/'link.md').symlink_to(ROOT/'README.md')
        with self.assertRaises(ValueError):r.export(self.root,self.base/'bad.zip')
    def test_readable_validation_does_not_claim_business_approval(self):
        result=self.prepare();self.assertIn('not business approval',result['scope'])
        self.assertEqual(result['drive_status'],'not_verified')
    def test_template_rules_match_modes(self):
        for name in ['INSTALL_PROMPT.txt','MOBILE_INSTALL_PROMPT.txt']:
            text=(ROOT/name).read_text(encoding='utf-8')
            self.assertIn('禁止自行增加KMW00-XXX',text);self.assertIn('一次全部列完',text)
            self.assertIn('JSON不是手機',text)
        self.assertNotIn('逐檔保存原始MD／JSON',(ROOT/'template/AGENTS.md').read_text(encoding='utf-8'))

if __name__=='__main__': unittest.main()

