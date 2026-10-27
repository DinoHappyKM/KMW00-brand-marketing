# 測試範圍

本版用15項自動化案例驗證：來源模板、分類與狀態錯誤、前置關卡、壞JSON、缺檔、品牌署名、成本假設、批次提問文件，以及原生安裝／重複保留／衝突停止／來源改動拒絕／大小寫路徑。

[查看Windows與Mac自動化結果](https://github.com/DinoHappyKM/KMW00-brand-marketing/actions)

公開預發行ZIP只在Windows與macOS兩組測試成功後建立。雲端Mac測試不代表真實學員Mac、Codex原生發現或手機操作驗收。

## 仍需人工試用
- Windows／Mac學員在Codex依提示詞實際下載、安裝、加入專案、寫入讀回。
- 新對話接續、手機平板私人企劃匯出入、外掛安裝。
- 真實品牌的成交分類、產業參考品質、價格與履約確認。
- 產業模組安裝／更新不在本版功能內。

程式PASS只代表列出的測項，不代表品牌上線或實際成交效果。維護者可用Python3.10以上執行python -B -X utf8 -m unittest discover -s tests -v；初始化本身不需Python。