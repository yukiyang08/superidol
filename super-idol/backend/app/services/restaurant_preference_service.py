from app.db import get_db_connection

def insert_restaurant_preference(user_id, food_type):
    """
    插入一筆使用者的餐廳偏好（由註冊流程中使用）
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 確認餐廳是否存在
        cursor.execute("SELECT * FROM Restaurant WHERE RestuarantID = %s", (food_type,))
        restaurant = cursor.fetchone()
        if not restaurant:
            return {"error": f"Restaurant ID {food_type} not found"}

        # 新增偏好關係
        cursor.execute("""
            INSERT INTO Restaurant_Preference (UserID, RestuarantID)
            VALUES (%s, %s)
        """, (user_id, food_type))

        conn.commit()
        return {"message": f"Preference for restaurant {food_type} added"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()
