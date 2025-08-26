"""
Redis 快取配置模組
用於提升 FoodSearch 的查詢效能
"""

import redis
import json
import hashlib
import time
from typing import Any, Optional, Dict, List
from functools import wraps
import logging

# 配置 Redis 連接
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'decode_responses': True,
    'socket_connect_timeout': 5,
    'socket_timeout': 5,
    'retry_on_timeout': True,
    'health_check_interval': 30
}

class RedisCache:
    """Redis 快取管理類"""
    
    def __init__(self, config: Dict = None):
        self.config = config or REDIS_CONFIG
        self.redis_client = None
        self.is_connected = False
        self._connect()
    
    def _connect(self):
        """連接到 Redis"""
        try:
            self.redis_client = redis.Redis(**self.config)
            # 測試連接
            self.redis_client.ping()
            self.is_connected = True
            logging.info("Redis 連接成功")
        except Exception as e:
            logging.warning(f"Redis 連接失敗: {e}")
            self.is_connected = False
    
    def _reconnect(self):
        """重新連接 Redis"""
        try:
            if self.redis_client:
                self.redis_client.close()
            self._connect()
        except Exception as e:
            logging.error(f"Redis 重新連接失敗: {e}")
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """生成快取鍵"""
        if isinstance(data, dict):
            # 排序鍵值對以確保一致性
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)
        
        # 使用 MD5 生成固定長度的鍵
        hash_obj = hashlib.md5(sorted_data.encode('utf-8'))
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """獲取快取值"""
        if not self.is_connected:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logging.error(f"Redis 獲取失敗: {e}")
            self._reconnect()
            return None
    
    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """設置快取值"""
        if not self.is_connected:
            return False
        
        try:
            serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            return self.redis_client.setex(key, expire, serialized_value)
        except Exception as e:
            logging.error(f"Redis 設置失敗: {e}")
            self._reconnect()
            return False
    
    def delete(self, key: str) -> bool:
        """刪除快取值"""
        if not self.is_connected:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logging.error(f"Redis 刪除失敗: {e}")
            self._reconnect()
            return False
    
    def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        if not self.is_connected:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logging.error(f"Redis 檢查鍵失敗: {e}")
            self._reconnect()
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """清除符合模式的鍵"""
        if not self.is_connected:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logging.error(f"Redis 清除模式失敗: {e}")
            self._reconnect()
            return 0

# 全局 Redis 實例
redis_cache = RedisCache()

def cache_result(prefix: str, expire: int = 300):
    """
    快取裝飾器
    :param prefix: 快取鍵前綴
    :param expire: 過期時間（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成快取鍵
            cache_key = redis_cache._generate_key(prefix, {
                'args': args,
                'kwargs': kwargs
            })
            
            # 嘗試從快取獲取
            cached_result = redis_cache.get(cache_key)
            if cached_result is not None:
                logging.info(f"快取命中: {cache_key}")
                return cached_result
            
            # 執行函數
            result = func(*args, **kwargs)
            
            # 儲存到快取
            if result is not None:
                redis_cache.set(cache_key, result, expire)
                logging.info(f"快取儲存: {cache_key}")
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """清除指定模式的快取"""
    return redis_cache.clear_pattern(pattern)

# 快取鍵常量
CACHE_KEYS = {
    'FOOD_SEARCH': 'food:search',
    'FOOD_RECOMMEND': 'food:recommend',
    'FOOD_TYPES': 'food:types',
    'RESTAURANTS': 'restaurants:list',
    'USER_PREFERENCES': 'user:preferences'
}

# 使用範例
@cache_result(CACHE_KEYS['FOOD_SEARCH'], expire=600)
def cached_food_search(filters: Dict) -> List[Dict]:
    """
    快取的食物搜尋函數
    這個函數會被裝飾器自動快取結果
    """
    # 實際的搜尋邏輯會在這裡實作
    pass

# 快取管理函數
def clear_food_search_cache():
    """清除食物搜尋快取"""
    return invalidate_cache_pattern(f"{CACHE_KEYS['FOOD_SEARCH']}:*")

def clear_user_cache(user_id: int):
    """清除特定用戶的快取"""
    patterns = [
        f"{CACHE_KEYS['USER_PREFERENCES']}:{user_id}:*",
        f"{CACHE_KEYS['FOOD_RECOMMEND']}:{user_id}:*"
    ]
    for pattern in patterns:
        invalidate_cache_pattern(pattern)

def get_cache_stats() -> Dict:
    """獲取快取統計資訊"""
    if not redis_cache.is_connected:
        return {"status": "disconnected"}
    
    try:
        info = redis_cache.redis_client.info()
        return {
            "status": "connected",
            "used_memory": info.get('used_memory_human', 'N/A'),
            "connected_clients": info.get('connected_clients', 0),
            "total_commands_processed": info.get('total_commands_processed', 0),
            "keyspace_hits": info.get('keyspace_hits', 0),
            "keyspace_misses": info.get('keyspace_misses', 0)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)} 