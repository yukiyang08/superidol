from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from typing import Generator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if not os.path.exists(env_path):
    logger.warning(f".env file not found at {env_path}")
load_dotenv(env_path)
#ssd
#ssd12
# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")  # Default MySQL port
DB_NAME = "superidol"  # 修改為正確的資料庫名稱!

# Validate required environment variables
required_vars = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Create database URL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    # Create engine with connection pooling
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=True  # Enable SQL query logging for debugging
    )
    
    # Test the connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        logger.info("Successfully connected to the database")
except Exception as e:
    logger.error(f"Failed to connect to the database: {str(e)}")
    raise

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Generator:
    """
    Get a database session.
    
    Yields:
        Session: A SQLAlchemy database session
        
    Example:
        ```python
        db = next(get_db())
        try:
            # Use the database session
            result = db.query(User).all()
        finally:
            db.close()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()

# 測試連接（當直接執行此檔案時）ss
if __name__ == "__main__":
    print("Testing database connection...")
    try:
        # 測試 engine 連接
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(" Engine connection successful!")
        
        # 測試 session 連接
        db = next(get_db())
        try:
            result = db.execute(text("SELECT 1"))
            print("✓ Session connection successful!")
        finally:
            db.close()
        
        print("\nAll connection tests passed! 🎉")
    except Exception as e:
        print(f"\nConnection test failed: {str(e)}")
        raise 
    #測試