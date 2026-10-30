# 電腦安裝與本機工具故障

## 先判斷在哪裡失敗
- 出現CreateProcess／helper_unknown_error／setup refresh had errors，且未取得安裝器退出碼：屬Codex命令啟動失敗，不代表KMW00腳本已執行。
- 腳本已啟動，回報來源校驗失敗／目的地非空／不允許連結：按該具體錯誤處理。保留檔案，不無條件覆寫。
- GitHub能讀但命令不能執行：代表網頁讀取正常，本機安裝尚未完成。換GitHub倉庫不能改變本機工具能力。
2026-10-30本機重現：一般命令在程序啟動前失敗；替代的授權程序可執行。當日日誌含G槽權限設定SetSecurityInfo failed: 87。本次證據不證明每位學員相同錯誤都來自同一個路徑。

## Codex代理的有界恢復
1. 先讀取目前已授權品牌資料夾；Windows使用NoProfile／不載入登入設定。最小讀取失敗時，只再做一次簡短診斷，記錄原錯誤。
2. 若是上述程序初始化錯誤，不將它當成沒有工具或安裝器錯誤；由平台允許的方式，申請只針對該品牌路徑及已閱讀安裝器的執行核准。是否可用由當次政策決定；既有授權不等於平台核准已取得。
3. 不自動修改Codex全域設定、Windows ACL或安全政策，也不要求開啟全域完整存取。替代操作遭拒就保留狀態，不換殼規避。
4. 仍無法啟動時提供下方本機安裝方式；或請使用者用一般本機品牌資料夾另開專案，只連該品牌資料夾。已連接的其他G槽資料夾也可能參與初始化；只改工作目錄不保證解決。
5. 不反覆重試、不要求換倉庫。明確回報未安裝，繼續可做的規劃。

## Windows直接安裝
1. 從固定發行頁下載完整ZIP並解壓到一般本機位置。
2. 閱讀Install-Windows.ps1、Install-Windows-Interactive.ps1和payload.sha256。
3. 雙擊Start-Windows.cmd，貼上私人品牌資料夾的完整路徑。這是使用者主動啟動的一般PowerShell程序，不依賴Codex命令助手。
4. 顯示VERIFIED後，在Codex單獨開啟該品牌資料夾，先讀AGENTS.md及四個核心文件，再開始KMW00。
此入口只對本次PowerShell程序使用ExecutionPolicy Bypass，不更改電腦永久政策、不要求管理員。只執行你信任的老師套件；若組織政策阻擋，交由管理者處理。
舊企劃偵測到既有安裝就保留；這個入口不會升級、不會重置。需升級時依INSTALL.md合併指定規則。
雲端硬碟若不支援目前Codex的權限設定，可先用一般本機工作資料夾，之後依需求保存到雲端。不要把Google Drive捷徑當成一般本機檔案。

## Mac
依INSTALL.md使用bash Install-Mac.sh安裝到指定品牌資料夾。若Codex命令工具本身不可用，也可由使用者在終端機執行同一支已閱讀腳本；不必另建倉庫。

## 官方參考
[Windows權限與故障診斷](https://learn.chatgpt.com/docs/windows/windows-sandbox)、
[Codex卡住時先測基本命令與新對話](https://learn.chatgpt.com/docs/reference/troubleshooting)。
官網沒有針對本次SetSecurityInfo:87提供確定修復保證；本套件只提供診斷與安裝替代方式，不能修復Codex底層程序。
