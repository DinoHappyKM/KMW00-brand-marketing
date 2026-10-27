# 手機、平板與跨裝置保存

## 指定資料夾就是根目錄
使用者提供的私人Google Drive資料夾URL／ID就是品牌根目錄，以「.」對應該ID。直接在它下面建立00_系統_System、10_品牌_Brand、20_行銷_Marketing等既定分類。
禁止自行加KMW00-XXX、template、workspace或KMW00-readable外層；ZIP的包裝層不是雲端安裝層。根目錄原有其他檔案也不構成另建品牌子資料夾的理由。
列齊目標內容再寫。分類已存在就沿用；同名多份或內容衝突集中列出核對，不能用新建外層或重置進度繞過。
舊版多一層時先列完整來源、目的與衝突；使用者確認搬移範圍後逐項保留ID移動並讀回。不得自行刪除舊層或覆蓋同名文件。

## 日常不依賴JSON
日常接續主檔是四個核心文件、品牌分類文件與90_專案_Project/跨裝置接續。可用Google Docs；文字保存及讀回通過即可，不要求上傳原始JSON或執行腳本。
跨裝置接續保存：企劃ID、修訂、更新時間、目前進度、已確認事項、估算與待確認、下一步、保存來源及各文件ID／連結。同一企劃ID沿用，不每次重生。
已有JSON可在首次轉換時逐欄轉成可讀文字；讀不到或格式壞掉仍可從既有文件繼續，標缺少的資料待確認。不得拿空白模板覆蓋舊企劃。
手機不必看程式欄位或自己整理JSON；代理負責整理可讀文件。後續已記錄的新決定優先於「舊開案資料逐欄轉存」，舊資料僅留作追溯。
JSON留作電腦工具快照，未重新對照可讀文件時標「可能較舊」，不能宣稱已同步，也不自動由文字猜成confirmed。

## Google Drive可讀保存
1. 先確認當次工具能列出／讀正文／建分類資料夾／建立或更新Google Docs；連接認證和相同帳號不代表這些動作都可用。
2. 在指定根目錄辨識已有分類和文件；以父ID與相對路徑建立映射，不能只靠名稱。先讀AGENTS規則、四核心文件、導引式開案與跨裝置接續；AGENTS不假設在手機自動載入。
3. 首次對一個必要文件做建立或更新、讀回正文驗證，再依分類保存其餘文件。不得反覆建測試檔或同名檔。
4. Markdown可轉成Google Docs正文；保持章節與內容，不是只改副檔名。索引記錄真實Docs連結，不能假設相對MD連結在Drive仍可點。
5. 每檔記錄相對路徑、parent ID、file ID、讀回修訂／內容及保存結果；最後更新跨裝置接續和索引。只有正文全部核對才報保存完成。部分失敗列清單，不把一個ZIP上傳當資料夾展開。
6. 更新前重新讀取遠端正文和修訂；對照本次開始讀到的版本，若有人改動，先合併或另外交付待合併稿，不直接覆蓋。不能只憑時間較新或修訂號相同就判定無衝突。
7. 跨裝置共用的雲端文件是主檔；本機是副本。每次切換先讀雲端最新版；離線有改動先比對，不能互相無條件覆蓋。這是明確讀取及保存流程，沒有背景自動同步。

## 沒有完整Drive能力仍能工作
- 可讀正文但不能寫：照常規劃，輸出更新內容或下載檔，明說尚未存入Drive。
- JSON不可讀：使用可讀文件，不要求重複認證或停止品牌分析。
- MD不可讀但可用Docs：轉存Google Docs並讀回；若無轉存能力，交付TXT讓使用者直接附加或貼入。
- 只有檔名或截斷內容：記未讀全；優先取得接續文件及本次必要文件，不假稱整個資料夾已同步。
- 只有對話：直接給可複製接續文字；不假稱安裝、產檔、Drive保存已完成。
- 大型圖片影音：放原私人儲存位置，文件保留連結；可讀快照不含原始媒體。

## 有執行工具時的可讀快照
Python 3.10以上（僅維護工具需要，手機聊天不要求安裝Python）：
```sh
python -B -X utf8 tools/readable_workspace.py prepare '/私人品牌資料夾'
python -B -X utf8 tools/readable_workspace.py verify '/私人品牌資料夾'
python -B -X utf8 tools/readable_workspace.py export '/私人品牌資料夾' '/既有交付區/本次企劃.zip'
python -B -X utf8 tools/readable_workspace.py restore '/交付區/本次企劃.zip' '/新的空品牌資料夾'
python -B -X utf8 tools/readable_workspace.py compare '/本機品牌副本' '/下載的雲端品牌副本'
```
prepare只新增缺少的接續文件，不覆蓋現有資料。export產生可讀ZIP、完整handoff.txt及drive-plan.md，不需要MANIFEST.json、開案JSON或JSON上傳清單。
restore驗證後直接還原到指定空目錄，不多一層；拒絕非空目的地。compare只比對，不寫檔，差異需人工／代理逐項核對。
可讀ZIP只含MD／TXT與文字校驗清單，保存規劃資料；不是包含圖片、程式與JSON的完整備份。完整原始備份仍可另用cloud_workspace.py（需要完整JSON），不能因此阻塞可讀模式。
若本機工具不可用，可由代理建立相同章節的可讀接續文件，企劃ID首次生成並沿用。不宣稱未執行的工具測試已通過。

## 官方說明與待驗收
2026-10-27查核：[專案來源不預先同步Drive](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)、[讀取與寫入權限](https://help.openai.com/en/articles/10929079-google-drive-app-and-setup-in-chatgpt)、[附件與連接應用限制不同](https://help.openai.com/en/articles/20001497-troubleshooting-plugins-and-apps-in-chatgpt)。
測試涵蓋跨平台工具和模擬缺檔；實際手機App、帳號可用動作及指定私人Drive往返需另驗收，不能用自動化成功代替。
