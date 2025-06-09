# 速Per Idol - 飲食+運動管理網站

速Per Idol 是一個全方位的健康飲食、運動追蹤應用程式，幫助用戶管理日常飲食和營養攝取，促進健康生活方式。

---

## 專案技術棧

### 前端
- **Vue 3** + **Pinia**（狀態管理）
- **Vue Router**（路由）
- **Element Plus**（UI元件）
- **Axios**（HTTP 請求）
- **Vite**（前端構建工具）
- **ESLint + Prettier**（代碼規範）

### 後端
- **Flask**（Python Web 框架）
- **Flask-SQLAlchemy**、**PyMySQL**（MySQL ORM/連線）
- **Flask-Cors**（CORS 支援）
- **Flask-Migrate**（資料庫遷移）
- **PyJWT**（JWT 認證）
- **python-dotenv**（環境變數管理）
- **pytest**（單元測試）

---

## 目錄結構

```
super-idol/
├── frontend/              # 前端 Vue 專案
│   ├── src/...
│   ├── dist/              # 前端 build 產物（可刪除，不需版本控制）
│   └── node_modules/      # 前端依賴（可刪除，不需版本控制）
├── backend/               # 後端 Flask 專案
│   ├── app/...
│   ├── static/            # 靜態文件目錄（由前端 build 複製，可重建）
│   └── .venv/             # Python 虛擬環境（可刪除，不需版本控制）
├── scripts/               # 開發/部署腳本
│   ├── dev.js             # 一鍵啟動前後端
│   ├── setup.js           # 一鍵安裝依賴與初始化
│   └── deploy.sh          # 部署腳本
└── ...
```

---

## 快取與產物目錄說明

- `node_modules/`、`dist/`、`__pycache__/`、`.venv/` 均為自動產生的快取或 build 產物，**可隨時安全刪除**。
- 這些目錄**不應加入版本控制**，請確認 `.gitignore` 已包含：
  ```
  node_modules/
  dist/
  __pycache__/
  .venv/
  .DS_Store
  ```
- 刪除後只需重新執行 `npm install`、`npm run build`、`pip install -r requirements.txt` 等指令即可自動恢復。

---

## 開發環境快速啟動

### 一鍵自動化（推薦）

```bash
# 1. 複製專案
git clone <repository-url>
cd super-idol/scripts

# 2. 一鍵設置與啟動
node setup.js   # 安裝依賴、建立 .env、初始化目錄
node dev.js     # 同時啟動前端與後端
```
- 前端: http://localhost:5173
- 後端: http://localhost:5000

### 手動啟動

**前端：**
```bash
cd super-idol/frontend
npm install
npm run dev
```

**後端：**
```bash
cd super-idol/backend
pip install -r requirements.txt
python run.py
```

---

## 常見問題與排查

1. **CORS 跨域錯誤**
   - 確認後端已啟動且 CORS 設定正確
   - 可用 http://localhost:5000/api/test-cors 測試
2. **API 連線失敗**
   - 檢查後端服務是否啟動、資料庫連線資訊是否正確
3. **端口被佔用**
   - 修改 `frontend/vite.config.js` 或 `.env` 指定其他可用端口
4. **資料庫初始化/重建**
   - 若已不需重建，可刪除 `scripts/init_db.py`、`scripts/exercise_items.sql`

---

## 專案清理建議

- 可安全刪除：`node_modules/`、`dist/`、`__pycache__/`、`.venv/`、`.DS_Store`、`scripts/init_db.py`、`scripts/exercise_items.sql`（如已無需重建資料庫）
- 請勿將上述目錄/檔案加入版本控制

---

## 參與貢獻

1. Fork 本倉庫
2. 建立分支 (`git checkout -b feature/your-feature`)
3. 提交並推送 (`git commit -m 'feat: 新功能說明'`)
4. 發送 Pull Request

---

## 授權

本專案採用 ISC License 授權。 