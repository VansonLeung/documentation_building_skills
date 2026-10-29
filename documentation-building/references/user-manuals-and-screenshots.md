# 使用手冊與平台截圖

## 按任務編排

先列使用者要完成的工作，例如找結果、篩選、查看證據、播放、覆核、匯出；用目前畫面標籤和可觀察行為說明。技術細節只在協助判斷時加入。把工作提交／重跑集中於管理章，避免多頁互相矛盾。

以共用 navigation 定義網站和 PDF 章節順序；雙語使用相同頁名及 anchor IDs。不要讓建置腳本用歷史設計文件覆蓋當前手冊。

若 HTML 是已確認的主要編輯來源，直接維護 HTML 亦可；共用 navigation 可由 headings 生成。從舊 DOCX／PPTX 遷移，見 [source-migration-and-reconciliation.md](source-migration-and-reconciliation.md)。需要可編輯 Word 和同次分頁一致的 PDF，見 [office-exports.md](office-exports.md)，不要把 Word styles 當成瀏覽器 CSS 的自然延伸。

## 擷取流程

1. 核對當前版本、路由、預覽服務及授權範圍。沿用已有截圖工具；無需為截圖重跑模型。
2. 使用已核准的測試資料／唯讀實例。初始 GET 也可能有副作用，先確認伺服器行為；僅限制 HTTP method 不能保證服務唯讀。
3. 阻擋非必要外部要求、提交、工作啟動與編輯；避免設定／憑證頁。真要記錄寫入操作時先建立隔離資料副本，且需在任務授權範圍內。
4. 固定 viewport、縮放、語言及篩選條件；等待字型、資料、圖像及 loading 結束。
5. 查看截圖，檢查敏感文字、裁切、彈窗、游標遮擋及空白圖。

擷取紀錄可含：

```text
image, route, captured_at, app_revision, language, viewport,
filters, data_snapshot, sha256, redactions, actions_performed
```

數字是擷取時快照，不把截圖數字寫成永不變動的系統常數。原始截圖保留來源，裁切／遮蔽版另存，記錄關係。

## 展示與驗證

- 優先展示一項任務的關鍵畫面，不用整頁縮小到無法閱讀。
- 圖說指出要看哪個控制項；無障礙替代文字說明用途。
- HTML 可連大圖；PDF 保留足以閱讀的尺寸、圖說及操作步驟。
- 檢查桌面／窄螢幕、語言切換、章節連結及搜尋。對有變更的篩選、圖例、展開、下鑽及匯出做對應操作驗證。
- 截圖成功不等於功能檢查通過；隨附通用瀏覽器工具只提供基本幾何／載入檢查，真正工作流程由專案測試補充。
