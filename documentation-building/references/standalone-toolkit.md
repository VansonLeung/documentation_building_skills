# 獨立工具與範本

本技能 repository 可以放在任意路徑。以下命令從 repository 根目錄執行；`<new-folder>` 應替換成不存在的輸出資料夾。不依賴歷史實例的原目錄，也不需全域安裝技能。

## 依賴與安裝

- Python 3.10+：靜態檢查、ZIP 打包、Office XML 檢查及 PCM 波形均用標準函式庫。
- Node.js 22+：以根目錄 package.json／package-lock.json 管理 Playwright、Reveal、PptxGenJS、PDF.js。
- Chromium：使用 Playwright 已安裝的瀏覽器；一般 browser checker 可用 `--chromium` 指定其他既有版本。
- Pandoc：可選 HTML → DOCX。
- LibreOffice `soffice`：可選 DOCX → PDF；不是從 HTML 另印一份 PDF。

```sh
npm ci --ignore-scripts
# 僅在需要而本機沒有瀏覽器時執行：
npx playwright install chromium
```

沒有 postinstall，也不會自動連接原專案、模型或生產資料。首次安裝可能需要網路；「離線」指安裝完畢後的 HTML 閱讀、搜尋及本機匯出，不宣稱無套件快取亦可離線首次安裝。

## 建立及編輯簡報

```sh
node documentation-building/scripts/create_presentation.mjs --output <new-presentation-folder>
```

輸出包含 `deck.html`、`deck.zh-Hant.html`、樣式、搜尋／導覽程式及 Reveal runtime／授權檔。直接開 HTML，或用靜態本機伺服器預覽。修改 HTML 作主要內容來源；每張保留唯一 ID，雙語對應相同 ID。

本機範本位於 [assets/presentation](../assets/presentation)。使用 1280×720 畫布、局部手動 fragments、閱讀模式及手機閱讀版。搜尋預設不索引備註，可選 approved notes；未提供未經批准的備註顯示功能。靜態預覽不需要正在運行的應用或 API。

講者備註用 `.notes[data-share="approved"]` 明確標示。把私密備註放在 HTML 中仍代表讀者可讀取來源；對外交付 HTML 前要移除私人備註，不能只靠 checkbox／CSS。

## PPTX 與 PDF

```sh
node documentation-building/scripts/export_presentation.mjs \
  --input <presentation-folder>/deck.html --output <new-export-folder>

# 如要包含已批准備註：
node documentation-building/scripts/export_presentation.mjs \
  --input <presentation-folder>/deck.zh-Hant.html --output <another-new-folder> \
  --notes approved --author "Author supplied by user"
```

只適用於此範本或實作相同 `documentationReady`／`section.slide`／export view 契約的 HTML，不是任意網站轉換器。所有 slides 必須有相同固定尺寸、穩定 ID 及標題。匯出會檢查主要內容區的 overflow，並拒絕非本機來源／變更請求。

輸出 `presentation.pptx`、`presentation.pdf`、每張 PNG、`contact-sheet.html` 及 `export-manifest.json`。PPTX 使用滿版圖片及可選 approved notes；PDF 從 HTML 另外生成，保留正文文字。PDF／PNG 顯示全部 fragments；不把搜尋及閱讀控制印出。看 contact sheet 後放大重要頁，不以自動 overflow 通過取代人工閱讀。

manifest 記錄本次實際載入的來源 hashes、exporter hashes、Node／Chromium 版本及輸出 hashes。這不是完整依賴圖；package-lock／provenance 分別保留套件及抽離版本。來源 PNG 和 manifest 可能是內部驗證資料，交付時按需要選檔。

exporter 不會修改或匿名化原 HTML，也不把它複製到交付目錄。沒有備註時可正常匯出。失敗輸出資料夾保留 `passed: false` 的 manifest 供排查；重試使用新資料夾。

## Office 與 PDF 讀回

```sh
python3 documentation-building/scripts/inspect_office.py <file.pptx>
python3 documentation-building/scripts/inspect_office.py <file.docx>
node documentation-building/scripts/inspect_pdf.mjs --input <file.pdf>
```

Office inspector 按 relationships 讀取 slide／notes，不假定 notes 從 1 連續編號。預設只輸出結構及字元數；明確加 `--include-text` 才輸出正文／備註。PDF inspector 唯讀、不重新序列化；`--include-text true` 會輸出每頁文字。

