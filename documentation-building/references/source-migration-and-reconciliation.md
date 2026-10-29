# 舊文件遷移與對照

用於把 PPTX／DOCX／PDF 等既有材料轉成可維護 HTML 或另一格式。單純改標題不需要啟動完整遷移流程。

## 確定 baseline

先問清楚哪份來源代表要保留的內容。同名 PPTX、PDF、Keynote 可能不同版；頁數不同不代表新稿漏頁。比對來源後記錄 authoritative_source、版次、日期、SHA-256 和不一致處。

沒有證據時不要從較大頁數推定它較新，也不要把歷史 coverage 表當作目前計數。格式遷移不自動授權新增產品能力、刪改教學重點或重新編排；使用者已有重整授權時，則按該範圍記錄去向。

## 建立輕量對照

```text
source_id, source_file, source_locator, source_hash,
destination_id, disposition, asset_ref, crop,
notes_status, reason, reviewed_at
```

disposition 可為 retained、rewritten、split、merged、moved、omitted 或 pending。重要的是可查去向，無需每次套固定表格。

需分開記錄：

- 投影片／章節的內容去向。
- 圖片原始 bytes、每次放置位置及裁切；同一圖片可能多次使用。
- 講者備註及歷史頁碼參照；忠實保留與更新參照是不同決定。
- 空白 placeholder、裝飾和真正教學圖片；隱藏 1-pixel 圖不等於少了一張教學截圖。
- native tables、文字及 screenshots；總圖片數相同不能證明內容完整。

如移除 placeholder 或重排編號，寫明理由。新頁使用新的 stable ID，不重用 source-slide 編號假裝是舊頁。標題、數據及例子是否改寫，與單純版型變更分開記錄。

## 導入與日常維護分開

一次性 import 工具只建立初稿。完成人工修正後，以已指定的 maintained HTML／資料為主；日常建置不得自動重跑 import 覆蓋。

需要重做導入時，先確認覆蓋範圍和備份；在暫存目錄產生差異，再決定合併。不因找到舊腳本的 `--overwrite` 就執行它。

原始文件與 Word 樣式範本分開。唯讀開啟來源做比較，避免 Office 自動存檔改寫 baseline。來源未包含的流程或「最佳實務」可提出建議，未被採納前不補寫成已確認操作。

## 驗證與交付

先按 source_id 對照去向，再比文字、notes、圖片 hashes／placements、表格及 crop，最後看實際畫面。HTML、PDF 和 Office 的計數應對應當前範圍；不是所有文件都要求與 baseline 頁數相同。

交付簡短 reconciliation：保留了甚麼、刻意改了甚麼、仍待確認甚麼。不要把所有原始內部文件自動帶進共享包。若來源不可隨包附上，保留來源識別及 hashes，並說清楚共享包能重現到哪一層。
