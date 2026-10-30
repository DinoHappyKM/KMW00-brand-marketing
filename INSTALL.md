# 電腦安裝與跨端接續
使用固定版本v0.1.0-beta.4，讀VERSION並記錄實際commit。標記未發布時明說候選版，不能將main稱固定版。
下載完整套件到授權位置，先閱讀腳本、payload.sha256及TESTING.md。套件解壓外層只用來放工具，不複製成品牌內的外層。

## Windows
可直接雙擊解壓後的Start-Windows.cmd，貼上指定品牌資料夾完整路徑。請先閱讀同包腳本；這是使用者主動啟動的一般PowerShell程序。本次程序的ExecutionPolicy Bypass不改永久政策。腳本受組織限制時依管理者規則處理。

Codex命令助手正常時也可使用：
```powershell
powershell.exe -NoProfile -File .\Install-Windows.ps1 -Destination '指定私人品牌資料夾完整路徑'
```
## Mac
```sh
bash ./Install-Mac.sh '/指定私人品牌資料夾'
```
兩者安裝不要求Python，安裝腳本分開。目的地就是根目錄，直接出現00、10、20分類。
## Linux／可寫雲端工作區
```sh
bash ./Install-Linux.sh '/指定私人品牌資料夾' --source-commit '實際40字元commit'
```
此入口需Python3.10以上。手機介面不決定執行環境，Drive URL也不是本機路徑。

## 工具初始化失敗
出現setup refresh had errors且安裝器未啟動時，依[電腦故障處理](DESKTOP_TROUBLESHOOTING.md)。先做最小讀取、有界診斷及平台允許的精確核准；仍失敗則用上方原生入口。單純把G槽換成C槽工作目錄不保證排除其他已連工作資料夾，必要時以一般本機品牌資料夾單獨開新專案。不自動修改全域安全設定。

## 日常工作與手機接續
首次安裝後先讀四核心文件及導引式開案。依MOBILE.md建立跨裝置接續文件，有Python可執行readable_workspace.py prepare；無Python由代理依READABLE_STATE_TEMPLATE.md建立。
後續日常以可讀文件為準，JSON不可讀仍能接續。可讀模式用readable_workspace.py verify；原verify_project.py僅驗證完整JSON工具快照，兩者通過的意義不同。
手機與平板使用MOBILE_INSTALL_PROMPT.txt。電腦先保存本機品牌文件，只有使用者要跨端保存時才檢查Drive，沒有雲端不阻止電腦安裝與使用。

## 舊版本更新
先讀舊企劃，不重裝、不重置。不必把beta.4全包覆寫私人資料夾。
1. 新版套件下載到另一個工具目錄。
2. 對舊私人資料夾執行prepare，或依既有資料新增跨裝置接續文件；原檔保留。
3. 由代理比對新版AGENTS與跨裝置規則，只合併規則調整，保留學員自訂內容。未讀完不覆蓋。
4. 匯出可讀快照，用新空資料夾試還原，核對品牌內容與下一步。
5. 若已是可讀模式，直接續作；不要再用完整安裝器要求補回JSON。僅可讀還原不含腳本與媒體，維護時從版本套件使用工具。
6. 雲端多一層的舊企劃先列搬移對照和衝突，取得搬移範圍確認後才操作，不自動刪舊層。
雲端保存依MOBILE.md逐檔讀回。回報安裝、可讀文件、Drive保存三者各自結果，不假設背景同步。
