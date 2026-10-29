# 海事專案實例索引

以下路徑相對於**原海事專案 checkout 根目錄**，不是本獨立技能 repository；本索引檢視日期為 **2026-10-29**。它們是可選的歷史實例，單獨 checkout 本技能時不預期存在。報告、真實音訊及資料庫留在原處。

可執行的獨立工具與合成範本見 [standalone-toolkit.md](standalone-toolkit.md)，不需要原海事目錄。

先定位 `codes/v18/maritime_vhf_navigator/codes/v1/test-results/`，下稱 `T`。

| 實例 | 位置 | 可參考內容 |
|---|---|---|
| 完整詳細方法報告 | `T/2026-10-22-methodology-report/` | 雙語長冊、完整提示／schema、分組書籤及來源 |
| 易讀主報告／技術附錄／簡報 | `T/2026-10-26-methodology-model-evaluation/` | 分層閱讀、Reveal、例子、手動動畫、合成音軌 |
| 結果報告 | `T/2026-10-18-evaluation-results/full-ai-generated-report/` | 圖表、頻道配色、計數與時間單位解說 |
| 使用手冊 | `codes/v3/poc_mp3_preprocessors/docs/20260929/documentations/` | VitePress、雙語導航、現行平台截圖與 PDF |

## 詳細版入口

在 `2026-10-22-methodology-report/`：

- `START_HERE.txt`、`manifest.json`：先看版本、範圍及實際交付內容。
- `scripts/enhance-detailed.py`：本次重整入口，保留原始證據並組合新版。依賴既有封存資料，不適合作通用 starter。
- `scripts/compose-report.py`：目前轉接上述流程；不要從檔名猜它仍是舊版生成器。
- `scripts/verify-evidence.py`：來源、設定、提示及評測記錄核對。
- `scripts/check-and-export.mjs`、`check-offline.mjs`、`check-detail-media.mjs`：渲染、精確 PDF 下載、離線及播放檢查。
- `scripts/inspect-pdfs.swift`：PDFKit 唯讀檢查及 contact sheets；不重新寫 PDF。
- `scripts/portable-pdf-links.py`：只適用該版特定 URI 的位元組修補，不整批搬成通用工具。
- `scripts/package-detailed.py`：該報告的交付 allowlist／驗證約束。

## 易讀版與簡報入口

在 `2026-10-26-methodology-model-evaluation/`：

- `scripts/sync-methodology.py`：當前報告內容同步；歷史 compose 腳本不應直接覆蓋現版。
- `scripts/build-meeting.py`、`meeting-diagrams.py`：雙語 slides、章節及 SVG。
- `scripts/wave-track.py`、`meeting-audio.py`：構造音軌和已核准合成樣本，示意不宣稱實際跑過 VAD／ASR。
- `scripts/check-meeting.mjs`：前進／倒退 fragment、Show all、動畫切換、reduced motion、語言、print 及輸出。
- `scripts/check-listening.mjs`、`check-reader-media.mjs`：離線媒體、來源及播放器。
- `scripts/export-reader.mjs`、`inspect-reader.swift`、`verify-reader.py`、`package-reader.py`：報告輸出與來源驗證。

`scripts/README.txt` 保留部分歷史建置／「舊版未改」敘述，不能逐字照做。詳細版在 28 日已另行更新；較新的 verifier 會依封存 receipt 驗證原版。跨版本依賴與交付 audit 分開，不為更新一冊順手重建另一冊。

## 使用手冊入口

在 `codes/v3/poc_mp3_preprocessors/docs/20260929/documentations/`：

- `README.md`、`package.json`：確認現行命令與依賴。
- `docs-nodejs/navigation.mjs`：網站與 PDF 的共用章節順序。
- `docs-nodejs/content/`、`content/zh/`：雙語內容，相同檔名及 heading IDs。
- `scripts/capture-current-interface.cjs`：當前本機平台截圖；舊 capture 工具另有資料副本用途，不混淆。
- `docs-nodejs/content/assets/screenshots/capture-info.json`：截圖路由、範圍及來源紀錄。
- `npm run screenshots:current`、`verify:platform`：需本機平台，不為文件啟動分析工作。
- `npm run build`、`verify`、`pdf`、`pdf:verify`：以該專案當前 package.json 核對，非其他專案的必要命令。

## 可重用與不宜照搬

可重用：資料與文案分離、完整提示原文、分母、證據狀態、雙語對應、分頁經驗、相依工期、離線驗證及明確選檔。

不宜照搬：作者／日期、固定樣本數、頁數、資料快照、內部方法名稱、私人路徑、連接埠、依賴版本、保護檔例外及特定讀者要求。當前 report-app 的 AGENTS.md 與已安裝插件規範優先於歷史建置筆記。

## 此技能包的首次驗證

2026-10-29：`test_tools.py` 的 14 項 Python 檢查通過；`test_browser.py` 使用既有 Node.js 24.18.0／Playwright 1.63.0，在隔離 loopback 服務完成六個情境，四份靜態樣本可截圖／匯出 PDF，overflow 和 POST 情境正確判為失敗，伺服器收到零個 POST。抽看繁中桌面／手機截圖，無明顯裁切。這不包含正式 Reveal runtime、真實平台功能或完整 PDF 字元／書籤驗證。

Python／Node 語法及 Markdown 參考連結已檢查。Skill Creator 的 `quick_validate.py` 因本機 Python 缺 PyYAML 未能完成；使用既有 Ruby YAML parser 獨立檢查 frontmatter、名稱、說明及 UI invocation 欄位通過，沒有安裝依賴或修改該驗證器。日後已有 PyYAML 時可重跑標準驗證器。
