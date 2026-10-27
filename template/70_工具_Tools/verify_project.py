#!/usr/bin/env python3
"""KMW00 schema and workflow checks. Does not prove a live platform or business outcome."""
from pathlib import Path
import json,sys

def verify(root):
    root=Path(root); errors=[]
    try:
        manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8-sig'))
        p=json.loads((root/'90_專案_Project/開案資料_ProjectProfile.json').read_text(encoding='utf-8-sig'))
    except (OSError,ValueError) as e:
        return ['無法讀取必要JSON：'+str(e)]
    for rel in manifest['required_files']:
        path=(root/rel).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():errors.append('必要檔案缺失或路徑錯誤：'+rel)
    if p.get('template_version')!=manifest['template_id']:errors.append('模板版本識別不一致')
    if not p.get('current_step') or not p.get('current_question'):errors.append('缺少接續位置')
    if p.get('intake_mode')!='batch':errors.append('本版須批次提問')
    sections=['brand','sales_model','offer_333','brand_ci','customer_data']
    allowed={'not_started','draft','estimated','confirmed'}
    for key in sections:
        if p.get(key,{}).get('status') not in allowed:errors.append('未知階段狀態：'+key)
    sales=p.get('sales_model',{})
    primary=sales.get('primary_type','');secondary=sales.get('secondary_type','')
    if primary not in ['',*'ABCDEFG'] or secondary not in ['',*'ABCDEFG']:errors.append('成交型須A～G或未定')
    if primary and primary==secondary:errors.append('主輔型不得相同')
    if sales.get('status')=='confirmed' and not primary:errors.append('確認成交型不能空白')
    if p.get('brand',{}).get('status')=='confirmed':
        for key in ['name','industry','target_audience']:
            if not str(p['brand'].get(key,'')).strip():errors.append('品牌確認缺必要欄位：'+key)
        if not p['brand'].get('services_or_products'):errors.append('品牌確認缺商品服務')
    if p.get('project_mode')!='generic_only':errors.append('本版僅generic_only')
    industry=p.get('industry',{})
    if industry.get('module_status') not in ['generic_only','not_installed']:errors.append('本版不支援此模組狀態')
    if industry.get('module_id') or industry.get('skill_id'):errors.append('本版不應宣告已安裝產業模組或Skill')
    for item in p.get('assumptions',[]):
        if not isinstance(item,dict):errors.append('假設須為物件');continue
        for key in ['item','value','basis','source','date','region','confidence','status']:
            if key not in item or item[key] in ['',None]:errors.append('假設缺欄位：'+key)
        if item.get('status')!='estimated':errors.append('假設不得冒充confirmed')
    build=p.get('system_build',{})
    if build.get('status') not in allowed:errors.append('未知建置狀態')
    if any(p.get(k,{}).get('status')=='confirmed' for k in sections) and not p.get('confirmed_decisions'):errors.append('缺少使用者確認紀錄')
    if build.get('status')=='confirmed':
        if not all(p.get(k,{}).get('status')=='confirmed' for k in sections):errors.append('前置五區尚未確認')
        if not build.get('test_evidence'):errors.append('缺少實際建置測試證據')
    for path in root.rglob('*.json'):
        try:json.loads(path.read_text(encoding='utf-8-sig'))
        except (OSError,ValueError):errors.append('JSON格式錯誤：'+str(path.relative_to(root)))
    return errors
if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    errors=verify(root)
    print('\n'.join('ERROR: '+e for e in errors) if errors else 'PASS: KMW00檔案與狀態檢查；不代表實際上線')
    sys.exit(bool(errors))