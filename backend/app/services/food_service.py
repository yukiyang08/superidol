"""食物服務模塊"""
from typing import Optional, List, Any, Tuple
from datetime import datetime
from ..database.models import FoodItem
from ..extensions import db
from ..schemas.food_item import FoodItemCreate, FoodItemUpdate
from app.db import get_db_connection, return_db_connection
import logging
import decimal
import functools


OPTIONAL_FOOD_RECORD_COLUMNS = {
    'photourl': 'photourl',
    'photopath': 'photopath',
    'photomimetype': 'photomimetype',
    'estimatedname': 'estimatedname',
    'estimatedcalories': 'estimatedcalories',
    'estimationprovider': 'estimationprovider',
    'estimationconfidence': 'estimationconfidence',
    'estimationnotes': 'estimationnotes',
    'estimatedprotein': 'estimatedprotein',
    'estimatedfat': 'estimatedfat',
    'estimatedcarb': 'estimatedcarb',
    'estimatedsugar': 'estimatedsugar',
    'estimatedsodium': 'estimatedsodium',
}

class FoodService:
    @staticmethod
    def get_food_by_id(food_id: int) -> Optional[FoodItem]:
        """根據 ID 獲取食物"""
        return FoodItem.query.get(food_id)

    @staticmethod
    def get_foods() -> List[FoodItem]:
        """獲取所有食物"""
        return FoodItem.query.all()

    @staticmethod
    def create_food(food_data: FoodItemCreate) -> FoodItem:
        """創建新食物"""
        food = FoodItem(**food_data.dict())
        db.session.add(food)
        db.session.commit()
        return food

    @staticmethod
    def update_food(food: FoodItem, food_data: FoodItemUpdate) -> FoodItem:
        """更新食物信息"""
        for key, value in food_data.dict(exclude_unset=True).items():
            setattr(food, key, value)
        food.updated_at = datetime.utcnow()
        db.session.commit()
        return food

    @staticmethod
    def delete_food(food: FoodItem) -> None:
        """刪除食物"""
        db.session.delete(food)
        db.session.commit()

def filters_to_tuple(filters: dict) -> Tuple[Tuple[str, Any], ...]:
    """
    將 dict 轉為可 hash 的 tuple，作為 lru_cache key。
    會自動將 type 轉 food_type，並排序 key。
    list 會自動轉 tuple。
    """
    filters = dict(filters)  # 複製避免副作用
    if 'type' in filters:
        filters['food_type'] = filters.pop('type')
    # 將所有 list 轉 tuple
    for k, v in filters.items():
        if isinstance(v, list):
            filters[k] = tuple(v)
    return tuple(sorted(filters.items()))

@functools.lru_cache(maxsize=512)  # 進一步增加快取大小
def cached_search_food(filters_tuple: Tuple[Tuple[str, Any], ...]):
    """
    lru_cache 包裝的 search_food，filters_tuple 需為 tuple。
    為精準推薦優化的快取系統。
    """
    # 還原 dict
    filters = dict(filters_tuple)
    return search_food(filters)

# 針對小數量精準推薦的特殊快取
@functools.lru_cache(maxsize=128)
def cached_search_food_precise(filters_tuple: Tuple[Tuple[str, Any], ...], limit: int = 50):
    """
    精準推薦專用的搜尋函數，限制返回數量以提高精準度
    """
    filters = dict(filters_tuple)
    results = search_food(filters)
    return results[:limit]  # 限制返回數量

