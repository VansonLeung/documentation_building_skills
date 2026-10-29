# 文件製作技能包

獨立使用的 Codex 技能、雙語範本及小型工具。入口為 [SKILL.md](documentation-building/SKILL.md)，操作方式見 [獨立工具指引](documentation-building/references/standalone-toolkit.md)。不需要海事或 LD 專案的原始目錄。

Python 基本檢查／打包只用標準函式庫。簡報、瀏覽器及 PDF 檢查使用本 repository 的 Node.js 依賴；Word 輸出另外需要已安裝的 Pandoc，DOCX-derived PDF 需要 LibreOffice。

```sh
# 從本 repository 根目錄執行；Node.js 22+、Python 3.10+
npm ci --ignore-scripts
# 尚未安裝 Chromium 時，明確執行以下步驟：
npx playwright install chromium

npm run create:presentation -- --output /tmp/my-presentation
npm run export:presentation -- \
  --input /tmp/my-presentation/deck.zh-Hant.html --output /tmp/my-presentation-export
npm test
```

`--output` 使用新的資料夾，不覆蓋既有交付。產生的 HTML 可直接離線開啟；PDF／PPTX 可獨立交付。圖片式 PPTX 不包含可逐項修改的文字／圖形，也不保留動畫；備註預設不匯出，可明確選 `--notes approved`。

範本均使用構造教學內容，不包含客戶資料或實測數字。不要把這些例子當成模型能力證據。DOCX、波形、驗證及依賴說明見獨立工具指引；抽離來源見 [provenance.json](provenance.json)。

2026-10-29 的隔離執行、輸出及驗證範圍記錄於 [validation.json](validation.json)。這次沒有以 Microsoft PowerPoint／Word／Keynote 開啟生成檔，不能把封裝及讀回檢查當成桌面 Office 匯入測試。
