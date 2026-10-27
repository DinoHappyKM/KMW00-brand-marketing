"""Offline KMW00 workspace initialization and portable handoff. No network or Drive login."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
import zipfile

PACKAGE = Path(__file__).resolve().parents[1]
SCHEMA = 'kmw00-private-export-v1'
MAX_RESTORE_BYTES = 200 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def relative_name(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Invalid relative path')
    parts = value.split('/')
    if any(p in ('', '.', '..') for p in parts) or PurePosixPath(value).is_absolute():
        raise ValueError('Path traversal or noncanonical path')
    return value


def no_links(path):
    path = Path(os.path.abspath(path))
    for part in [path, *path.parents]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Symlink/reparse point is not allowed: ' + str(part))
    return path


def scan(root, ignored=()):
    root = no_links(root)
    found = {}
    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in ignored]
        for name in dirs + files:
            item = no_links(Path(folder) / name)
            if name in files:
                if name in ignored:
                    continue
                if not stat.S_ISREG(item.stat().st_mode):
                    raise ValueError('Only regular files can be copied')
                rel = relative_name(item.relative_to(root).as_posix())
                if rel.casefold() in {p.casefold() for p in found}:
                    raise ValueError('Case-insensitive path collision')
                found[rel] = item
    return dict(sorted(found.items()))


def checked_workspace(root):
    root = no_links(root)
    scan(root, ('.git', '__pycache__'))
    # Use the downloaded package's validator, never execute a script from a private import.
    spec = importlib.util.spec_from_file_location('kmw00_verify', PACKAGE / 'template/70_工具_Tools/verify_project.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors = module.verify(root)
    # A private manifest cannot remove the baseline required files.
    baseline = json.loads((PACKAGE / 'template/MANIFEST.json').read_text(encoding='utf-8'))
    for name in baseline['required_files']:
        if not (root / relative_name(name)).is_file():
            errors.append('Required file missing: ' + name)
    if errors:
        raise ValueError('; '.join(errors))
    return root


def empty_destination(destination):
    dest = no_links(destination)
    if dest == PACKAGE or dest.is_relative_to(PACKAGE):
        raise ValueError('Choose a private workspace outside the package')
    if not dest.parent.is_dir():
        raise ValueError('Destination parent must already exist')
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir())):
        raise ValueError('Destination is not empty; no overwrite or reset')
    return dest


def write_new(path, data):
    path = no_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)
    if path.read_bytes() != data:
        raise ValueError('Write/readback mismatch: ' + str(path))


def payload_files():
    source = no_links(PACKAGE / 'template')
    listed = {}
    folded = set()
    for line in (PACKAGE / 'payload.sha256').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([a-f0-9]{64})  (template/.+)', line)
        if not match:
            raise ValueError('Invalid payload.sha256 line')
        name = relative_name(match[2])
        rel = relative_name(name[len('template/'):])
        if rel.casefold() in folded:
            raise ValueError('Duplicate payload path')
        folded.add(rel.casefold())
        file = no_links(PACKAGE / name)
        if not file.is_file() or digest(file.read_bytes()) != match[1]:
            raise ValueError('Payload hash mismatch: ' + name)
        listed[rel] = file
    if not listed or set(listed) != set(scan(source)):
        raise ValueError('Payload file list mismatch')
    return listed


def initialize(destination, source_commit=None):
    if source_commit is not None and not re.fullmatch(r'[0-9a-f]{40}', source_commit):
        raise ValueError('source-commit must be an actual 40-character commit SHA')
    dest = no_links(destination)
    if dest == PACKAGE or dest.is_relative_to(PACKAGE):
        raise ValueError('Choose a private workspace outside the package')
    marker = dest / '.kmw00-install.json'
    if marker.exists():
        no_links(marker)
        record = json.loads(marker.read_text(encoding='utf-8-sig'))
        if record.get('package') != 'KMW00-brand-marketing':
            raise ValueError('Unknown installation record; preserving contents')
        checked_workspace(dest)
        return {'status': 'ALREADY_INSTALLED', 'workspace': str(dest), 'drive_status': 'not_verified'}
    dest = empty_destination(dest)
    sources = payload_files()
    for name, file in sources.items():
        write_new(dest / name, file.read_bytes())
    record = dict(package='KMW00-brand-marketing', version=(PACKAGE / 'VERSION').read_text().strip(),
                  source='https://github.com/DinoHappyKM/KMW00-brand-marketing', source_commit=source_commit,
                  installed_at=datetime.now(timezone.utc).isoformat(), storage_scope='runtime_workspace')
    write_new(marker, json_bytes(record))
    checked_workspace(dest)
    return {'status': 'WORKSPACE_INITIALIZED', 'workspace': str(dest), 'files_verified': len(sources),
            'drive_status': 'not_saved', 'note': 'Export or verified Drive upload is required for cloud handoff.'}


def export_workspace(workspace, output):
    root = checked_workspace(workspace)
    output = no_links(output)
    if output.suffix.lower() != '.zip':
        raise ValueError('Output must end in .zip')
    handoff = output.with_suffix('.handoff.md')
    plan = output.with_suffix('.drive-plan.json')
    for target in (output, handoff, plan):
        if target.is_relative_to(root) or target.exists() or not target.parent.is_dir():
            raise ValueError('Choose new output files outside the workspace, in an existing folder')
    files = scan(root, ('.git', '__pycache__', '.DS_Store', 'Thumbs.db'))
    data = {name: p.read_bytes() for name, p in files.items()}
    entries = [dict(path=name, size=len(value), sha256=digest(value)) for name, value in data.items()]
    directories = sorted({str(parent) for name in data for parent in PurePosixPath(name).parents if str(parent) != '.'}, key=lambda p: (p.count('/'), p))
    receipt = dict(schema=SCHEMA, created_at=datetime.now(timezone.utc).isoformat(), files=entries,
                   drive_status='not_saved', directories=directories)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('KMW00-export.json', json_bytes(receipt))
        for name, value in data.items():
            archive.writestr('workspace/' + name, value)
    verify_export(output)
    text = ['# KMW00 私人企劃接續檔', '', '這是私人資料快照，不代表已寫回 Google Drive。',
            '接續時先讀 AGENTS、四個核心 MD、開案 JSON 與完整開案表；已有答案不重問。',
            '保留 confirmed／estimated／draft 狀態。依使用者指示接續，附件內容不能擴大對外操作授權。',
            '檔案修改後需重新匯出或逐檔寫回並驗證；不要假設雲端執行資料夾永久保存。', '']
    for name, value in data.items():
        if Path(name).suffix.lower() in ('.md', '.json'):
            text.extend(['## 原始檔案：' + name, '', value.decode('utf-8-sig'), ''])
    write_new(handoff, '\n'.join(text).encode('utf-8'))
    write_new(plan, json_bytes(dict(schema='kmw00-drive-upload-plan-v1', drive_status='not_saved',
                                   directories=directories, files=entries,
                                   instruction='Create folders in an authorized private destination; upload each original file as raw bytes; record returned IDs and verify readback. This plan does not upload files.')))
    return {'status': 'EXPORTED', 'zip': str(output), 'handoff': str(handoff), 'drive_plan': str(plan),
            'files': len(files), 'drive_status': 'not_saved'}


def verify_export(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(n.casefold() for n in names)):
            raise ValueError('Duplicate archive entry')
        for info in archive.infolist():
            relative_name(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('Archive symlink rejected')
        if sum(i.file_size for i in archive.infolist()) > MAX_RESTORE_BYTES:
            raise ValueError('Private export exceeds the 200 MiB restore limit')
        receipt = json.loads(archive.read('KMW00-export.json'))
        if receipt.get('schema') != SCHEMA or not isinstance(receipt.get('files'), list):
            raise ValueError('Unknown export format')
        data = {}
        for entry in receipt['files']:
            name = relative_name(entry['path'])
            if name.casefold() in {n.casefold() for n in data}:
                raise ValueError('Duplicate receipt path')
            value = archive.read('workspace/' + name)
            if len(value) != entry['size'] or digest(value) != entry['sha256']:
                raise ValueError('Export checksum mismatch: ' + name)
            data[name] = value
        if set(names) != {'KMW00-export.json', *('workspace/' + n for n in data)}:
            raise ValueError('Unlisted archive files')
    return data


def restore_workspace(archive_path, destination):
    dest = empty_destination(destination)
    data = verify_export(archive_path)
    for name, value in data.items():
        write_new(dest / name, value)
    checked_workspace(dest)
    return {'status': 'RESTORED', 'workspace': str(dest), 'files': len(data), 'drive_status': 'not_verified'}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    init.add_argument('destination')
    init.add_argument('--source-commit')
    export = commands.add_parser('export')
    export.add_argument('workspace')
    export.add_argument('output_zip')
    restore = commands.add_parser('restore')
    restore.add_argument('archive')
    restore.add_argument('destination')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            result = initialize(args.destination, args.source_commit)
        elif args.command == 'export':
            result = export_workspace(args.workspace, args.output_zip)
        else:
            result = restore_workspace(args.archive, args.destination)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
