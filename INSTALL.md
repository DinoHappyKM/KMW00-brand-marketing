# Windows／Mac 安裝說明

先下載一份已標版本的倉庫ZIP並完整解壓；不要直接在ZIP裡執行。選擇與下載目錄分開、可持續保存的私人品牌資料夾。

## 讓Codex協助
在Codex已授權的工作資料夾貼INSTALL_PROMPT.txt。Codex先讀此說明與腳本、檢查作業系統和目的地，再執行。讀到GitHub網頁不代表安裝完成；必須有本機檔案與讀寫驗證。

## Windows
在解壓後的套件目錄使用PowerShell，將目的地替換為自己的空資料夾：

```powershell
powershell.exe -NoProfile -File .\Install-Windows.ps1 -Destination '你的品牌資料夾完整路徑'
```

若電腦政策不允許腳本，交Codex依腳本做等效複製與驗證，或由管理者處理；不要求停用安全限制。

## Mac
在解壓後的套件目錄使用終端機，將目的地替換為自己的空資料夾：

```sh
bash ./Install-Mac.sh '你的品牌資料夾完整路徑'
```

不要求雙擊腳本或安裝PowerShell；使用Mac內建bash、shasum及複製工具。Python只供維護測試，不是初始化必要條件。

## 安裝後
將安裝目的地加入Codex本機專案並設為主要資料夾；應直接看到AGENTS.md、四個核心MD及開案JSON。先請Codex讀取並建立一個測試文字檔再讀回，接著開始KMW00。不要把整部電腦或公開倉庫當成私人品牌資料夾。

安裝器遇到非空目錄會停止；已安裝則保留原資料。請另選空資料夾，不要刪掉自己的品牌資料。更新需另裝新版、備份後比對，不直接覆蓋。若網路或權限受限，列出失敗步驟，不宣稱成功。
