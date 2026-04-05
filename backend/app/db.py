"""
檔案：db.py
用途：資料庫連接與操作工具（Supabase / PostgreSQL via psycopg v3）
"""

import psycopg
from psycopg import pq
import os
import sys
import threading
import queue
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from config import Config


# ---------------------------------------------------------------------------
# CIDict：大小寫不敏感 dict，讓舊有 row["UserID"] 等查詢繼續有效
# ---------------------------------------------------------------------------
class CIDict(dict):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            lk = key.lower()
            for k in self:
                if k.lower() == lk:
                    return super().__getitem__(k)
            raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        if super().__contains__(key):
            return True
        lk = key.lower()
        return any(k.lower() == lk for k in self)


def ci_dict_row(cursor):
    if cursor.description is None:
        return lambda values: values
    columns = [col.name for col in cursor.description]
    def make_row(values):
        return CIDict(zip(columns, values))
    return make_row


# ---------------------------------------------------------------------------
# 連接池
# ---------------------------------------------------------------------------
class SimpleConnectionPool:
    def __init__(self, max_connections=10, max_idle_time=300):
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()

    def get_connection(self):
        try:
            conn, last_used = self.pool.get_nowait()
            if time.time() - last_used > self.max_idle_time:
                try:
                    conn.close()
                except Exception:
                    pass
                return self._create_new_connection()
            try:
                conn.execute("SELECT 1")
                conn.rollback()
                return conn
            except Exception:
                return self._create_new_connection()
        except queue.Empty:
            return self._create_new_connection()

    def _create_new_connection(self):
        with self.lock:
            if self.active_connections >= self.max_connections:
                return self._new_connection()
            self.active_connections += 1
            return self._new_connection()

    def _new_connection(self):
        return psycopg.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            dbname=Config.MYSQL_DB,
            sslmode='require',
            row_factory=ci_dict_row,
        )

    def return_connection(self, conn):
        try:
            if conn.info.transaction_status != pq.TransactionStatus.IDLE:
                conn.rollback()
            if self.pool.qsize() < self.max_connections:
                self.pool.put((conn, time.time()), block=False)
            else:
                conn.close()
                with self.lock:
                    self.active_connections -= 1
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            with self.lock:
                self.active_connections -= 1


_connection_pool = SimpleConnectionPool()


def get_db_connection():
    try:
        return _connection_pool.get_connection()
    except Exception as e:
        print(f"資料庫連接失敗: {e}")
        try:
            return psycopg.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                dbname=Config.MYSQL_DB,
                sslmode='require',
                row_factory=ci_dict_row,
            )
        except Exception as fallback_e:
            print(f"降級連接也失敗: {fallback_e}")
            raise


def return_db_connection(conn):
    try:
        _connection_pool.return_connection(conn)
    except Exception:
        try:
            conn.close()
        except Exception:
            pass


def execute_query(query, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
        return result
    finally:
        return_db_connection(conn)


def execute_update(query, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount
        conn.commit()
        return affected_rows
    except Exception as e:
        conn.rollback()
        print(f"執行更新操作失敗: {e}")
        raise
    finally:
        return_db_connection(conn)


def execute_transaction(queries_and_params):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for query, params in queries_and_params:
                cursor.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"執行事務失敗: {e}")
        raise
    finally:
        return_db_connection(conn)
