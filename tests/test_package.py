import copy,importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('verify',R/'template/70_工具_Tools/verify_project.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kmw00-test-')
        self.base=Path(self.tmp.name); self.root=self.base/'品牌資料 測試'
        shutil.copytree(R/'template',self.root)
        self.profile=self.root/'90_專案_Project/開案資料_ProjectProfile.json'
    def tearDown(self):self.tmp.cleanup()
    def edit(self,fn):
        obj=json.loads(self.profile.read_text(encoding='utf-8'));fn(obj)
        self.profile.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf-8')
    def test_baseline(self):self.assertEqual(v.verify(self.root),[])
    def test_invalid_sales(self):
        self.edit(lambda p:p['sales_model'].update(primary_type='Z'));self.assertTrue(v.verify(self.root))
    def test_invalid_module(self):
        self.edit(lambda p:p['industry'].update(module_status='invalid_state'));self.assertTrue(v.verify(self.root))
    def test_empty_confirmed_brand(self):
        self.edit(lambda p:p['brand'].update(status='confirmed'));self.assertTrue(v.verify(self.root))
    def test_premature_build(self):
        self.edit(lambda p:p['system_build'].update(status='confirmed'));self.assertTrue(v.verify(self.root))
    def test_missing_file(self):
        (self.root/'01_品牌知識_Brand.md').unlink();self.assertTrue(v.verify(self.root))
    def test_bad_json(self):
        self.profile.write_text('{broken',encoding='utf-8');self.assertTrue(v.verify(self.root))
    def test_product_credit(self):
        with (self.root/'README.md').open('a',encoding='utf-8') as f:f.write('\n黃嘉偉KMW00品牌行銷\n')
        self.assertEqual(v.verify(self.root),[])
    def test_unknown_costs_continue(self):
        def change(p):
            p['offer_333']['status']='estimated'
            p['assumptions']=[dict(item='直接人工',value='低中高情境，尚無可靠金額',basis='時數乘時薪，等待地區參考',source='未取得',date='2026-10-27',region='待確認',confidence='low',status='estimated')]
        self.edit(change);self.assertEqual(v.verify(self.root),[])
    def test_batch_documents(self):
        text='\n'.join(p.read_text(encoding='utf-8') for p in self.root.rglob('*.md'))
        self.assertNotIn('一次只問一題',text);self.assertNotIn('只補問一題',text)
        self.assertIn('一次列完',text);self.assertIn('工作假設',text)
    def install(self,dest,package=R):
        if os.name=='nt':cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(package/'Install-Windows.ps1'),'-Destination',str(dest)]
        else:cmd=['bash',str(package/('Install-Mac.sh' if sys.platform=='darwin' else 'Install-Linux.sh')),str(dest)]
        # ExecutionPolicy Bypass is only the test subprocess, never a machine policy change.
        return subprocess.run(cmd,capture_output=True,timeout=30)
    def test_installer_new(self):
        target=self.base/'新品牌 空間';result=self.install(target)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(v.verify(target),[]);self.assertTrue((target/'.kmw00-install.json').exists())
        for source in (R/'template').rglob('*'):
            if source.is_file():self.assertEqual(source.read_bytes(),(target/source.relative_to(R/'template')).read_bytes())
    def test_installer_repeat_preserves_data(self):
        target=self.base/'重複';self.assertEqual(self.install(target).returncode,0)
        private=target/'01_品牌知識_Brand.md';private.write_text('學員已填資料',encoding='utf-8')
        self.assertEqual(self.install(target).returncode,0)
        self.assertEqual(private.read_text(encoding='utf-8'),'學員已填資料')
    def test_installer_conflict(self):
        target=self.base/'已有';target.mkdir();(target/'私人.txt').write_text('keep',encoding='utf-8')
        self.assertNotEqual(self.install(target).returncode,0)
        self.assertEqual(list(target.iterdir()),[target/'私人.txt'])
    def test_installer_tampered(self):
        package=self.base/'套件';shutil.copytree(R,package,ignore=shutil.ignore_patterns('__pycache__','.git','artifacts'))
        (package/'template/README.md').write_text('tampered',encoding='utf-8')
        target=self.base/'不應建立';self.assertNotEqual(self.install(target,package).returncode,0)
        self.assertFalse(target.exists())
    def test_source_case_paths(self):
        names=[p.relative_to(R/'template').as_posix() for p in (R/'template').rglob('*') if p.is_file()]
        self.assertEqual(len(names),len(set(n.casefold() for n in names)))
if __name__=='__main__':unittest.main(verbosity=2)
