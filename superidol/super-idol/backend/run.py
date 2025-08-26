"""
Application entry point.
"""

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
import logging
import glob
import shutil
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尋找靜態文件目錄
def find_static_directory():
    """尋找最佳的靜態文件目錄，按優先級：
    1. ./static (直接在當前目錄下的靜態目錄)
    2. ../frontend/dist (前端構建目錄)
    3. 各種可能的 Render 環境下的絕對路徑
    """
    # 獲取當前文件目錄
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    # 上一級目錄，即super-idol目錄
    project_dir = os.path.dirname(backend_dir)
    
    # 記錄當前檔案和目錄資訊
    logger.info(f"當前檔案路徑: {__file__}")
    logger.info(f"後端目錄: {backend_dir}")
    logger.info(f"項目目錄: {project_dir}")
    logger.info(f"工作目錄: {os.getcwd()}")
    
    # 記錄環境變數，不包含敏感信息
    env_vars = {k: v for k, v in os.environ.items() 
                if not any(s in k.lower() for s in ['secret', 'password', 'key'])}
    logger.info(f"環境變數: {env_vars}")
    
    # 檢查關鍵環境變數是否存在
    for key in ['FLASK_ENV', 'DB_HOST', 'DB_USER', 'DB_NAME']:
        value = os.environ.get(key)
        if value:
            logger.info(f"環境變數 {key} 存在")
        else:
            logger.warning(f"環境變數 {key} 不存在")
    
    # 嘗試可能的靜態目錄路徑，按優先級順序
    possible_paths = [
        os.path.join(backend_dir, 'static'),           # 後端靜態目錄
        os.path.join(project_dir, 'frontend', 'dist'),  # 前端構建目錄
    ]
    
    # 嘗試各種可能的 Render 路徑
    render_base_paths = [
        '/opt/render/project/src',             # 基本 Render 路徑
        '/opt/render/project',                  # 備用 Render 路徑
        '/opt/render'                          # 更上層的 Render 路徑
    ]
    
    # 嘗試可能的專案結構
    project_structures = [
        ['backend', 'static'],                 # /backend/static
        ['super-idol', 'backend', 'static'],   # /super-idol/backend/static
        ['frontend', 'dist'],                  # /frontend/dist
        ['super-idol', 'frontend', 'dist'],    # /super-idol/frontend/dist
        ['static'],                            # /static - 直接在根目錄
        ['dist']                               # /dist - 直接在根目錄
    ]
    
    # 為 Render 環境添加所有可能的絕對路徑
    if os.environ.get('RENDER') == 'true':
        render_paths = []
        for base_path in render_base_paths:
            # 檢查是否有 super-idol 目錄
            if os.path.exists(os.path.join(base_path, 'super-idol')):
                logger.info(f"找到 super-idol 目錄: {os.path.join(base_path, 'super-idol')}")
            
            # 先檢查基本路徑下的靜態目錄
            if os.path.exists(os.path.join(base_path, 'static')):
                render_paths.append(os.path.join(base_path, 'static'))
            
            # 加入各種可能的組合
            for structure in project_structures:
                path = os.path.join(base_path, *structure)
                render_paths.append(path)
        
        # 加入當前工作目錄相關路徑
        cwd = os.getcwd()
        render_paths.append(os.path.join(cwd, 'static'))
        
        # 在最高優先級添加這些路徑
        possible_paths = render_paths + possible_paths
        
        # 嘗試直接在目錄下搜尋 dist 或 static 文件夾
        for base_path in render_base_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    if 'dist' in dirs:
                        possible_paths.insert(0, os.path.join(root, 'dist'))
                        logger.info(f"搜尋到 dist 目錄: {os.path.join(root, 'dist')}")
                    if 'static' in dirs:
                        possible_paths.insert(0, os.path.join(root, 'static'))
                        logger.info(f"搜尋到 static 目錄: {os.path.join(root, 'static')}")
                    # 限制搜尋深度，避免過度遞歸
                    if root.count(os.sep) - base_path.count(os.sep) > 3:
                        break
    
    # 記錄所有要檢查的路徑
    logger.info(f"將檢查以下路徑: {possible_paths}")
    
    found_path = None
    
    # 檢查每個可能的路徑
    for path in possible_paths:
        logger.info(f"檢查靜態目錄: {path}")
        
        if os.path.exists(path):
            logger.info(f"目錄存在: {path}")
            # 檢查index.html是否存在
            index_path = os.path.join(path, 'index.html')
            if os.path.exists(index_path) and os.path.isfile(index_path):
                logger.info(f"找到有效的靜態目錄: {path}")
                found_path = path
                break
            else:
                try:
                    # 檢查目錄內有哪些文件
                    files = os.listdir(path)
                    logger.warning(f"目錄存在但沒有index.html: {path}，內容: {files}")
                except Exception as e:
                    logger.warning(f"讀取目錄內容失敗: {path}, 錯誤: {str(e)}")
        else:
            logger.warning(f"目錄不存在: {path}")
    
    # 如果找不到任何有效目錄，使用後端靜態目錄並創建簡單的index.html
    if not found_path:
        static_dir = os.path.join(backend_dir, 'static')
        logger.warning(f"未找到任何有效靜態目錄，將使用並創建: {static_dir}")
        
        try:
            os.makedirs(static_dir, exist_ok=True)
            index_html = os.path.join(static_dir, 'index.html')
            
            # 創建更完整的應急前端頁面
            with open(index_html, 'w') as f:
                f.write('''
                <!DOCTYPE html>
                <html lang="zh-TW">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Super Idol 健康管理系統</title>
                    <style>
                        body { 
                            font-family: Arial, sans-serif; 
                            max-width: 800px; 
                            margin: 0 auto; 
                            padding: 20px; 
                            background-color: #f9f9f9;
                        }
                        h1 { 
                            color: #2c3e50; 
                            text-align: center;
                            border-bottom: 2px solid #3498db;
                            padding-bottom: 10px;
                        }
                        .card { 
                            background-color: white;
                            padding: 20px; 
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
                            margin: 20px 0; 
                            border-radius: A0px;
                        }
                        .info { color: #3498db; }
                        .error { color: #e74c3c; }
                        .btn {
                            display: inline-block;
                            padding: 10px 15px;
                            background: #3498db;
                            color: white;
                            text-decoration: none;
                            border-radius: 4px;
                            margin-top: 15px;
                        }
                        .center {
                            text-align: center;
                        }
                    </style>
                </head>
                <body>
                    <h1>Super Idol 健康管理系統</h1>
                    <div class="card">
                        <h2>API 服務正常運行</h2>
                        <p>後端系統已成功啟動，但找不到前端靜態文件。</p>
                        <p>這是自動生成的應急頁面。您可以訪問以下端點：</p>
                        <ul>
                            <li><a href="/api/auth/register">用戶註冊</a></li>
                            <li><a href="/api/auth/login">用戶登入</a></li>
                            <li><a href="/api/food">飲食記錄</a></li>
                            <li><a href="/api/exercise">運動記錄</a></li>
                            <li><a href="/api/report">健康報告</a></li>
                        </ul>
                        <div class="center">
                            <a href="/api/debug/static-info" class="btn">查看系統狀態</a>
                        </div>
                    </div>
                    <div class="card">
                        <h3>開發資訊</h3>
                        <p>要完整部署前端，請將 frontend 目錄添加到 Git 倉庫中。</p>
                        <p>或者可以使用 Render.com 上的靜態網站服務單獨部署前端。</p>
                    </div>
                </body>
                </html>
                ''')
            
            logger.info(f"成功創建測試頁面: {index_html}")
            found_path = static_dir
        except Exception as e:
            logger.error(f"創建靜態目錄或測試頁面失敗: {str(e)}")
            return None
    
    # 嘗試複製前端文件到後端靜態目錄(如果需要)
    if found_path == os.path.join(project_dir, 'frontend', 'dist'):
        static_dir = os.path.join(backend_dir, 'static')
        try:
            # 確保後端靜態目錄存在
            os.makedirs(static_dir, exist_ok=True)
            
            # 只在後端靜態目錄不包含index.html時進行複製
            if not os.path.exists(os.path.join(static_dir, 'index.html')):
                logger.info(f"複製前端文件到後端靜態目錄: {found_path} -> {static_dir}")
                
                # 清理目標目錄
                for item in os.listdir(static_dir):
                    item_path = os.path.join(static_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except Exception as e:
                        logger.warning(f"清理文件失敗: {item_path}, 錯誤: {str(e)}")
                
                # 複製文件
                for item in os.listdir(found_path):
                    s = os.path.join(found_path, item)
                    d = os.path.join(static_dir, item)
                    if os.path.isfile(s):
                        shutil.copy2(s, d)
                    else:
                        shutil.copytree(s, d)
                
                logger.info(f"複製完成，後端靜態目錄現在包含: {os.listdir(static_dir)}")
                found_path = static_dir
        except Exception as e:
            logger.error(f"複製前端文件到後端靜態目錄失敗: {str(e)}")
            # 繼續使用前端目錄
    
    return found_path

# 創建Flask應用
from app import create_app

# 獲取應用實例
app = create_app()

# 添加詳細的API請求日誌記錄
@app.before_request
def log_request_info():
    import logging
    from flask import request
    
    if '/api/' in request.path:
        logging.info(f"API請求: {request.method} {request.path}")
        if request.args:
            logging.info(f"查詢參數: {dict(request.args)}")
        if request.content_type and 'application/json' in request.content_type:
            try:
                logging.info(f"請求體(JSON): {request.get_json()}")
            except:
                logging.warning(f"無法解析JSON請求體")
        logging.info(f"請求頭: {dict(request.headers)}")

@app.after_request
def log_response_info(response):
    import logging
    from flask import request
    
    if '/api/' in request.path:
        logging.info(f"API響應: {response.status_code} {response.status}")
        logging.info(f"響應頭: {dict(response.headers)}")
        if response.content_type and 'application/json' in response.content_type:
            try:
                # 嘗試讀取並記錄響應內容，但不修改原始響應
                response_data = response.get_data()
                logging.info(f"響應體(JSON): {response_data.decode('utf-8')}")
            except:
                logging.warning("無法解析JSON響應體")
    return response

# 設置靜態文件目錄
static_folder = find_static_directory()
if static_folder:
    app.static_folder = static_folder
    logger.info(f"設置靜態目錄為: {static_folder}")
else:
    logger.error("無法找到或創建有效的靜態文件目錄！")

# 調試端點
@app.route('/api/debug/static-info')
def static_info():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(backend_dir)
    
    # 檢查可能的靜態目錄
    paths_info = {}
    for path in [
        os.path.join(project_dir, 'frontend', 'dist'),
        os.path.join(backend_dir, 'static')
    ]:
        try:
            exists = os.path.exists(path)
            files = []
            if exists:
                files = [os.path.basename(f) for f in glob.glob(os.path.join(path, '*'))]
            paths_info[path] = {
                'exists': exists,
                'files': files,
                'has_index_html': 'index.html' in files
            }
        except Exception as e:
            paths_info[path] = {'error': str(e)}
    
    # 安全過濾環境變數
    env_vars = {}
    for k, v in os.environ.items():
        if not any(s in k.lower() for s in ['secret', 'password', 'key']):
            env_vars[k] = v
    
    # 收集Flask配置（過濾敏感信息）
    flask_config = {}
    for k, v in app.config.items():
        if not any(s in k.upper() for s in ['SECRET', 'PASSWORD', 'KEY']):
            flask_config[k] = str(v)
    
    # 系統信息
    import sys
    import platform
    
    return jsonify({
        'app_static_folder': app.static_folder,
        'static_paths': paths_info,
        'environment': os.getenv('FLASK_ENV', 'development'),
        'database_host': app.config.get('MYSQL_HOST', 'not_set'),
        'safe_environment_variables': env_vars,
        'flask_config': flask_config,
        'python_version': sys.version,
        'platform': platform.platform(),
        'working_directory': os.getcwd(),
        'render_env': os.environ.get('RENDER') == 'true',
        'file_path': __file__,
        'render_build_directory': os.environ.get('RENDER_BUILD_DIR', 'not_set')
    })

# 前端路由處理
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    logger.info(f"請求路徑: {path}")
    
    if path.startswith('api/'):
        # API請求由Flask處理
        logger.info("API請求路徑，返回404")
        return app.response_class(status=404)
    
    if path and path != '' and not path.startswith('api'):
        # 嘗試從靜態文件夾提供文件
        logger.info(f"嘗試提供靜態文件: {path}")
        try:
            full_path = os.path.join(app.static_folder, path)
            logger.info(f"檢查文件是否存在: {full_path}")
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return send_from_directory(app.static_folder, path)
            logger.warning(f"文件不存在: {full_path}")
        except Exception as e:
            logger.error(f"提供靜態文件出錯: {str(e)}")
    
    # 默認返回index.html
    logger.info(f"嘗試返回index.html，從目錄: {app.static_folder}")
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        logger.error(f"提供index.html出錯: {str(e)}")
        return f"錯誤: 無法加載前端應用。詳細信息: {str(e)}", 500

# 提供備用首頁
@app.route('/app-status')
def app_status():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(backend_dir)
    
    # 檢查各種路徑
    paths = [
        ('前端構建目錄', os.path.join(project_dir, 'frontend', 'dist')),
        ('後端靜態目錄', os.path.join(backend_dir, 'static')),
        ('Flask 靜態目錄', app.static_folder)
    ]
    
    path_info = []
    for name, path in paths:
        exists = os.path.exists(path)
        has_index = exists and os.path.exists(os.path.join(path, 'index.html'))
        path_info.append(f"{name}: {path} (存在: {exists}, 包含index.html: {has_index})")
    
    return f"""
    <html>
    <head>
        <title>Super Idol 應用狀態</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333; }}
            pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Super Idol API服務正在運行</h1>
        <p>API路由可用，但前端靜態文件可能有問題。</p>
        <h2>路徑信息:</h2>
        <pre>{chr(10).join(path_info)}</pre>
        <p>詳細診斷: <a href="/api/debug/static-info">/api/debug/static-info</a></p>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 