# PDF、驗證與交付工具

## 建置與輸出

沿用專案已驗證的 renderer 和 exporter。一般流程是共用資料 → HTML／網站 → PDF → 最終 HTML 內嵌下載（如需要）→ 再建置 → 核對下載檔與交付檔 → 打包。不要讓內嵌 PDF 包含自己而形成無限循環。

主要來源也可直接是 maintained HTML，無需為每個教學文件另建 JSON。若需要 Word／PDF 分頁相符，採 HTML → DOCX → PDF；圖片式 PPTX 則與可選取文字的 PDF 分別由同一 HTML export view 生成。Office 詳見 [office-exports.md](office-exports.md)。

工具不可用時，先說明具體缺項及既有授權，再選可行替代。不要默默安裝依賴、改產品 runtime 或為普通文案變更切換整套技術棧。若選定的插件另有流程要求，依當時有效規範執行。

## PDF 重點

- 封面、頁碼、目錄、分組書籤、中文可搜尋／複製；字型載入完成後才列印。
- 長表可跨頁並重複表頭，避免把整個長區塊設為不可分頁而產生大量空白。
- 查裁切、孤立標題、空白／只有頁尾的頁面、圖例與註腳；用 contact sheets 全冊掃視，再放大問題頁。
- 媒體控制在列印時隱藏，但完整波形、文字、樣本檔名和連結保留。
- 對本機絕對連結做可攜處理；PDF reader 未必支援相對 URI，因此保留同資料夾聆聽頁作備援。
- 本海事專案曾遇 PDFKit 重寫後破壞中文 ToUnicode。避免為改連結重新序列化整份 PDF；優先在來源修正再匯出。特殊位元組修補只有在格式、長度、xref 及讀回驗證均明確時才採用，不把個案修補器當成一般 PDF 工具。

通用工具不提供完整 PDF 解析器。優先使用既有本機 PDF 工具檢查文字、頁數、outline 和 annotations，並做人工視覺檢查。未執行者列為未檢查。

## 工具設定

下列 JSON 是可複製的示例；檔名、日期、必要字串改為本次任務設定。工具檔案位於技能的 `scripts/`。Python 工具只用標準函式庫，執行 Python 3.10+。

```json
{
  "metadata": {
    "title": "Example methodology",
    "document_date": "2026-10-29",
    "author": "Author supplied by user"
  },
  "files": ["report.html", "report.zh-Hant.html", "figure.svg", "report.pdf"],
  "bilingual": [
    {"left": "report.html", "right": "report.zh-Hant.html", "anchors": ["method", "results"]}
  ],
  "required_text": {"report.html": ["Illustrative"], "report.zh-Hant.html": ["示意"]},
  "forbidden_text": ["REPLACE_WITH_AN_ACTUAL_PRIVATE_VALUE_IF_NEEDED"],
  "require_packaged_links": true
}
```

`files` 必須是逐檔清單，不接受 glob。`bilingual` 如不設 `anchors`，則比對兩份靜態 HTML 的全部 IDs；有些 runtime 會產生不同 IDs，宜只設定真正的章節 IDs。HTML `<base>` 會影響 URL 語意，本工具明確拒絕，交由專案測試。網站 `/path` 以 `--root` 為站台根；靜態離線交付宜改相對路徑。

```sh
python3 <skill>/scripts/check_documentation.py \
  --root <delivery-folder> --config <task-config.json>

python3 <skill>/scripts/package_documentation.py \
  --root <delivery-folder> --config <task-config.json> \
  --output <new-handover.zip>

python3 <skill>/scripts/test_tools.py
```

兩個工具成功回傳 0，失敗回傳 1，結果以 JSON 寫到 stdout。檢查器唯讀；打包器產生新的 ZIP，不覆蓋既有檔。ZIP 內 `manifest.json` 記錄明確選取檔案的 bytes／SHA-256；manifest 本身不列自己的雜湊，ZIP 雜湊寫在執行結果。

路徑穿越／symlink、重複選檔、缺檔會拒絕。打包器亦拒絕常見憑證檔及 `.git`／`node_modules` 等；這不是完整個資檢測器，實際內容和音訊分享資格仍需核對。

檢查器不執行 JS，也不擷取外部連結。CSS imports、srcset、生成式 DOM、PDF、媒體品質及翻譯意思不在它的通過範圍內。`forbidden_text` 只掃選取的 UTF-8 文字，不解 base64、壓縮內容或二進位文件。

## 可選瀏覽器工具

需要 Node.js、Playwright 及 Chromium；正常使用根目錄 package.json／lockfile 安裝本 repository 的依賴，不需要原海事專案。工具不會自行安裝或啟動平台。`--playwright-from` 是進階選項，可指向另一個已能解析 Playwright 的目錄；具體環境見 [standalone-toolkit.md](standalone-toolkit.md)。

```sh
node <skill>/scripts/browser_documentation.mjs \
  --url http://127.0.0.1:<port>/report.html \
  --output <new-validation-folder> \
  --ready '#method' --pdf true
```

`--chromium <executable>` 可指定既有 Chromium。工具檢查 desktop／mobile 頁面 overflow、img 載入、JS／HTTP 錯誤、非預期自動播放；擷取截圖，可選擇匯出 A4 PDF。輸出目錄必須不存在，避免混用過期結果。

只接受 loopback HTTP，同源 GET/HEAD，阻擋其他網路請求、service workers 及 websocket；不點控制項。這不證明伺服器沒有 GET 副作用，也不取代 file:// 離線、互動、讀完 loading、canvas 圖表、PDF 字元及視覺檢查。動態頁面應提供真正的 ready selector；需要更多狀態時擴充專案測試。

阻擋請求會列在結果且令檢查失敗，不默默忽略 CDN 依賴。回報中可能含網址，對外分享前先核對；驗證資料預設留內部。

可重跑的隔離瀏覽器測試（不連平台、不安裝依賴）：

```sh
python3 <skill>/scripts/test_browser.py --output <new-test-folder>
```

它產生雙語報告、手冊與靜態簡報樣本，測試截圖／PDF 成功，以及 overflow 和 POST 被拒絕的失敗情境。這不是完整 Reveal runtime 或生產平台測試；輸出目錄可供人工檢視。

## 交付前核對

區分兩種雜湊用途：**source fingerprint** 比對輸入是否改變，判斷匯出是否過期；**output manifest** 識別成品 bytes 是否一致。前者可按實際影響鏈包含文字、圖片、CSS、exporter、範本、runtime／lockfile 及工具版本。若只涵蓋選定部分檔案，要照實標示，不宣稱完整可重現。現有 `package_documentation.py` 只做後者，不會自行重建來源依賴圖。

圖片式 PPTX 中的文字不可逐項編輯；DOCX 中的圖片也不會變成 native text。交付說明應逐格式列明限制。需要測試修改能否進入多格式成品時，在暫存副本做一次文字／樣式 smoke edit，不覆寫日常編輯來源。

對外 ZIP 只選必要的 HTML、PDF、已核准附件、媒體、授權及 START_HERE 類閱讀指引；不把資料庫、模型、node_modules、原始備註或封存歷史一起打包。雜湊只能證明一致性，不能證明內容正確。

記錄自動檢查、人工視覺檢查及未完成項目。不要將單一 `passed` 當成所有層面的品質聲明。原有報告框架的 buildStatus／身份／保護規則，沿用其當前指引。
