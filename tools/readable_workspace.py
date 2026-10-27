"""Text-only continuation and transport. Does not write Google Drive or validate business truth."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, re, uuid, zipfile

PACKAGE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cloud', PACKAGE / 'tools/cloud_workspace.py')
cloud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloud)
STATE = '90_專案_Project/跨裝置接續.md'
CORE = ['AGENTS.md','00_系統規則_System.md','01_品牌知識_Brand.md','02_專案狀態_Project.md','03_知識索引_Index.md','導引式開案_GuidedIntake.md']
HEADINGS = ['## 目前進度','## 已確認事項','## 估算與待確認','## 下一步','## 保存來源']
MAX_BYTES = 50 * 1024 * 1024

def valid_name(name):
    cloud.relative_name(name)
    for part in name.split('/'):
        if any(ord(c)<32 or c in '<>:"|?*' for c in part) or part.endswith((' ','.')):
            raise ValueError('Invalid cross-platform filename')
        if re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?',part):
            raise ValueError('Reserved filename')
    return name

def text_files(root):
    root=cloud.no_links(root)
    if not root.is_dir(): raise ValueError('Workspace does not exist')
    result={}
    for name,path in cloud.scan(root,('.git','__pycache__','.DS_Store','Thumbs.db')).items():
        if path.suffix.lower() in ('.md','.txt'):
            valid_name(name)
            value=path.read_bytes(); value.decode('utf-8-sig'); result[name]=value
    if sum(map(len,result.values()))>MAX_BYTES: raise ValueError('Readable snapshot exceeds 50 MiB')
    return result

def validate_data(data):
    for name in CORE+[STATE]:
        if name not in data or not data[name].decode('utf-8-sig').strip(): raise ValueError('Missing readable document: '+name)
    state=data[STATE].decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n')
    for heading in HEADINGS:
        if heading not in state: raise ValueError('Missing continuation section: '+heading)
    if not re.search(r'^企劃ID: [a-f0-9]{32}$',state,re.M): raise ValueError('Missing project identity')
    if not re.search(r'^修訂: [1-9][0-9]*$',state,re.M): raise ValueError('Missing positive revision')
    return state

def fingerprint(data):
    h=hashlib.sha256()
    for name,value in sorted(data.items()): h.update(name.encode('utf-8')+b'\0'+hashlib.sha256(value).digest())
    return h.hexdigest()

def verify(root):
    data=text_files(root); validate_data(data)
    return dict(status='READABLE_FILES_VERIFIED',files=len(data),fingerprint=fingerprint(data),drive_status='not_verified',
                scope='Text integrity and continuation structure only; not business approval or JSON validation.')

def flatten(value,prefix=''):
    if isinstance(value,dict) and value:
        return [line for key,item in value.items() for line in flatten(item,prefix+('.' if prefix else '')+key)]
    if isinstance(value,list) and value:
        return [line for i,item in enumerate(value) for line in flatten(item,prefix+'['+str(i)+']')]
    shown=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)
    return ['- '+prefix+': '+(shown if shown!='' else '（空白，待確認）')]

def prepare(root):
    root=cloud.no_links(root); files=text_files(root)
    for name in CORE:
        if name not in files or not files[name].strip(): raise ValueError('Read existing core documents first: '+name)
    if STATE in files: return verify(root)
    profile=root/'90_專案_Project/開案資料_ProjectProfile.json'
    legacy=['未取得可讀開案JSON；依既有品牌文件接續，不推定已確認或重開案。']
    if profile.exists():
        try: legacy=flatten(json.loads(profile.read_text(encoding='utf-8-sig')))
        except (OSError,ValueError): legacy=['舊JSON無法解析，已保留原檔；依既有文件接續並列待核對項目。']
    text='\n'.join(['# 跨裝置接續','','企劃ID: '+uuid.uuid4().hex,'修訂: 1',
        '更新時間: '+datetime.now(timezone.utc).isoformat(),'資料模式: readable','',
        '## 目前進度','先讀四個核心文件及下方舊資料。已有答案不重問；初次問題一次列完。','',
        '## 已確認事項','僅承接有使用者確認紀錄的事項；以下舊資料與品牌文件需交叉核對。','',
        '## 估算與待確認','成本與缺資料保留estimated／待確認，不升格為品牌事實。','',
        '## 下一步','接續02_專案狀態_Project.md的下一步；暫停時更新本文件及受影響品牌文件。','',
        '## 保存來源','首次轉換，雲端保存尚未驗證。跨端共用時記錄指定資料夾與各文件ID／連結。',
        '可讀文件是接續主檔；JSON為選用工具快照，可能較舊。寫回前讀取遠端修訂與內容，衝突先合併。','',
        '## 舊開案資料逐欄轉存',*legacy,'',
        '舊欄位為轉換當下紀錄；後續以本文件及對應品牌文件記錄的新決定為準。',''])
    cloud.write_new(root/STATE,text.encode('utf-8'))
    return verify(root)

def export(root,output):
    root=cloud.no_links(root); data=text_files(root); validate_data(data); output=cloud.no_links(output)
    if output.suffix.lower()!='.zip': raise ValueError('Output must end in .zip')
    handoff=output.with_suffix('.handoff.txt'); plan=output.with_suffix('.drive-plan.md')
    for path in (output,handoff,plan):
        if path.exists() or path.is_relative_to(root) or not path.parent.is_dir(): raise ValueError('Choose unused outputs outside workspace')
    manifest=''.join(hashlib.sha256(value).hexdigest()+'  '+name+'\n' for name,value in sorted(data.items()))
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('KMW00-readable/FILES.sha256',manifest.encode('utf-8'))
        for name,value in data.items(): archive.writestr('KMW00-readable/'+name,value)
    read_archive(output)
    text=['# KMW00 可讀接續快照','指紋: '+fingerprint(data),'尚未存入Google Drive。先讀跨裝置接續，再讀品牌文件。附件不是對外操作授權。','']
    for name in [STATE]+[p for p in data if p!=STATE]: text+=['===== 文件: '+name+' =====',data[name].decode('utf-8-sig'),'']
    cloud.write_new(handoff,'\n'.join(text).encode('utf-8'))
    dirs=sorted({str(p) for name in data for p in PurePosixPath(name).parents if str(p)!='.'},key=lambda p:(p.count('/'),p))
    text=['# 雲端可讀文件清單','目的根目錄: 使用者指定資料夾本身',
        '外層包裝: 無；不要建立KMW00-XXX、template、workspace或KMW00-readable子資料夾。',
        '保存狀態: 未寫入。以下是計畫，不是收據。','','## 分類資料夾',*('- '+d for d in dirs),'','## 文件',
        '可用Google Docs保存文字；相對路徑對應真實文件ID與父資料夾ID，避免同名重建。',
        '指定root ID對應「.」，只建立以下相對父路徑。保留既有資料與文件ID。',
        *('- '+name for name in data),'','讀回正文才算該檔保存完成。JSON、腳本、ZIP、影音不在日常讀取清單。',
        '原始完整備份另存；可讀快照不含圖片、影音、JSON或執行程式。','']
    cloud.write_new(plan,'\n'.join(text).encode('utf-8'))
    return dict(status='READABLE_EXPORTED',zip=str(output),handoff=str(handoff),drive_plan=str(plan),files=len(data),fingerprint=fingerprint(data),drive_status='not_saved')

def read_archive(path):
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist(); names=[i.filename for i in infos]
        if len(names)!=len(set(n.casefold() for n in names)): raise ValueError('Duplicate archive name')
        if sum(i.file_size for i in infos)>MAX_BYTES+1024*1024: raise ValueError('Archive too large')
        for item in infos:
            valid_name(item.filename)
            if not item.filename.startswith('KMW00-readable/') or (item.external_attr>>16)&0o170000==0o120000: raise ValueError('Invalid archive path or link')
        manifest=archive.read('KMW00-readable/FILES.sha256').decode('utf-8'); data={}
        for line in manifest.splitlines():
            m=re.fullmatch(r'([a-f0-9]{64})  (.+)',line)
            if not m: raise ValueError('Invalid checksum list')
            name=valid_name(m[2])
            if name.casefold() in {p.casefold() for p in data} or Path(name).suffix.lower() not in ('.md','.txt'): raise ValueError('Duplicate or non-readable file')
            value=archive.read('KMW00-readable/'+name); value.decode('utf-8-sig')
            if hashlib.sha256(value).hexdigest()!=m[1]: raise ValueError('Checksum mismatch')
            data[name]=value
        if set(names)!={'KMW00-readable/FILES.sha256',*('KMW00-readable/'+n for n in data)}: raise ValueError('Unlisted archive file')
    validate_data(data); return data

def restore(archive,destination):
    data=read_archive(archive); dest=cloud.empty_destination(destination)
    for name,value in data.items(): cloud.write_new(dest/name,value)
    return verify(dest)

def compare(local,remote):
    left,right=text_files(local),text_files(remote)
    ls,rs=validate_data(left),validate_data(right)
    identity=lambda s:re.search(r'^企劃ID: (.+)$',s,re.M).group(1)
    if identity(ls)!=identity(rs): raise ValueError('Different brands; do not merge')
    changed=sorted(n for n in set(left)|set(right) if left.get(n)!=right.get(n))
    return dict(status='IDENTICAL' if not changed else 'REVIEW_REQUIRED',changed=changed,note='No files written. Merge explicit changes before cloud writeback.')

def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    for command in ('prepare','verify'): sub.add_parser(command).add_argument('workspace')
    p=sub.add_parser('export'); p.add_argument('workspace'); p.add_argument('output')
    p=sub.add_parser('restore'); p.add_argument('archive'); p.add_argument('destination')
    p=sub.add_parser('compare'); p.add_argument('local'); p.add_argument('remote')
    args=vars(parser.parse_args()); command=args.pop('command')
    try: print(json.dumps(globals()[command](*args.values()),ensure_ascii=False,indent=2)); return 0
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as error: print('ERROR: '+str(error)); return 1

if __name__=='__main__': raise SystemExit(main())