def search_food(filters):
    """
    搜尋符合條件的食物清單（優化版本）
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 基本查詢 - 添加 LIMIT 以提升性能
        sql = """
            SELECT f.FoodID, f.Name, f.Calories, f.Price, f.Food_Type, f.Set_Type, f.ImageUrl, 
                   f.Protein, f.Fat, f.Sugar, f.Sodium, f.Carb, f.Caffeine, 
                   r.Name AS Restaurant
            FROM Food f
            LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
            WHERE 1 = 1
        """
        params = []

        # 優化過濾條件 - 使用更高效的查詢方式
        # priceMin
        if filters.get('priceMin') is not None:
            price_min = filters['priceMin']
            if isinstance(price_min, (int, float, decimal.Decimal)):
                sql += " AND (f.Price IS NULL OR f.Price >= %s)"
                params.append(float(price_min))
            elif isinstance(price_min, str) and price_min.strip():
                sql += " AND (f.Price IS NULL OR f.Price >= %s)"
                params.append(float(price_min.strip()))
        
        # priceMax
        if filters.get('priceMax') is not None:
            price_max = filters['priceMax']
            if isinstance(price_max, (int, float, decimal.Decimal)):
                sql += " AND (f.Price IS NULL OR f.Price <= %s)"
                params.append(float(price_max))
            elif isinstance(price_max, str) and price_max.strip():
                sql += " AND (f.Price IS NULL OR f.Price <= %s)"
                params.append(float(price_max.strip()))
        
        # calMin
        if filters.get('calMin') is not None:
            cal_min = filters['calMin']
            if isinstance(cal_min, (int, float, decimal.Decimal)):
                sql += " AND (f.Calories IS NULL OR f.Calories >= %s)"
                params.append(float(cal_min))
            elif isinstance(cal_min, str) and cal_min.strip():
                sql += " AND (f.Calories IS NULL OR f.Calories >= %s)"
                params.append(float(cal_min.strip()))
        
        # calMax
        if filters.get('calMax') is not None:
            cal_max = filters['calMax']
            if isinstance(cal_max, (int, float, decimal.Decimal)):
                sql += " AND (f.Calories IS NULL OR f.Calories <= %s)"
                params.append(float(cal_max))
            elif isinstance(cal_max, str) and cal_max.strip():
                sql += " AND (f.Calories IS NULL OR f.Calories <= %s)"
                params.append(float(cal_max.strip()))
        
        # name - 使用索引友好的查詢
        if filters.get('name') is not None:
            name = filters['name']
            if isinstance(name, str) and name.strip():
                sql += " AND f.Name LIKE %s"
                params.append(f"%{name.strip()}%")
        
        # restaurant - 優化多選查詢
        if filters.get('restaurant') is not None:
            restaurant = filters['restaurant']
            if isinstance(restaurant, str) and restaurant.strip():
                # 支援多選：逗號分隔
                names = [n.strip() for n in restaurant.split(',') if n.strip()]
                if len(names) == 1:
                    sql += " AND r.Name LIKE %s"
                    params.append(f"%{names[0]}%")
                elif len(names) > 1:
                    placeholders = ','.join(['%s'] * len(names))
                    sql += f" AND r.Name IN ({placeholders})"
                    params.extend(names)
        
        # food_type - 優化多選查詢
        if filters.get('food_type') is not None:
            food_type = filters['food_type']
            if isinstance(food_type, str) and food_type.strip():
                types = [t.strip() for t in food_type.split(',') if t.strip()]
                if len(types) == 1:
                    sql += " AND f.Food_Type LIKE %s"
                    params.append(f"%{types[0]}%")
                elif len(types) > 1:
                    placeholders = ','.join(['%s'] * len(types))
                    sql += f" AND f.Food_Type IN ({placeholders})"
                    params.extend(types)

        # 添加排序和限制以提升性能
        sql += " ORDER BY f.FoodID LIMIT 500"  # 限制返回結果數量

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # 將資料庫結果轉換為 JSON 格式（優化版本）
        results = []
        for row in rows:
            results.append({
                'id': row['FoodID'],
                'name': row['Name'],
                'calories': row['Calories'],
                'price': row['Price'],
                'food_type': row['Food_Type'],
                'type': row['Set_Type'],
                'restaurant': row['Restaurant'],
                'ImageUrl': row.get('ImageUrl'),
                'Protein': row.get('Protein'),
                'Fat': row.get('Fat'),
                'Sugar': row.get('Sugar'),
                'Sodium': row.get('Sodium'),
                'Carb': row.get('Carb'),
                'Caffeine': row.get('Caffeine')
            })
        
        return results
    except Exception as e:
        import traceback
        logging.error(f"search_food SQL error: {e}\n{traceback.format_exc()}")
        raise Exception(f"Database error: {str(e)}")
    finally:
        cursor.close()
        return_db_connection(conn)


def get_food_record_available_columns(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND lower(table_name) = 'food_records'
            """
        )
        return {row['column_name'].lower() for row in cursor.fetchall()}

