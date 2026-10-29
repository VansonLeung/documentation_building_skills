# LD 培訓文件實例索引

檢視日期：**2026-10-29**。以下位置相對於另一個 LD 專案 checkout：

```text
<LD_PROJECT_ROOT>/docs/20260923/
```

這是可選的歷史實例索引，不是技能的必要依賴。原始文件、客戶截圖及範本留在原處。簡報控制／匯出／Office 檢查的通用邏輯已抽離至技能，來源紀錄見根目錄 provenance.json；獨立執行方式見 [standalone-toolkit.md](standalone-toolkit.md)。

## 入口及內容來源

| 位置 | 用途及可借用方法 |
|---|---|
| `index.html` | 一般使用者／技術人員／手冊入口及下載分流 |
| `user-training.html` | 55 張使用者培訓，HTML 為日常編輯來源 |
| `technical-training.html` | 88 張技術培訓，案例與附錄分段 |
| `user-guide.html` | 原生段落與表格，供 DOCX 及其 PDF 轉換 |
| `styles/theme.css`、`slides.css`、`guide.css` | 共用視覺 tokens、截圖與 callout 版型、固定畫布 |
| `README.md`、`RECONCILIATION.md`、`VALIDATION.md` | 操作方式、來源決策及歷史交付檢查 |

JSON manifests 是遷移／輸出紀錄，並非該例教學文字的編輯來源。HTML-first 與海事報告的資料驅動方式可並存；不要為統一技能而重寫它。

## 工程實例

| 腳本／資源 | 參考重點 |
|---|---|
| `scripts/slides.js` | reading／presentation 切換、返回該頁、圖片尺寸、穩定 ID |
| `scripts/slide-search.js`、`.mjs`、`.test.mjs` | 本機全文、prefix／typo search、dialog、快捷鍵；原版包括 notes |
| `scripts/navigation-check.mjs` | Chromium／WebKit、HTTP／file:// 導覽測試 |
| `scripts/export-slides.mjs` | 元素截圖 → 滿版圖片 PPTX＋notes；另以相同 screen layout 匯出文字可選取 PDF |
| `scripts/export-guide.mjs`、`style-guide.py` | HTML → Pandoc／reference DOCX → LibreOffice PDF，獨立暫存 profile |
| `templates/` | untouched source DOCX 與 export reference styles 分開 |
| `scripts/import-sources.py` | 一次性導入；`--overwrite` 不用於日常維護 |
| `manifests/source-map.json`、`image-coverage.json` | source destinations、圖片 hashes／placements／crop |
| `scripts/fingerprint.mjs`、`manifests/export-*.json` | 當前選定輸入與上次輸出時的來源 fingerprint 比較 |
| `scripts/validate.mjs`、`inspect-office.py` | layout、頁數、notes、ZIP／XML、PDF selectable titles 及 DOCX native text |
| `scripts/smoke-edit.mjs` | 暫存文字／樣式修改是否進入輸出 |

依賴及執行命令以該專案當前 package.json 為準。技能不自動跑其 postinstall、導入、匯出或會寫入 build／exports／manifests 的驗證腳本。

## 已檢視與未重新驗證

本次讀取來源、腳本及既有 validation records，並唯讀開啟兩套實際 HTML，抽查使用者第 5 張及技術第 40 張、閱讀模式返回原頁、搜尋 dialog 與結果；無觀察到 JS error。截圖僅存暫存目錄，沒有修改來源。

三份選定來源 fingerprint 與既有 export manifests 相符；這只是已列入依賴的來源一致，不是完整 build environment 或成品 hashes 驗證。本次沒有重建、全面逐頁檢查或重新在 Office 軟件開啟檔案。

歷史 VALIDATION.md 記錄 Keynote／LibreOffice 檢查，並明確說明未用 Microsoft PowerPoint／Word；不得把該紀錄提升成這次重新執行的檢查。

## 抽離時需要調整

- 搜尋原版包括 speaker notes；新技能預設只搜尋 visible text，對外版本需先移除私人 notes。
- 原版 Unicode word matching 對中文中間詞不足：構造標題「如何辨識對話交錯」搜尋「對話」得到零個結果。這是跨語言適配測試，非原英文 deck 的既有缺陷。
- PPTX 為 full-slide images，不能逐項改字；notes 的可編輯程度不能代替內容可編輯承諾。
- 固定 1280×720 畫布及 2560×1440 截圖為該專案設定，不必套在所有文件；手機閱讀需另驗證。
- 專用 `?export` view 不等於 Reveal generic print，應沿用已驗證的輸出排版。
- 移植時擴充依賴紀錄：目前 fingerprint 為選定檔案集合，未涵蓋全部 runtime／lockfile／瀏覽器與轉換器版本。新流程可按需要記錄完整影響鏈，不能將現有 digest 稱為完整重現證明。
- 這裡的靜態 slides 和海事簡報的 fragments 都是可選模式；不把一方當成另一方的必要替換。

通用方法見 [office-exports.md](office-exports.md)、[slide-navigation-and-search.md](slide-navigation-and-search.md) 及 [source-migration-and-reconciliation.md](source-migration-and-reconciliation.md)。
