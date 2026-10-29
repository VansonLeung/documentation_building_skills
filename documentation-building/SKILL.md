---
name: documentation-building
description: 製作或修訂來源可追溯的技術報告、使用手冊及 Reveal.js 簡報，支援雙語、舊稿遷移、PDF、可選 Office 輸出與離線交付。用於持續維護的文件製作流程；一般短文改字不需啟動整套流程。
---

# 文件製作與交付

把實作、設定、評測及操作畫面整理成讀者能理解、團隊能維護的文件。操作指引使用繁中；欄位及程式參數使用英文。可以依任務產生其他語言文件。

## 先確定本次工作

沿用使用者已確認的讀者、語言、範圍、格式及授權。先讀現有文件、生成入口及適用的 AGENTS.md，再判斷是小幅修訂、資料更新，還是章節重整。只詢問會改變結果的缺項，不為已確認事項重問。

第一次使用可先完成一個代表性頁面，再擴充到完整範圍。既有文件優先沿用原技術棧、穩定章節 ID、應用 ID 及交付位置。這套技能不要求任何指定插件；若使用插件或受保護的 runtime，遵守當時有效的指引，不把本專案的舊建置命令當成通用命令。

## 按任務選擇指引

只讀當次需要的參考：

| 任務 | 指引 |
|---|---|
| 技術方法、詳細／易讀報告、提示詞附錄 | [methodology-reports.md](references/methodology-reports.md) |
| 操作手冊、新平台截圖 | [user-manuals-and-screenshots.md](references/user-manuals-and-screenshots.md) |
| Reveal.js、圖解、動畫、講者備註 | [presentations.md](references/presentations.md) |
| 簡報閱讀模式、搜尋及跳頁 | [slide-navigation-and-search.md](references/slide-navigation-and-search.md) |
| 可選圖片式 PPTX、可編輯 DOCX 及其驗證 | [office-exports.md](references/office-exports.md) |
| 從舊 PPTX／DOCX／PDF 遷移、內容及圖片去向 | [source-migration-and-reconciliation.md](references/source-migration-and-reconciliation.md) |
| 雙語章節、術語及數字同步 | [bilingual-content.md](references/bilingual-content.md) |
| 評測、來源、資料範圍與說法 | [evidence-and-evaluation.md](references/evidence-and-evaluation.md) |
| 波形、音訊、流程圖與數據圖 | [audio-and-diagrams.md](references/audio-and-diagrams.md) |
| PDF、離線、驗證、精簡工具用法 | [pdf-and-delivery.md](references/pdf-and-delivery.md) |
| 獨立 checkout、隨附簡報／Word／波形範本及執行方式 | [standalone-toolkit.md](references/standalone-toolkit.md) |
| 本海事專案的來源及生成器位置 | [maritime-project-examples.md](references/maritime-project-examples.md) |
| LD 培訓文件的 HTML-first／Office／導覽實例 | [ld-project-examples.md](references/ld-project-examples.md) |

## 共用工作方式

1. **盤點及定稿資料。** 找出目前有效的生成器、已核對資料及原始設定，明確指定主要編輯來源。教學文件可採 HTML-first，數據報告可採資料驅動；不強制另建 JSON 來源。記錄來源／版本／日期；舊 README、歷史圖解及過往成功的腳本都需與現況核對。
2. **分開證據與表達。** 同一組資料支援不同篇幅及語言；簡化文字不改分母、人口、限制或證據狀態。表格／圖表盡量由共用資料生成。
3. **製作與修訂。** 先定閱讀順序，再改內容與視覺。保留完整原始提示詞及結構契約；解說與翻譯另列。改寫應與本次範圍相稱，頁數由需求決定。
4. **從實際輸出驗證。** 檢查受影響的畫面、雙語、連結、互動與列印結果。自動檢查、人工閱讀及未執行項目分開記錄；工具通過不代表事實已核實。
5. **交付。** 以明確選檔清單打包；HTML、PDF、附件及雜湊相符。需要保留舊版時先封存，封存檔不混入日常交付包。

HTML／PDF 保留為主要交付流程，Office 按任務啟用。若需要 PPTX，預設建議圖片式以保持 HTML 外觀，清楚說明文字／圖形不能逐項編輯、動畫不保留；如任務要求原生可編輯物件，再選對應製作及驗證流程。簡報搜尋預設索引標題與可見文字，講者備註另設選項；外部版本只含已批准分享的備註。

## 需要保留的界線

- 不把推算改稱實測，不把開發樣本改稱獨立測試；沒有能力偵測不等於偵測結果為零。
- 實測、覆核、觀察、示意、待確認和規劃使用不同標示；資料日期、測試日期、文件日期分開。
- 更新文件不自動授權模型推論、訓練、提交工作、改生產資料、公開發布、安裝依賴或全域安裝技能。原有授權仍按其範圍適用。
- 不把私人憑證、服務位址、原始覆核備註或未獲准音訊帶入共享包。遮蔽名稱後也要檢查圖像、提示詞、附件及內嵌資料。
- 保留可重現證據；本機個案的連接埠、日期、樣本數、作者、色碼與檔名放在專案設定，不硬編入跨專案工具。

## 隨附工具

- `scripts/check_documentation.py`：檢查靜態 HTML 的本地連結、錨點、雙語 ID、必要文字與禁止文字；不連網、不改文件。
- `scripts/browser_documentation.mjs`：可選的本機唯讀瀏覽器檢查、截圖及 PDF 匯出；需要既有 Playwright／Chromium，不自動安裝。
- `scripts/package_documentation.py`：依明確檔案清單建立附 SHA-256 manifest 的 ZIP，驗證封裝內容；不掃整個專案打包。
- `scripts/test_tools.py`：用暫存小型雙語報告、手冊頁及簡報測試上述 Python 工具的成功與失敗情境。
- `scripts/create_presentation.mjs`、`export_presentation.mjs`：無品牌雙語 Reveal 範本及圖片式 PPTX／文字 PDF 匯出。
- `scripts/inspect_office.py`、`inspect_pdf.mjs`：唯讀結構／文字讀回，不改寫成品。
- `scripts/export_guide.py`：可選 HTML → native DOCX → PDF，需既有 Pandoc／LibreOffice。
- `scripts/waveform.py`：16-bit PCM envelope 與合成非人聲波形示例。

這些工具是起點，不取代專案已有的語意、評測或互動檢查。參數與設定範例見 PDF／交付指引。

本技能可獨立 checkout；Node 依賴由 repository 根目錄 package.json／lockfile 管理。歷史實例索引僅供選讀，不是執行前置條件。先讀獨立工具指引，按需要才安裝／啟用可選工具；保留使用者已授權的範圍。
