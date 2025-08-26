import pymysql
import jwt
from datetime import datetime, timedelta
from app.db import get_db_connection
from app.utils.security import hash_password, verify_password
from app.config import Config
from app.services.preference_service import save_restaurant_preferences, save_exercise_preferences, save_food_preferences

def register_user(data):
    """
    註冊使用者，只寫入 user，不處理偏好。
    """
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    weight = data.get('weight')
    budget = data.get('budget')
    weekcalorielimit = data.get('weekcalorielimit')

    if not all([name, email, password, weight, budget, weekcalorielimit]):
        return {"error": "Missing required fields"}

    hashed_password = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 檢查 email 是否存在
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        if cursor.fetchone():
            return {"error": "Email already exists"}

        # 新增使用者
        cursor.execute("""
            INSERT INTO Users (Name, Email, PasswordHash, Weight, Budget, WeekCalorieLimit)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, hashed_password, weight, budget, weekcalorielimit))
        user_id = cursor.lastrowid
        conn.commit()
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "name": name,
            "email": email
        }
    except pymysql.Error as e:
        conn.rollback()
        return {"error": f"Database error: {str(e)}"}
    finally:
        cursor.close()
        conn.close()


def login_user(data):
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return {"error": "Email and password are required"}

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT UserID, Name, Email, PasswordHash, Weight, Budget, WeekCalorieLimit FROM Users WHERE Email = %s", (email,))
            user = cursor.fetchone()

            if not user or not verify_password(password, user['PasswordHash']):
                return {"error": "Invalid email or password"}

            payload = {
                'user_id': user['UserID'],
                'email': user['Email'],
                'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
            }
            token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

            return {
                "message": "Login successful",
                "access_token": token,
                "user": {
                    "id": user['UserID'],
                    "name": user['Name'],
                    "email": user['Email'],
                    "weight": user['Weight'],
                    "budget": user['Budget'],
                    "weekCalorieLimit": user['WeekCalorieLimit']
                }
            }
    except pymysql.Error as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        conn.close()

def get_user_weight(user_id: int) -> float:
    """
    根據 user_id 查詢用戶體重。
    Args:
        user_id (int): 用戶ID
    Returns:
        float: 體重，查不到則回傳 None
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Weight FROM Users WHERE UserID = %s", (user_id,))
            row = cursor.fetchone()
            if row and 'Weight' in row:
                return float(row['Weight'])
            return None
    finally:
        conn.close()
