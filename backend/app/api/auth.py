from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, login_user
from app.db import get_db_connection
import jwt
from app.config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    使用者註冊
    ---
    tags:
      - Auth
    responses:
      201:
        description: 註冊成功
      400:
        description: 請求參數錯誤
      409:
        description: 使用者已存在
      500:
        description: 伺服器錯誤
    """
    try:
        data = request.get_json() or {}

        required_fields = ['name', 'email', 'password', 'weight']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        if 'weekcalorielimit' not in data and 'weekCalorieLimit' not in data and 'calorieLimit' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        result = register_user(data)
        if 'error' in result:
            return jsonify(result), 409 if 'exists' in result['error'] else 400

        return jsonify({
            'user_id': result['user_id'],
            'name': result['name'],
            'email': result['email'],
            'message': result['message']
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    使用者登入
    ---
    tags:
      - Auth
    responses:
      200:
        description: 登入成功
      400:
        description: 缺少輸入資料
      401:
        description: 帳號或密碼錯誤
      500:
        description: 伺服器錯誤
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        result = login_user(data)
        if 'error' in result:
            return jsonify(result), 401

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/user', methods=['GET'])
def get_user():
    """
    獲取用戶完整資料
    ---
    tags:
      - Auth
    responses:
      200:
        description: 成功取得使用者資料
      401:
        description: Token 無效或缺失
      404:
        description: 找不到使用者
      500:
        description: 伺服器錯誤
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT UserID, Name, Email, Weight, Budget, WeekCalorieLimit
                    FROM Users
                    WHERE UserID = %s
                    """,
                    (user_id,),
                )
                user = cursor.fetchone()

            if not user:
                return jsonify({"error": "User not found"}), 404

            return jsonify({
                "id": user['UserID'],
                "name": user['Name'],
                "email": user['Email'],
                "weight": user['Weight'],
                "budget": user['Budget'],
                "weekCalorieLimit": user['WeekCalorieLimit']
            }), 200
        except jwt.PyJWTError:
            return jsonify({"error": "Invalid or expired token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({'exists': False, 'error': 'No email provided'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM Users WHERE Email = %s", (email,))
            exists = cursor.fetchone() is not None
        return jsonify({'exists': exists})
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)}), 500
    finally:
        conn.close()


@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        data = request.get_json() or {}

        allowed_fields = ['name', 'email', 'budget', 'weekcalorielimit', 'weight']
        fields = []
        values = []
        for key in allowed_fields:
            if key in data:
                db_key = {
                    'name': 'Name',
                    'email': 'Email',
                    'budget': 'Budget',
                    'weekcalorielimit': 'WeekCalorieLimit',
                    'weight': 'Weight'
                }[key]
                fields.append(f"{db_key} = %s")
                values.append(data[key])

        if not fields:
            return jsonify({"error": "No fields to update"}), 400

        values.append(user_id)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"UPDATE Users SET {', '.join(fields)} WHERE UserID = %s", tuple(values))
            conn.commit()
        finally:
            conn.close()

        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
