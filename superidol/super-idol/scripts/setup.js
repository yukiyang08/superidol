// setup.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 顯示開始信息
console.log('===== 設置 Super Idol 開發環境 =====');

// 建立後端靜態目錄
const staticDir = path.join(__dirname, '..', 'backend', 'static');
if (!fs.existsSync(staticDir)) {
  fs.mkdirSync(staticDir, { recursive: true });
}
console.log('後端靜態目錄已創建');

// 創建環境變數文件
const envContent = `DB_HOST=superidol.c9i82eygu8mk.ap-southeast-2.rds.amazonaws.com
DB_PORT=3306
DB_USER=DBMS11302
DB_PASSWORD=ilovedbms
DB_NAME=superidol
FLASK_ENV=development
JWT_SECRET_KEY=dev-key-for-local-development
SECRET_KEY=local-dev-secret-key`;

fs.writeFileSync(path.join(__dirname, '..', 'backend', '.env'), envContent);
console.log('環境變數文件已創建');

// 安裝依賴
try {
  console.log('安裝前端依賴...');
  execSync('cd ../frontend && npm install', { stdio: 'inherit' });
  
  console.log('安裝後端依賴...');
  execSync('cd ../backend && pip install -r requirements.txt', { stdio: 'inherit' });
  
  console.log('===== 設置完成 =====');
  console.log('您現在可以運行 "node dev.js" 啟動開發環境');
} catch (error) {
  console.error('設置過程中發生錯誤:', error);
}