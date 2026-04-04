"""
Configuration settings for the application.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = False
    
    # Database settings
    MYSQL_HOST = os.getenv('DB_HOST', 'superidol.c9i82eygu8mk.ap-southeast-2.rds.amazonaws.com')
    MYSQL_PORT = int(os.getenv('DB_PORT', '3306'))
    MYSQL_USER = os.getenv('DB_USER', 'DBMS11302')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'ilovedbms')
    MYSQL_DB = os.getenv('DB_NAME', 'superidol')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-please-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_TOKEN_EXPIRE', '3600'))  # 1 hour
    
    # API settings
    API_TITLE = 'Super Idol API'
    API_VERSION = 'v1'
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://super-idol.onrender.com').split(',')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # 開發環境 CORS 設置 - 添加前端開發伺服器地址
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173').split(',')

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    MYSQL_DB = 'super_idol_test_db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # 從環境變數獲取所有生產環境配置
    # 提供更安全的默認值，以防環境變數未設置
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        import logging
        logging.warning("WARNING: No SECRET_KEY set for production environment! Using a default value, but this is not secure.")
        SECRET_KEY = 'render-production-default-key-change-me'
    
    # JWT 設置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        import logging
        logging.warning("WARNING: No JWT_SECRET_KEY set for production environment! Using a default value, but this is not secure.")
        JWT_SECRET_KEY = 'render-production-default-jwt-key-change-me'
    
    # 資料庫設置 - 必須從環境變數獲取
    MYSQL_HOST = os.getenv('DB_HOST')
    MYSQL_PORT = int(os.getenv('DB_PORT', '3306'))
    MYSQL_USER = os.getenv('DB_USER')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD')
    MYSQL_DB = os.getenv('DB_NAME')
    
    # 檢查必要的資料庫設置，但提供錯誤處理而不是直接崩潰
    if not all([MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB]):
        import logging
        logging.error("Database configuration incomplete. Some environment variables are missing.")
        # 使用父類的默認值
        if not MYSQL_HOST:
            MYSQL_HOST = Config.MYSQL_HOST
            logging.warning(f"Using default DB_HOST: {MYSQL_HOST}")
        if not MYSQL_USER:
            MYSQL_USER = Config.MYSQL_USER
            logging.warning(f"Using default DB_USER: {MYSQL_USER}")
        if not MYSQL_PASSWORD:
            MYSQL_PASSWORD = Config.MYSQL_PASSWORD
            logging.warning(f"Using default DB_PASSWORD: [HIDDEN]")
        if not MYSQL_DB:
            MYSQL_DB = Config.MYSQL_DB
            logging.warning(f"Using default DB_NAME: {MYSQL_DB}")
    
    # 生產環境 CORS 設置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://super-idol.onrender.com').split(',') 