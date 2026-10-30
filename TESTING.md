# beta.4測試範圍

2026-10-30新增9項（6項原生Windows、3項入口及版本規則），連同既有46項共55項。Windows跳過2項Mac/Linux連結測試；Mac/Linux跳過6項原生Windows測試。實際結果看[本版CI](https://github.com/DinoHappyKM/KMW00-brand-marketing/actions)。

以本機一般程序測Windows入口，不能代替Codex受限命令助手恢復；環境setup refresh錯誤另記實測證據。原生入口仍受使用者與組織的政策限制。

本輪Windows本機54項：52成功、2平台連結測試跳過；另實際以cmd.exe啟動Start-Windows.cmd並透過輸入指定目的地，退出碼0且核心文件存在。受限Codex命令啟動錯誤可重現；替代授權程序及使用者一般本機程序可執行，不等於底層故障已消失。

## 歷史beta.3
# 測試與驗收範圍
版本：0.1.0-beta.3

## 自動化
執行 `python -B -X utf8 -m unittest discover -s tests -v`，共46個測項。
- 原26項：各平台安裝、完整備份／還原、校驗、批次提問、成本與確認狀態、拒絕覆寫與錯誤路徑。
- 新20項：無JSON工作、舊欄位逐項轉存、重複保留、JSON損壞不中斷、直接根目錄計畫、TXT全文、模擬電腦→手機副本→電腦往返、同修訂不同內容衝突、不同品牌拒絕合併、缺核心文件、身分與修訂、破損與越界ZIP、匯出不覆蓋、CLI及連結檔。
- Windows本機第二輪：44成功、2跳過（原生連結測試留Mac／Linux）。
- 第一輪發現Windows CRLF辨識問題，已正規化讀取再通過完整回歸。
- [本版CI](https://github.com/DinoHappyKM/KMW00-brand-marketing/actions)：Windows、Mac、Linux各自執行46項及封裝；只有三組成功才發布版本，不由本文件預先宣稱遠端成功。
- ZIP驗證：單根、標準斜線、UTF-8、CRC、大小寫路徑及解壓逐檔位元組一致。

## 成功的意義
可讀驗證只檢查必備文件、接續欄位及檔案完整性，不替代品牌事實、成本來源或使用者確認。
舊JSON驗證仍嚴格，供完整工具快照使用；無JSON可讀模式使用readable_workspace.py，不冒充已通過舊語意檢查。
模擬手機副本是在測試目錄內修改可讀文件，不是真實手機App或Google Docs轉換。

## 尚待實機
未取得使用者手機對話的實際工具與指定私人Drive目標，因此沒有替使用者移動現有資料夾，也沒有宣稱手機Drive保存已驗收。
需要在學員帳號驗證：直接根目錄、Google Docs正文建立／讀回、手機新對話接續、電腦取回新版、遠端衝突處理、權限不足降級。確認只有檔名／截斷或無寫入時能如實回報。
不可把GitHub Actions成功說成ChatGPT外掛上架、手機雲端存檔或背景自動同步。


發行首輪測試三平台成功，但VERSION帶CR造成gh資產路徑錯誤；版本檔改LF並在發行讀取時去除CR/LF，加入跨平台版本回歸。最終以新版CI結果為準。
