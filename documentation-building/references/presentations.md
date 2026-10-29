# Reveal.js 會議簡報

## 敘事與順序

依觀眾的理解順序分組：問題與成果 → 資料及處理 → 評測與限制 → 下一步。頁數與會議長度由任務決定，不固定成海事簡報的張數。

一張一個主要問題，標題說清楚主題或結論。例如用「如何找出對話交錯候選」代替「時間接近縮小搜尋，並非證明」。數字頁標明母體及範圍；具體例子放要點側，較長技術內容放備註或聆聽附頁。

保留 stable slide ID，顯示順序與來源 ID 分開。重排時同步章節進度、語言連結、講者備註及來源圖解，不只改頁碼。

操作培訓可採截圖＋側欄，說清楚「看到甚麼 → 先檢查甚麼 → 下一步」。長篇 deck 的入口分流、閱讀模式、搜尋及跳頁，按需要閱讀 [slide-navigation-and-search.md](slide-navigation-and-search.md)；不要求所有短簡報加入控制功能。

## 動畫

先決定是否需要動畫；靜態培訓 deck 也是合理選擇。需要動畫而未另有要求時，以講者手動推進為預設建議。流程圖逐步顯示輸入、判斷及輸出；數據表和關鍵數字不靠動畫才可讀。

- 使用 Reveal 的 fragment / fragment-index，避免改 vendor runtime。
- 完整測試前進、倒退、跨頁、Show all、關閉動畫和語言切換。
- 尊重 reduced-motion；關閉動畫時顯示完整內容。
- Print/PDF 顯示所有步驟，只輸出每張一次，避免 fragment 造成重複頁。
- 保持方向鍵、空白鍵、焦點與播放器控制正常；頁面轉換時暫停音訊。

## 可攜與輸出

如需離線，固定並隨包帶合法可分發的 Reveal runtime／授權檔，不依靠會議場地 CDN。不要把第三方 runtime 混成自己的技能程式。

PDF 必須檢查每張裁切、長中文標題、表格、圖說和頁數。動畫與音訊的意義要有完整靜態圖、文字和附件連結承接。備註可能含內部資料；不要默認把內部備註交付給外部讀者。

隨附瀏覽器工具可匯出靜態 HTML；Reveal 的專用輸出仍應走既有 deck export 流程（經測試的 print-pdf 或固定 screen-layout export），並自行驗證 fragment 與 speaker notes。不要假定通用列印模式適合全部版面。工具不自動猜測或點擊簡報控制。

如需 PPTX，先看 [office-exports.md](office-exports.md)：預設建議圖片式並明確說明限制；如果要求原生可編輯物件，另選製作流程。從既有 PPTX／DOCX 遷移前，先按 [source-migration-and-reconciliation.md](source-migration-and-reconciliation.md) 指定 baseline 及對照方式。
