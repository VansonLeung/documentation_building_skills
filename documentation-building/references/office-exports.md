# 可選 Office 輸出

## 選擇交付契約

只有任務需要時才加入 Office，不因有範例工具就每次產生 PPTX／DOCX。沿用既有已授權的輸出方式；沒有工具時先記錄缺項，不把依賴安裝當成文件修訂的預設步驟。

| 輸出 | 適用目的 | 必須交代的限制 |
|---|---|---|
| 圖片式 PPTX（預設建議） | 保持 HTML 的字型、位置及圖解外觀，方便會議播放 | 每張是完整圖片，不能逐項改文字或圖形；沒有原生動畫，圖片內文字不可當原生文字搜尋 |
| 原生可編輯 PPTX | 接手團隊需要修改物件、表格或圖形 | 需要另做版面映射及字型／軟件測試，與 HTML 未必完全一致 |
| 可編輯 DOCX | 接手團隊需要修改段落及表格 | 截圖仍是圖片；瀏覽器 CSS 不會自動轉成 Word 樣式 |
| HTML-derived PDF | 保留 HTML 排版及可選取的正文文字 | 圖片內文字仍是圖片；需獨立驗證字型、頁數及搜尋 |
| DOCX-derived PDF | 希望同次生成的 Word 與 PDF 分頁相符 | 換軟件、字型或修改 DOCX 後可能重新分頁 |

用 metadata 或交付說明記錄 contract，例如：

```json
{
  "office_enabled": true,
  "pptx_mode": "full-slide-images",
  "pptx_native_text_editable": false,
  "pptx_animation": "none",
  "speaker_notes": "approved-only",
  "guide_pdf_source": "docx"
}
```

這是契約示例，不是現有通用打包／瀏覽器工具的新增參數。輸出前確認所選 exporter 真能履行契約。講者備註可保留為可編輯文字，但不能因此把整張圖片式 PPTX 稱為可編輯簡報。

## 圖片式 PPTX

1. 使用完整顯示所有 fragment 的確定性 export view；等待字型、圖片及 layout 完成。
2. 固定每張畫布及比例，用元素 screenshot 擷取每張。LD 範例使用 16:9、2560×1440，屬該專案的設定，不是所有任務的固定規格。
3. 每張放一張滿版圖片，附上簡短 alt text 和已批准的講者備註。不要把內部備註順手加進外部檔案。
4. 頁碼依現行順序生成；保留 slide_id 與來源映射。圖片去重只減少資產儲存，不刪掉重複教學位置。
5. 以同一 export view 另外生成 HTML-derived PDF；不要為方便而將圖片式 PPTX 再轉成 PDF，卻宣稱正文仍可選取。

使用 PptxGenJS 等工具只是可選實作。若既有技術棧不同，不為套此例而改寫。Reveal 的通用 print 模式不適合某些固定尺寸版面；按當前 exporter 實測選擇 print media 或固定 screen-layout export。

## HTML → DOCX → PDF

HTML 作主要編輯來源時，從正文區域抽取 headings、paragraphs、tables、images 與 links；不要把搜尋工具列或閱讀控制帶進 Word。由當前 headings 重建 TOC，避免沿用過時頁碼或未更新的 Word TOC field。

需要可編輯正文時，可用 Pandoc 等轉換器，並使用獨立 reference DOCX 控制 Word styles、紙張、header/footer。只改瀏覽器 CSS，不代表 DOCX 已更新。原始文件與已整理的樣式範本分開保留。

如要求 Word／PDF 分頁相符，用同次生成的 DOCX 經已選定的 Office renderer 匯出 PDF；不要另一邊直接列印 HTML。若用 LibreOffice 自動化，採獨立暫存 profile，避免干擾使用者現有 Office session。

## 驗證與維護

- ZIP／XML 可讀只證明封裝基本有效，不證明在 PowerPoint 或 Word 排版正常。
- PPTX：張數、16:9／指定比例、圖片清晰度、approved notes 內容、alt text、裁切、字型外觀及檔案大小。
- DOCX：正文段落、表格、圖片位置及連結保留；「可編輯」要檢查 native text/table，不能只看副檔名。
- PDF：逐頁數目、可選取標題／正文、中文、近乎空白頁及 contact sheets。
- 在可用的目標軟件開啟並抽看重要頁；只測過 Keynote／LibreOffice 時照實標示，不能稱已驗證 Microsoft PowerPoint／Word。
- 首次建立或大改 exporter 時，在暫存副本修改一段文字／一個樣式後重新輸出，確認新內容確實進入成品。日常小修不必每次重跑全部遷移測試。
- source fingerprint 記錄影響輸出的輸入；交付 manifest 另記成品 bytes／SHA-256。兩者用途不同，詳見 [pdf-and-delivery.md](pdf-and-delivery.md)。

本技能已有範本相容的 `export_presentation.mjs`、可選 `export_guide.py` 及唯讀 inspectors，詳見 [standalone-toolkit.md](standalone-toolkit.md)。它們不調用 LD 原專案；原碼位置只作 [歷史實例索引](ld-project-examples.md)。尚未提供原生可編輯 PPTX 生成器。