def add_food_record(user_id, food_data):
    """
    添加食物消費記錄
    Args:
        user_id (int): 用戶ID
        food_data (dict): 包含 food_id, mealtime, quantity, date, 以及 custom 欄位
    Returns:
        dict: 包含操作結果和新增記錄的ID
    """
    conn = get_db_connection()

    def _normalize_int(value, field_name, allow_none=False):
        if value is None:
            if allow_none:
                return None
            raise ValueError(f"{field_name} is required")
        if isinstance(value, str) and not value.strip():
            if allow_none:
                return None
            raise ValueError(f"{field_name} is required")
        try:
            return int(float(value))
        except (TypeError, ValueError):
            raise ValueError(f"Invalid {field_name}")

    def _normalize_float(value, field_name, allow_none=False):
        if value is None:
            if allow_none:
                return None
            raise ValueError(f"{field_name} is required")
        if isinstance(value, str) and not value.strip():
            if allow_none:
                return None
            raise ValueError(f"{field_name} is required")
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid {field_name}")

    try:
        food_id = food_data.get('food_id')
        mealtime = food_data.get('mealtime')
        quantity = _normalize_int(food_data.get('quantity', 1), 'quantity')
        date = food_data.get('date')
        # 新增自訂欄位
        custom_name = food_data.get('custom_name')
        custom_calories = _normalize_int(food_data.get('custom_calories'), 'custom_calories', allow_none=True)
        custom_type = food_data.get('custom_type')
        custom_price = _normalize_float(food_data.get('custom_price'), 'custom_price', allow_none=True)
        custom_restaurant = food_data.get('custom_restaurant')
        optional_columns = get_food_record_available_columns(conn)
        optional_values = {
            'photourl': food_data.get('photo_url'),
            'photopath': food_data.get('photo_path'),
            'photomimetype': food_data.get('photo_mime_type'),
            'estimatedname': food_data.get('estimated_name'),
            'estimatedcalories': _normalize_int(food_data.get('estimated_calories'), 'estimated_calories', allow_none=True),
            'estimationprovider': food_data.get('estimation_provider'),
            'estimationconfidence': _normalize_float(food_data.get('estimation_confidence'), 'estimation_confidence', allow_none=True),
            'estimationnotes': food_data.get('estimation_notes'),
            'estimatedprotein': _normalize_float(food_data.get('estimated_protein'), 'estimated_protein', allow_none=True),
            'estimatedfat': _normalize_float(food_data.get('estimated_fat'), 'estimated_fat', allow_none=True),
            'estimatedcarb': _normalize_float(food_data.get('estimated_carb'), 'estimated_carb', allow_none=True),
            'estimatedsugar': _normalize_float(food_data.get('estimated_sugar'), 'estimated_sugar', allow_none=True),
            'estimatedsodium': _normalize_float(food_data.get('estimated_sodium'), 'estimated_sodium', allow_none=True),
        }
        supported_optional_values = {
            column: value
            for key, column in OPTIONAL_FOOD_RECORD_COLUMNS.items()
            if key in optional_columns and (value := optional_values[column]) is not None
        }
        # 驗證必要參數
        if not all([mealtime, date, quantity]):
            raise ValueError("Missing required fields: mealtime, date, quantity")
        # 檢查用戶是否存在
        with conn.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
        # 判斷是自訂還是關聯食物
        if food_id:
            # 檢查食物是否存在
            with conn.cursor() as cursor:
                cursor.execute("SELECT FoodID FROM Food WHERE FoodID = %s", (food_id,))
                food = cursor.fetchone()
                if not food:
                    raise ValueError(f"Food with ID {food_id} not found")
            # 插入關聯食物
            with conn.cursor() as cursor:
                columns = ['UserID', 'FoodID', 'Mealtime', 'Quantity', 'Date', *supported_optional_values.keys()]
                placeholders = ', '.join(['%s'] * len(columns))
                values = [user_id, food_id, mealtime, quantity, date, *supported_optional_values.values()]
                sql = f"INSERT INTO Food_Records ({', '.join(columns)}) VALUES ({placeholders}) RETURNING RecordID"
                cursor.execute(sql, values)
                record_id = cursor.fetchone()['RecordID']
                conn.commit()
                return {
                    "record_id": record_id,
                    "message": "Food record added successfully"
                }
        else:
            # 自訂食物必填 custom 欄位
            if not all([custom_name, custom_calories]):
                raise ValueError("Custom food must have name and calories")
            with conn.cursor() as cursor:
                columns = [
                    'UserID', 'FoodID', 'CustomName', 'CustomCalories', 'CustomType',
                    'CustomPrice', 'CustomRestaurant', 'Mealtime', 'Quantity', 'Date',
                    *supported_optional_values.keys()
                ]
                placeholders = ', '.join(['%s'] * len(columns))
                values = [
                    user_id, None, custom_name, custom_calories, custom_type,
                    custom_price, custom_restaurant, mealtime, quantity, date,
                    *supported_optional_values.values()
                ]
                sql = f"INSERT INTO Food_Records ({', '.join(columns)}) VALUES ({placeholders}) RETURNING RecordID"
                cursor.execute(sql, values)
                record_id = cursor.fetchone()['RecordID']
                conn.commit()
                return {
                    "record_id": record_id,
                    "message": "Custom food record added successfully"
                }
    except Exception as e:
        conn.rollback()
        if isinstance(e, ValueError):
            raise
        raise Exception(f"Error adding food record: {str(e)}")
    finally:
        conn.close()

