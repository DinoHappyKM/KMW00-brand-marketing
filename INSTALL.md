# Windows／Mac／Linux 安裝說明

先解析指定標記 v0.1.0-beta.2 對應的實際 commit，下載完整套件 ZIP 並解壓。標記尚未存在時才使用 main 的實際 commit，讀 VERSION 並記錄，不能稱為固定標記版本。下載與所有寫入只在使用者授權的工作區或暫存區。

先讀 README.md、TESTING.md、適用腳本及 payload.sha256，再選與套件分開的私人品牌資料夾。不要因手機回報 Linux 就判定無法安裝；先確認是否可建立檔案並讀回。Google Drive URL 不是本機路徑，也不會自動掛載為檔案系統。

## Windows（不要求 Python）
```powershell
powershell.exe -NoProfile -File .\Install-Windows.ps1 -Destination '已授權的品牌資料夾完整路徑'
```
電腦政策不允許腳本時，依腳本做等效複製與驗證或由管理者處理，不要求停用安全限制。

## Mac（不要求 Python）
```sh
bash ./Install-Mac.sh '/已授權的私人品牌資料夾'
```
使用內建 bash、shasum 及複製工具，不要求安裝 PowerShell。

## Linux／雲端工作區（Python 3.10 以上）
```sh
bash ./Install-Linux.sh '/已授權工作區/品牌資料夾' --source-commit '實際40字元commit'
```
也可由代理使用 `python3 -B tools/cloud_workspace.py init ...`。工具核對全部 payload、拒絕連結與非空衝突、逐檔寫入讀回並保留已安裝進度。缺 Python 時如實說明，可依完整校驗清單等效複製及驗證，不因缺少一個入口就重置資料。

Linux 初始化成功只代表目前執行工作區可用，不代表已存進 Google Drive 或手機儲存空間。繼續依 [MOBILE.md](MOBILE.md) 做 Drive 驗證或匯出交付；不要假設執行工作區永久保存。

## 安裝後共同驗收
回報來源 commit、版本、實際工作區路徑；確認 AGENTS.md、四個核心 MD、開案 JSON 存在，做一個小檔寫入讀回。可執行 `python -B -X utf8 template/70_工具_Tools/verify_project.py '品牌資料夾'`。

本機目的地若是新增子資料夾，提醒使用者加入 Codex 並設為主要資料夾。雲端／手機則回報實際交付檔案與 Drive 驗證狀態，不套用本機主要資料夾步驟，也不宣稱 AGENTS 已自動載入；由對話明確讀取。

## 既有資料與接續
非空目的地不覆蓋；已安裝則讀取既有進度。更新需另裝新版範本、備份後比對，不整包覆寫。舊版私人工作區也可使用本套件的匯出工具，原 package_version 不會被修改。保留原始套件或依記錄的版本重新下載到暫存區，才有 tools/cloud_workspace.py 可用。
