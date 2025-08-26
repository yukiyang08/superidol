# Git 操作指南 - Super Idol 專案

本文檔將指導團隊成員如何使用 Git 進行版本控制，特別是如何在我們的六個個人分支上進行操作。

## 目錄
1. [分支結構](#分支結構)
2. [初始設置](#初始設置)
3. [日常工作流程](#日常工作流程)
4. [拉取更新 (Pull)](#拉取更新-pull)
5. [提交更改 (Commit)](#提交更改-commit)
6. [推送更新 (Push)](#推送更新-push)
7. [分支合併 (Merge)](#分支合併-merge)
8. [處理衝突](#處理衝突)
9. [常見問題與解決方案](#常見問題與解決方案)

## 分支結構

共設了 6 個個人分支，每個人負責自己的分支：

- `llona` - Llona 負責的分支
- `andrew` - Andrew 負責的分支
- `sherry` - Sherry 負責的分支
- `chiao` - Chiao 負責的分支
- `rita` - Rita 負責的分支
- `yuki` - Yuki 負責的分支

主分支是 `main`，用於整合所有成員的工作。

## 初始設置

### 1. 克隆專案

首次獲取專案時，請執行以下命令：

```bash
# 克隆專案儲存庫
git clone https://github.com/使用者名稱/super-idol.git

# 進入專案目錄
cd super-idol
```

### 2. 查看所有分支

```bash
# 列出所有本地和遠程分支
git branch -a
```

### 3. 切換到你的專屬分支

根據你的名字，選擇相應的分支：

```bash
# 例如，如果你是 Yuki，切換到 yuki 分支
git checkout yuki

# 如果是第一次切換，可能需要使用 -b 來創建並切換
git checkout -b yuki origin/yuki
```

## 日常工作流程

每天開始工作前，建議執行以下步驟：

### 1. 確保你在正確的分支上

```bash
# 查看當前分支
git status
```

輸出應該顯示你正在自己的分支上（例如 `On branch yuki`）。

### 2. 獲取最新的主分支更新

```bash
# 獲取所有遠程分支的更新
git fetch origin

# 將主分支的更新合併到你的分支
git merge origin/main
```

### 3. 開始你的工作

現在你可以開始修改檔案、新增功能或修復問題。

## 拉取更新 (Pull)

### 從遠端分支拉取更新

如果你的分支已經在遠端有了更新（例如其他電腦上的修改），使用以下命令更新你的本地分支：

```bash
# 確保你在正確的分支上
git checkout yuki

# 拉取遠端分支的更新
git pull origin yuki
```

### 從主分支拉取更新

要將主分支的最新變更整合到你的分支中：

```bash
# 確保你在自己的分支上
git checkout yuki

# 拉取主分支的更新
git pull origin main
```

如果出現衝突，請參閱[處理衝突](#處理衝突)部分。

## 提交更改 (Commit)

當你完成一部分工作後，應該提交這些更改：

```bash
# 查看哪些文件已被修改
git status

# 將所有修改的文件添加到暫存區
git add .

# 或者選擇性地添加文件
git add 檔案路徑1 檔案路徑2

# 提交更改，附帶清晰的描述性訊息
git commit -m "新增登入頁面設計"
```

提交訊息的建議格式：
- "新增功能：XXX" - 用於添加新功能
- "修復問題：XXX" - 用於修復錯誤
- "改進：XXX" - 用於提升現有功能
- "重構：XXX" - 用於重構代碼而不改變功能

## 推送更新 (Push)

將你的本地提交推送到遠端儲存庫：

```bash
# 推送到你的分支
git push origin yuki
```

如果是第一次推送新分支：

```bash
git push -u origin yuki
```

設置 `-u` 後，之後就可以直接使用 `git push` 而不需要指定分支名。

## 分支合併 (Merge)

### 合併到主分支

當你的功能完成並經過測試後，需要將其合併到主分支：

```bash
# 首先切換到主分支
git checkout main

# 拉取主分支的最新狀態
git pull origin main

# 合併你的分支到主分支
git merge yuki

# 推送更新後的主分支
git push origin main

# 切回你的分支繼續工作
git checkout yuki
```

注意：在某些團隊中，可能會要求通過 Pull Request 來進行合併，而不是直接合併。

### 合併主分支到你的分支

定期將主分支的更新合併到你的分支，以避免未來出現大量衝突：

```bash
# 確保你在自己的分支上
git checkout yuki

# 拉取主分支的更新
git merge origin/main

# 解決可能的衝突後，推送更新
git push origin yuki
```

## 處理衝突

當合併或拉取時出現衝突，Git 會提示「Merge conflict」：

1. **查看衝突文件**：
   ```bash
   git status
   ```

2. **打開衝突文件**，你會看到類似這樣的標記：
   ```
   <<<<<<< HEAD
   你的更改
   =======
   其他分支的更改
   >>>>>>> 分支名稱
   ```

3. **編輯文件解決衝突**：
   - 刪除衝突標記 `<<<<<<< HEAD`、`=======` 和 `>>>>>>> 分支名稱`
   - 選擇保留哪些部分或如何合併兩者

4. **標記為已解決**：
   ```bash
   git add 衝突文件路徑
   ```


5. **完成合併**：
   ```bash
   git commit -m "解決合併衝突"
   ```

6. **推送更改**：
   ```bash
   git push origin yuki
   ```

## 常見問題與解決方案

### 1. 我想撤銷未提交的更改

```bash
# 撤銷單個文件的更改
git checkout -- 檔案路徑

# 撤銷所有未暫存的更改
git checkout -- .

# 撤銷已暫存的更改（先取消暫存，再撤銷）
git reset
git checkout -- .
```

### 2. 我想撤銷最後一次提交

```bash
# 保留更改，但撤銷提交
git reset --soft HEAD~1

# 完全撤銷提交和更改（危險！）
git reset --hard HEAD~1
```

### 3. 我需要切換分支，但有未提交的更改

```bash
# 暫存當前工作
git stash

# 切換分支
git checkout 其他分支

# 完成工作後，切回原分支
git checkout 原分支

# 恢復暫存的工作
git stash pop
```

### 4. 我想查看提交歷史

```bash
# 查看簡潔的提交歷史
git log --oneline

# 查看圖形化的分支歷史
git log --graph --oneline --all

# 查看特定文件的修改歷史
git log --follow 檔案路徑
```

### 5. 遠端拒絕推送（Push rejected）

這通常是因為遠端分支有你本地沒有的更新：

```bash
# 先拉取遠端更新
git pull origin yuki

# 解決可能的衝突後，再次推送
git push origin yuki
```

### 6. 如何查看兩個分支之間的差異

```bash
# 查看你的分支與主分支的差異
git diff yuki..main
```

### 7. 我提交了敏感資料或超大檔案，需要移除

```bash
# 在所有歷史中移除檔案（需謹慎使用）
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch 敏感檔案路徑" --prune-empty --tag-name-filter cat -- --all

# 強制推送更改
git push origin --force --all
```

記住：Git 是一個強大的工具，可以幫助你管理代碼，但也有潛在的風險。請謹慎使用破壞性操作（如 `--force` 和 `--hard`）。

如有更多 Git 相關問題，請參考 [Git 官方文檔](https://git-scm.com/doc) 

# Mac 環境下 API 連接失敗的完整排查方案

這種情況很可能是 Mac 系統特有的網絡設置或權限問題，以下是系統性的排查步驟：

## 1. 後端服務狀態檢查

```bash
# 確認後端是否運行
ps aux | grep python
# 或
ps aux | grep flask

# 查看5000端口是否被使用
lsof -i :5000
```

## 2. 網絡連接測試

```bash
# 測試本地網絡
ping localhost

# 嘗試使用curl訪問API
curl http://localhost:5000/api/test-cors
# 或
curl http://127.0.0.1:5000/api/test-cors
```

## 3. Mac 特有問題排查

### 網絡配置問題
```bash
# 檢查hosts文件
cat /etc/hosts
# 確保有 "127.0.0.1 localhost" 這一行

# 檢查網絡接口
ifconfig lo0
# 確保loopback接口啟動
```

### 防火牆設置
1. 打開「系統設置」>「網絡」>「防火牆」
2. 暫時關閉防火牆進行測試
3. 如果關閉後工作正常，重新開啟並添加Flask應用例外

## 4. 前端配置檢查

```bash
# 檢查前端API配置
cat super-idol/frontend/src/services/api.js
```

將baseURL修改為：
```javascript
// 嘗試使用IP地址而非localhost
const baseURL = 'http://127.0.0.1:5000/api';
```

## 5. 後端CORS設置確認

```bash
# 查看後端CORS配置
cat super-idol/backend/app/__init__.py
```

確保CORS設置為：
```python
CORS(app, resources={r"/*": {"origins": "*"}})
```

## 6. Mac專用解決方案

### 嘗試使用不同端口
```bash
# 編輯.env文件
echo "PORT=8080" >> super-idol/backend/.env

# 重啟後端
# 然後修改前端API地址為 http://127.0.0.1:8080/api
```

### 使用特定網絡接口
修改run.py文件：
```python
app.run(host='127.0.0.1', port=5000, debug=True)
```

## 7. 特殊權限問題

某些Mac版本(尤其是M1/M2芯片)可能有特殊的安全機制：
```bash
# 嘗試以管理員權限運行
sudo python3 run.py

# 檢查應用程序權限
ls -la super-idol/backend/run.py
chmod +x super-idol/backend/run.py
```

## 8. 查看瀏覽器Console錯誤

打開瀏覽器開發者工具(F12)，查看Console標籤中的具體錯誤信息。
錯誤訊息會提供更多線索，比如：
- "Network Error" - 表示無法連接
- "CORS error" - 表示跨域問題
- 具體HTTP錯誤碼

如果以上步驟都不能解決問題，請提供瀏覽器控制台的具體錯誤訊息，以便進一步診斷。 