def get_user_food_records(user_id, start_date=None, end_date=None, mealtime=None):
    """
    獲取用戶的食物記錄
    Args:
        user_id (int): 用戶ID
        start_date (str, optional): 開始日期 (YYYY-MM-DD)
        end_date (str, optional): 結束日期 (YYYY-MM-DD)
        mealtime (str, optional): 餐點類型篩選 (早餐、午餐、晚餐、宵夜)
    Returns:
        list: 食物記錄列表
    """
    conn = get_db_connection()
    try:
        available_columns = get_food_record_available_columns(conn)
        optional_selects = []
        if 'photourl' in available_columns:
            optional_selects.append('fr.photourl')
        if 'estimatedcalories' in available_columns:
            optional_selects.append('fr.estimatedcalories')
        if 'estimatedname' in available_columns:
            optional_selects.append('fr.estimatedname')
        if 'estimationconfidence' in available_columns:
            optional_selects.append('fr.estimationconfidence')
        if 'estimatedprotein' in available_columns:
            optional_selects.append('fr.estimatedprotein')
        if 'estimatedfat' in available_columns:
            optional_selects.append('fr.estimatedfat')
        if 'estimatedcarb' in available_columns:
            optional_selects.append('fr.estimatedcarb')
        if 'estimatedsugar' in available_columns:
            optional_selects.append('fr.estimatedsugar')
        if 'estimatedsodium' in available_columns:
            optional_selects.append('fr.estimatedsodium')
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    fr.RecordID,
                    fr.FoodID,
                    fr.CustomName,
                    fr.CustomCalories,
                    fr.CustomType,
                    fr.CustomPrice,
                    fr.CustomRestaurant,
                    f.Name,
                    r.Name AS Restaurant,
                    f.Price,
                    f.Calories,
                    f.ImageUrl,
                    f.Protein,
                    f.Fat,
                    f.Sugar,
                    f.Sodium,
                    f.Carb,
                    f.Caffeine,
                    f.Food_Type,
                    f.Set_Type,
                    fr.Mealtime,
                    fr.Quantity,
                    fr.Date
                FROM Food_Records fr
                LEFT JOIN Food f ON fr.FoodID = f.FoodID
                LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
                WHERE fr.UserID = %s
            """
            if optional_selects:
                sql = sql.replace('fr.Date', f"fr.Date, {', '.join(optional_selects)}", 1)
            params = [user_id]
            if start_date:
                sql += " AND fr.Date >= %s"
                params.append(start_date)
            if end_date:
                sql += " AND fr.Date <= %s"
                params.append(end_date)
            if mealtime:
                sql += " AND fr.Mealtime = %s"
                params.append(mealtime)
            sql += " ORDER BY fr.Date DESC, fr.Mealtime"
            cursor.execute(sql, params)
            records = cursor.fetchall()
            results = []
            for record in records:
                if record['FoodID']:
                    # 關聯食物
                    results.append({
                        'record_id': record['RecordID'],
                        'food_id': record['FoodID'],
                        'name': record['Name'],
                        'restaurant': record['Restaurant'],
                        'price': record['Price'],
                        'calories': record['Calories'],
                        'image_url': record.get('ImageUrl'),          # DB food image
                        'photo_url': record.get('PhotoUrl'),           # Supabase user upload
                        'food_type': record['Food_Type'],
                        'type': record['Set_Type'],
                        'estimated_calories': record.get('EstimatedCalories'),
                        'estimated_name': record.get('EstimatedName'),
                        'estimation_confidence': record.get('EstimationConfidence'),
                        'protein': record.get('Protein') if record.get('Protein') is not None else record.get('EstimatedProtein'),
                        'fat': record.get('Fat') if record.get('Fat') is not None else record.get('EstimatedFat'),
                        'sugar': record.get('Sugar') if record.get('Sugar') is not None else record.get('EstimatedSugar'),
                        'sodium': record.get('Sodium') if record.get('Sodium') is not None else record.get('EstimatedSodium'),
                        'carb': record.get('Carb') if record.get('Carb') is not None else record.get('EstimatedCarb'),
                        'caffeine': record.get('Caffeine'),
                        'mealtime': record['Mealtime'],
                        'quantity': record['Quantity'],
                        'date': record['Date'].strftime('%Y-%m-%d') if record['Date'] else None
                    })
                else:
                    # 自訂食物
                    results.append({
                        'record_id': record['RecordID'],
                        'food_id': None,
                        'name': record['CustomName'],
                        'restaurant': record['CustomRestaurant'],
                        'price': record['CustomPrice'],
                        'calories': record['CustomCalories'],
                        'image_url': None,                             # custom food has no DB image
                        'photo_url': record.get('PhotoUrl'),           # Supabase user upload
                        'food_type': record['CustomType'],
                        'type': None,
                        'estimated_calories': record.get('EstimatedCalories'),
                        'estimated_name': record.get('EstimatedName'),
                        'estimation_confidence': record.get('EstimationConfidence'),
                        'protein': record.get('EstimatedProtein'),
                        'fat': record.get('EstimatedFat'),
                        'sugar': record.get('EstimatedSugar'),
                        'sodium': record.get('EstimatedSodium'),
                        'carb': record.get('EstimatedCarb'),
                        'caffeine': None,
                        'mealtime': record['Mealtime'],
                        'quantity': record['Quantity'],
                        'date': record['Date'].strftime('%Y-%m-%d') if record['Date'] else None
                    })
            return results
    except Exception as e:
        raise Exception(f"Error retrieving food records: {str(e)}")
    finally:
        conn.close()

def delete_food_record(user_id, record_id):
    """
    刪除食物記錄
    
    Args:
        user_id (int): 用戶ID (用於權限驗證)
        record_id (int): 記錄ID
        
    Returns:
        dict: 操作結果
    """
    conn = get_db_connection()
    try:
        # 首先檢查記錄是否存在且屬於該用戶
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT RecordID FROM Food_Records WHERE RecordID = %s AND UserID = %s",
                (record_id, user_id)
            )
            record = cursor.fetchone()
            if not record:
                raise ValueError(f"Food record not found or does not belong to user {user_id}")
        
        # 刪除記錄
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Food_Records WHERE RecordID = %s", (record_id,))
            conn.commit()
            
            return {
                "message": "Food record deleted successfully"
            }
            
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting food record: {str(e)}")
    finally:
        conn.close()

def get_user_favorites(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    f.FoodID,
                    f.Name,
                    r.Name AS Restaurant,
                    f.Price,
                    f.Calories,
                    f.Food_Type,
                    f.Set_Type
                FROM My_Favorite mf
                JOIN Food f ON mf.FoodID = f.FoodID
                LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
                WHERE mf.UserID = %s
                ORDER BY f.Name
            """
            cursor.execute(sql, (user_id,))
            favorites = cursor.fetchall()
            # 處理結果為 JSON 格式
            results = []
            for fav in favorites:
                results.append({
                    'food_id': fav['FoodID'],
                    'name': fav['Name'],
                    'restaurant': fav['Restaurant'],
                    'price': fav['Price'],
                    'calories': fav['Calories'],
                    'food_type': fav['Food_Type'],
                    'type': fav['Set_Type']
                })
            return results
    except Exception as e:
        raise Exception(f"Error retrieving favorites: {str(e)}")
    finally:
        conn.close()

