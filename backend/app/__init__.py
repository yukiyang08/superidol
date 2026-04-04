"""
Initialization file for the Flask application.
"""

import logging
import os

from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: rule.rule.startswith("/api/"),
            "model_filter": lambda tag: True,
        }
    ],
    "swagger_ui": True,
    "specs_route": "/swagger/",
}


def create_app():
    # 根據環境選擇正確的配置
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        from app.config import ProductionConfig as AppConfig

        logging.info("使用生產環境配置")
    elif env == "testing":
        from app.config import TestingConfig as AppConfig

        logging.info("使用測試環境配置")
    else:
        from app.config import DevelopmentConfig as AppConfig

        logging.info("使用開發環境配置")

    app = Flask(__name__, static_url_path="/app-static")
    app.config.from_object(AppConfig)

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "SuperIdol API",
            "description": "Backend API documentation for SuperIdol.",
            "version": "1.0.0",
        },
        "basePath": "/",
        "schemes": ["http", "https"],
    }
    Swagger(app, template=swagger_template, config=swagger_config)

    # 配置日誌級別 - 設為DEBUG以便排錯
    log_level = os.getenv("LOG_LEVEL", "DEBUG")
    logging.basicConfig(level=getattr(logging, log_level))

    # 設置 CORS：以 config.py 的 CORS_ORIGINS 為準（可由環境變數覆蓋）
    CORS(app, origins=app.config.get("CORS_ORIGINS", []), supports_credentials=True)

    # 記錄每個請求的CORS信息
    @app.after_request
    def log_cors_headers(response):
        logging.debug(f"CORS Headers: {dict(response.headers)}")
        return response

    # 添加一個測試端點
    @app.route("/api/test-cors", methods=["GET", "OPTIONS"])
    def test_cors():
        """
        CORS 測試端點
        ---
        tags:
          - System
        responses:
          200:
            description: CORS test passed
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                message:
                  type: string
                  example: CORS test passed
        """
        return jsonify({"status": "success", "message": "CORS test passed"})

    # 註冊藍圖
    from app.api import auth_bp, exercise_bp, food_bp, my_favorite_bp, preferences_bp, report_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(food_bp, url_prefix="/api/food")
    app.register_blueprint(exercise_bp, url_prefix="/api/exercise")
    app.register_blueprint(preferences_bp, url_prefix="/api/preferences")
    app.register_blueprint(my_favorite_bp, url_prefix="/api/myfavorite")
    app.register_blueprint(report_bp, url_prefix="/api/reports")

    # 記錄應用啟動信息
    logging.info(f"Flask應用已啟動，環境: {env}")
    logging.info(f"數據庫連接: {app.config.get('MYSQL_HOST')}:{app.config.get('MYSQL_PORT')}")
    logging.info(f"CORS設置: 允許來源 {app.config.get('CORS_ORIGINS')}")

    return app