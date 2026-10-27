from pathlib import Path
import hashlib,json,sys,zipfile, tempfile
R=Path(__file__).resolve().parents[1]
T=R/'template'
version=(R/'VERSION').read_text().strip()
manifest={'template_id':'kmw00-brand-marketing','template_type':'generic_core','core_release_version':version,'paths':{'profile':'90_專案_Project/開案資料_ProjectProfile.json','project_status':'02_專案狀態_Project.md','index':'03_知識索引_Index.md'},'required_files':sorted(p.relative_to(T).as_posix() for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts)}
(T/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
files=sorted(p for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
(R/'payload.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(R).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
if '--manifest-only' in sys.argv:print('Manifest ready:',len(files));sys.exit(0)
out=R/'artifacts';out.mkdir(exist_ok=True)
zip_path=out/f'KMW00-brand-marketing-{version}.zip'
root=f'KMW00-brand-marketing-{version}'
sources=sorted(p for p in R.rglob('*') if p.is_file() and not any(x in p.relative_to(R).parts for x in ['.git','artifacts','__pycache__']) and p.suffix!='.pyc')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sources:z.write(p,root+'/'+p.relative_to(R).as_posix())
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(sources)
    assert len({n.split('/')[0] for n in z.namelist()})==1
    assert all('\\' not in n and '..' not in Path(n).parts for n in z.namelist())
    assert len({n.casefold() for n in z.namelist()})==len(z.namelist())
    assert all(not any(ord(c)>127 for c in i.filename) or i.flag_bits&0x800 for i in z.infolist())
    with tempfile.TemporaryDirectory(prefix='kmw00-zip-') as tmp:
        z.extractall(tmp)
        for p in sources:assert p.read_bytes()==(Path(tmp)/root/p.relative_to(R)).read_bytes()
print('ZIP PASS:',len(sources),'files;',zip_path)
print('SHA256:',hashlib.sha256(zip_path.read_bytes()).hexdigest())