def add_to_favorites(user_id, food_id):
    conn = get_db_connection()
    try:
        try:
            user_id = int(user_id)
            food_id = int(food_id)
        except (TypeError, ValueError):
            raise ValueError("user_id and food_id must be integers")

        if user_id <= 0 or food_id <= 0:
            raise ValueError("user_id and food_id must be positive integers")

        # 檢查用戶是否存在
        with conn.cursor() as cursor:
            cursor.execute("SELECT UserID FROM Users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

        # 檢查食物是否存在
        with conn.cursor() as cursor:
            cursor.execute("SELECT FoodID FROM Food WHERE FoodID = %s", (food_id,))
            food = cursor.fetchone()
            if not food:
                raise ValueError(f"Food with ID {food_id} not found")

        # 檢查是否已經收藏
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM My_Favorite WHERE UserID = %s AND FoodID = %s",
                (user_id, food_id)
            )
            existing = cursor.fetchone()
            if existing:
                return {
                    "created": False,
                    "message": "Food already in favorites",
                    "code": "favorite_already_exists"
                }

        # 添加到收藏
        with conn.cursor() as cursor:
            sql = "INSERT INTO My_Favorite (UserID, FoodID) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, food_id))
            conn.commit()
            return {
                "created": True,
                "message": "Food added to favorites successfully"
            }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def remove_from_favorites(user_id, food_id):
    conn = get_db_connection()
    try:
        try:
            user_id = int(user_id)
            food_id = int(food_id)
        except (TypeError, ValueError):
            raise ValueError("user_id and food_id must be integers")

        if user_id <= 0 or food_id <= 0:
            raise ValueError("user_id and food_id must be positive integers")

        # 檢查是否存在該收藏
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM My_Favorite WHERE UserID = %s AND FoodID = %s",
                (user_id, food_id)
            )
            favorite = cursor.fetchone()
            if not favorite:
                return {
                    "removed": False,
                    "message": f"Food with ID {food_id} not found in user's favorites",
                    "code": "favorite_not_found"
                }

        # 從收藏中移除
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM My_Favorite WHERE UserID = %s AND FoodID = %s",
                (user_id, food_id)
            )
            conn.commit()
            return {
                "removed": True,
                "message": "Food removed from favorites successfully"
            }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def update_food_record(user_id, record_id, updates):

    conn = get_db_connection()
    try:
        # 檢查記錄是否存在且屬於該用戶
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT RecordID FROM Food_Records WHERE RecordID = %s AND UserID = %s",
                (record_id, user_id)
            )
            record = cursor.fetchone()
            if not record:
                raise ValueError(f"Food record not found or does not belong to user {user_id}")
        # 動態組裝 SQL
        set_clauses = []
        params = []
        for field in ['Mealtime', 'Quantity', 'Date']:
            key = field.lower()
            if key in updates:
                set_clauses.append(f"{field} = %s")
                params.append(updates[key])
        if not set_clauses:
            raise ValueError("No valid fields to update")
        params.append(record_id)
        # 執行更新
        with conn.cursor() as cursor:
            sql = f"UPDATE Food_Records SET {', '.join(set_clauses)} WHERE RecordID = %s"
            cursor.execute(sql, params)
            conn.commit()
            return {"message": "Food record updated successfully"}
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating food record: {str(e)}")
    finally:
        conn.close() 