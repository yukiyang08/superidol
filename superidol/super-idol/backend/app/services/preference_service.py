from db import get_db_connection

# 這裡只保留底層邏輯 function，不再定義 Blueprint 路由



#取得
def get_exercise_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ExerciseItem")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    # 只回傳 name 欄位，id 不需要
    return [{"name": item["Exercise_Name"]} for item in items]

def get_food_types():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Food_Type FROM Food")
    types = [row['Food_Type'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return [{"id": i+1, "name": t} for i, t in enumerate(types)]

def get_restaurants():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Restaurant")
    restaurants = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": r["RestaurantID"], "name": r["Name"]} for r in restaurants]

#存取偏好

def save_exercise_preferences(user_id: int, exercise_names: list[str], cursor) -> None:
    """
    儲存用戶運動偏好（會先清空再新增）。
    Args:
        user_id (int): 用戶 ID。
        exercise_names (list[str]): 運動項目名稱列表。
        cursor: 資料庫 cursor，由外部傳入。
    """
    print(f'[DEBUG] save_exercise_preferences: user_id={user_id}, exercise_names={exercise_names}')
    cursor.execute("DELETE FROM Exercise_Preference WHERE UserID = %s", (user_id,))
    for exercise_name in exercise_names:
        print(f'[DEBUG] INSERT Exercise_Preference: user_id={user_id}, exercise_name={exercise_name}')
        cursor.execute(
            "INSERT INTO Exercise_Preference (UserID, Exercise_Name) VALUES (%s, %s)",
            (user_id, exercise_name)
        )


def save_food_preferences(user_id: int, food_types: list[str], cursor) -> None:
    """
    儲存用戶食物偏好（會先清空再新增）。
    Args:
        user_id (int): 用戶 ID。
        food_types (list[str]): 食物類型名稱列表。 
        cursor: 資料庫 cursor，由外部傳入。
    """
    print(f'[DEBUG] save_food_preferences: user_id={user_id}, food_types={food_types}')
    cursor.execute("DELETE FROM Food_Preference WHERE UserID = %s", (user_id,))
    for food_type in food_types:
        print(f'[DEBUG] INSERT Food_Preference: user_id={user_id}, food_type={food_type}')
        cursor.execute(
            "INSERT INTO Food_Preference (UserID, Food_Type) VALUES (%s, %s)",
            (user_id, food_type)
        )


def save_restaurant_preferences(user_id: int, restaurant_ids: list[int], cursor) -> None:
    """
    儲存用戶餐廳偏好（會先清空再新增）。
    Args:
        user_id (int): 用戶 ID。
        restaurant_ids (list[int]): 餐廳 ID 列表。
        cursor: 資料庫 cursor，由外部傳入。
    """
    print(f'[DEBUG] save_restaurant_preferences: user_id={user_id}, restaurant_ids={restaurant_ids}')
    cursor.execute("DELETE FROM Restaurant_Preference WHERE UserID = %s", (user_id,))
    for restaurant_id in restaurant_ids:
        print(f'[DEBUG] INSERT Restaurant_Preference: user_id={user_id}, restaurant_id={restaurant_id}')
        cursor.execute(
            "INSERT INTO Restaurant_Preference (UserID, RestaurantID) VALUES (%s, %s)",
            (user_id, restaurant_id)
        )