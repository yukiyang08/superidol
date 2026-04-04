import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  root: '.',          // ← 將 root 改為專案根目錄，Vite 會自動載入 frontend/index.html
  publicDir: 'public',

  server: {           // 本地開發伺服器設定
    port: 5173,       // 啟動於 5173 端口
    open: true,       // 啟動後自動開啟瀏覽器
    proxy: {          // API 代理設定
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from:', req.url, proxyRes.statusCode);
          });
        }
      }
    }
  },

  build: {            // 打包設定
    outDir: 'dist',   // 打包輸出目錄
    assetsDir: 'assets',
    sourcemap: true
  },

  resolve: {          // 別名設定
    alias: {
      '@': path.resolve(__dirname, './src')  // import 時用 '@/…' 直接指向 src
    }
  }
})
