"""
檔案：db.py
用途：資料庫連接與操作工具
"""

import pymysql
import os
import sys
import threading
import queue
import time

# 直接從檔案中導入 Config 類
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from config import Config

# 簡單的連接池實現
class SimpleConnectionPool:
    def __init__(self, max_connections=10, max_idle_time=300):
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        
    def get_connection(self):
        """從連接池獲取連接"""
        try:
            # 嘗試從池中獲取連接
            conn_info = self.pool.get_nowait()
            conn, last_used = conn_info
            
            # 檢查連接是否仍然有效
            if time.time() - last_used > self.max_idle_time:
                try:
                    conn.close()
                except:
                    pass
                return self._create_new_connection()
            
            # 測試連接是否有效
            try:
                conn.ping(reconnect=True)
                return conn
            except:
                return self._create_new_connection()
                
        except queue.Empty:
            return self._create_new_connection()
    
    def _create_new_connection(self):
        """創建新的資料庫連接"""
        with self.lock:
            if self.active_connections >= self.max_connections:
                # 如果達到最大連接數，直接創建臨時連接
                return self._new_connection()
            
            self.active_connections += 1
            return self._new_connection()
    
    def _new_connection(self):
        """創建新連接的實際方法"""
        return pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            db=Config.MYSQL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    
    def return_connection(self, conn):
        """將連接返回到連接池"""
        try:
            if self.pool.qsize() < self.max_connections:
                self.pool.put((conn, time.time()), block=False)
            else:
                conn.close()
                with self.lock:
                    self.active_connections -= 1
        except:
            conn.close()
            with self.lock:
                self.active_connections -= 1

# 全局連接池實例
_connection_pool = SimpleConnectionPool()

def get_db_connection():
    """
    獲取資料庫連接（使用連接池優化）
    
    Returns:
        pymysql.connections.Connection: 資料庫連接對象
    """
    try:
        return _connection_pool.get_connection()
    except Exception as e:
        print(f"資料庫連接失敗: {str(e)}")
        # 降級到直接連接
        try:
            return pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                db=Config.MYSQL_DB,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as fallback_e:
            print(f"降級連接也失敗: {str(fallback_e)}")
            raise

def return_db_connection(conn):
    """
    將連接返回到連接池
    
    Args:
        conn: 資料庫連接對象
    """
    try:
        _connection_pool.return_connection(conn)
    except:
        try:
            conn.close()
        except:
            pass

def execute_query(query, params=None):
    """
    執行資料查詢操作（使用連接池優化）
    
    Args:
        query (str): SQL 查詢語句
        params (tuple, optional): 查詢參數
        
    Returns:
        list: 查詢結果
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
        return result
    finally:
        return_db_connection(conn)

def execute_update(query, params=None):
    """
    執行資料更新操作（INSERT, UPDATE, DELETE）（使用連接池優化）
    
    Args:
        query (str): SQL 更新語句
        params (tuple, optional): 更新參數
        
    Returns:
        int: 受影響的行數
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            affected_rows = cursor.execute(query, params or ())
        conn.commit()
        return affected_rows
    except Exception as e:
        conn.rollback()
        print(f"執行更新操作失敗: {str(e)}")
        raise
    finally:
        return_db_connection(conn)

def execute_transaction(queries_and_params):
    """
    在單一事務中執行多個操作（使用連接池優化）
    
    Args:
        queries_and_params (list): 包含 (query, params) 元組的列表
        
    Returns:
        bool: 事務是否成功執行
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for query, params in queries_and_params:
                cursor.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"執行事務失敗: {str(e)}")
        raise
    finally:
        return_db_connection(conn) 
        