PDF `--config expectations.json` 支援 `expected_pages`、`required_text`、`require_outline` 和 `min_chars_per_page`。按文件設定，不把合法短封面套成固定錯誤門檻。這些工具沒有驗證桌面 Office 匯入、完整視覺品質或語意正確。

## 可選 Word 手冊

乾淨雙語範本位於 [assets/guide](../assets/guide)，可複製後直接編輯 HTML：

```sh
python3 documentation-building/scripts/export_guide.py \
  --input documentation-building/assets/guide/guide.zh-Hant.html \
  --output <new-guide-export> --pdf
```

`--pdf` 可省略；`--reference <clean-reference.docx>` 可提供自己的樣式範本。未提供時從本機 Pandoc 取得乾淨 default reference，不使用原客戶頁首頁尾。`--pandoc`／`--soffice` 可指定可執行檔。LibreOffice 使用獨立暫存 profile。

輸入應是已整理的 HTML 正文，不是帶控制介面的整個網站。工具不執行 JavaScript，不自動重建任意網站的 TOC，也不處理客戶專用 Word 欄位；需要時在維護來源中明確整理。記錄 native text／table、工具版本及 hashes，PDF 由同一 DOCX 生成。沒有內含原生可編輯 PPTX 工具。

此簡單 exporter 使用正文的標題作可見標題，抑制 Pandoc 從 HTML `<title>` 另加重複 title block；有自訂封面需要時，在正文或專用生成器中明確建立。

## 波形範例

```sh
python3 documentation-building/scripts/waveform.py --example --output <new-waveform-example>
python3 documentation-building/scripts/waveform.py \
  --input <approved-audio.wav> --output <new-waveform-output> --channel 0
```

`--example` 生成四秒靜音／合成音調，不是人聲、TTS、VAD 或 ASR 測試。工具支援 uncompressed 16-bit PCM WAV，以固定 full-scale 振幅畫 min/max envelope；記錄實際 duration、channel、source hash 及 bins。輸入模式只輸出 SVG／JSON，不自行複製原音訊到交付目錄。

## 測試與隔離驗收

```sh
PYTHONDONTWRITEBYTECODE=1 npm test
python3 documentation-building/scripts/test_browser.py
# 已具備 Pandoc／LibreOffice 時：
npm run test:guide
```

`npm test` 包含 Python 邏輯、搜尋，以及真正 Reveal 的 HTTP／file:// 雙語導覽、手機閱讀、備註篩選、fragment 前進／後退、三組 PPTX／PDF、來源文字修改後重新匯出及 hashes。輸出留在暫存資料夾；`DOC_TEST_OUTPUT=<new-directory>` 可保留到指定位置。它不是實際桌面 Office 匯入測試。

`npm run check` 先唯讀檢查本包程式／範本的 provenance hashes、文件連結及依賴 lock 一致性，不讀取原海事／LD 檔案。編輯工具後需重新檢視變更及更新 provenance.json 的本地 file hash；保留 original source hash 作來源紀錄，不能把它改成衍生檔的 hash。

PDF 必要文字比較採 NFKC 與移除空白：某些中文字型會輸出 Unicode 相容部首。工具不修改 PDF 或原始抽取文字，也不以這項比較取代實際閱讀器的搜尋／複製及字型外觀檢查。

`test_browser.py` 是既有靜態範例的六個情境，可自行解析 repository 的 Playwright。`--playwright-from` 只作進階依賴覆寫，不是正常執行的必要條件。

獨立驗收應使用只含本 repository 的暫存 checkout／副本，在其內 `npm ci --ignore-scripts` 並執行工具；不得從原海事／LD 目錄借用程式或 node_modules。標準系統工具、已安裝的瀏覽器及系統字型仍屬環境依賴。Word 輸出需另用本機 converters 檢查，工具不自動安裝。

2026-10-29 已完成上述隔離副本驗收；結果、環境及未覆蓋範圍見根目錄 [validation.json](../../validation.json)。首次技能包記錄中曾缺 PyYAML；後續已在獨立暫存 Python 環境執行 Skill Creator 標準驗證並通過，沒有將 PyYAML 變成本技能的 runtime 依賴。
