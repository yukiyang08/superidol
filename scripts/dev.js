// dev.js 開發環境啟動腳本
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 輔助函數：檢查路徑是否存在
function checkPathExists(dirPath) {
  try {
    return fs.existsSync(dirPath);
  } catch (err) {
    console.error(`檢查路徑時出錯: ${dirPath}`, err);
    return false;
  }
}

// 獲取正確的路徑
const scriptDir = __dirname;
const projectRoot = path.resolve(scriptDir, '..');

const frontendDir = path.join(projectRoot, 'frontend');
const backendDir = path.join(projectRoot, 'backend');

// 驗證路徑
console.log('==== 啟動環境檢查 ====');
console.log(`項目根目錄: ${projectRoot}`);
console.log(`前端目錄: ${frontendDir} (${checkPathExists(frontendDir) ? '存在' : '不存在!'})`);
console.log(`後端目錄: ${backendDir} (${checkPathExists(backendDir) ? '存在' : '不存在!'})`);

if (!checkPathExists(frontendDir)) {
  console.error('錯誤: 找不到前端目錄!');
  process.exit(1);
}

if (!checkPathExists(backendDir)) {
  console.error('錯誤: 找不到後端目錄!');
  process.exit(1);
}

// 啟動前端
console.log('\n==== 啟動前端 ====');
const frontend = spawn('npm', ['run', 'dev'], { 
  cwd: frontendDir,
  shell: true,
  stdio: 'inherit'
});

// 啟動後端
console.log('\n==== 啟動後端 ====');
const backend = spawn('python', ['run.py'], { 
  cwd: backendDir,
  shell: true,
  stdio: 'inherit'
});

console.log('\n==== 開發環境已啟動 ====');
console.log('前端: http://localhost:5173');
console.log('後端: http://localhost:5000');
console.log('按 Ctrl+C 可停止所有服務');

// 處理進程錯誤
frontend.on('error', (err) => {
  console.error('前端啟動失敗:', err);
  if (backend) backend.kill();
  process.exit(1);
});

backend.on('error', (err) => {
  console.error('後端啟動失敗:', err);
  if (frontend) frontend.kill();
  process.exit(1);
});

// 處理退出信號
process.on('SIGINT', () => {
  console.log('\n正在關閉服務...');
  if (frontend) frontend.kill();
  if (backend) backend.kill();
  process.exit(0);
});

// 監聽子進程結束
frontend.on('close', (code) => {
  if (code !== 0 && code !== null) {
    console.error(`前端進程異常退出，代碼: ${code}`);
  } else {
    console.log(`前端進程已退出，代碼: ${code}`);
  }
  // 不自動終止後端，讓用戶可以單獨重啟前端
});

backend.on('close', (code) => {
  if (code !== 0 && code !== null) {
    console.error(`後端進程異常退出，代碼: ${code}`);
  } else {
    console.log(`後端進程已退出，代碼: ${code}`);
  }
  // 不自動終止前端，讓用戶可以單獨重啟後端
});