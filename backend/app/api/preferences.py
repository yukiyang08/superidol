from flask import Blueprint, request, jsonify
from app.services.preference_service import (
    get_exercise_items, get_food_types, get_restaurants,
    save_exercise_preferences, save_food_preferences, save_restaurant_preferences
)
import traceback
from app.db import get_db_connection
from functools import wraps

preferences_bp = Blueprint('preferences', __name__)

def db_transaction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_db_connection()
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print('[DB ERROR]', e)
            import traceback; traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    return wrapper

@preferences_bp.route('/exercise-items', methods=['GET'])
def api_get_exercise_items():
    try:
        items = get_exercise_items()
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@preferences_bp.route('/food-types', methods=['GET'])
def api_get_food_types():
    try:
        types = get_food_types()
        return jsonify(types)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@preferences_bp.route('/restaurants', methods=['GET'])
def api_get_restaurants():
    try:
        restaurants = get_restaurants()
        return jsonify(restaurants)
    except Exception as e:
        print("發生錯誤:", e)
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@preferences_bp.route('/user/exercise-preferences', methods=['POST'])
@db_transaction
def api_save_exercise_preferences(conn):
    data = request.json
    user_id = data.get('user_id')
    exercise_names = data.get('exercise_names', [])
    with conn.cursor() as cursor:
        save_exercise_preferences(user_id, exercise_names, cursor)
    return jsonify({'success': True})

@preferences_bp.route('/user/food-preferences', methods=['POST'])
@db_transaction
def api_save_food_preferences(conn):
    data = request.json
    user_id = data.get('user_id')
    food_types = data.get('food_types', [])
    with conn.cursor() as cursor:
        save_food_preferences(user_id, food_types, cursor)
    return jsonify({'success': True})

@preferences_bp.route('/user/restaurant-preferences', methods=['POST'])
@db_transaction
def api_save_restaurant_preferences(conn):
    data = request.json
    user_id = data.get('user_id')
    restaurant_ids = data.get('restaurant_ids', [])
    with conn.cursor() as cursor:
        save_restaurant_preferences(user_id, restaurant_ids, cursor)
    return jsonify({'success': True})

@preferences_bp.route('/user/food-preferences', methods=['GET'])
def get_food_preferences():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Food_Type FROM Food_Preference WHERE UserID = %s", (user_id,))
            rows = cursor.fetchall()
        return jsonify({'food_types': [row['Food_Type'] for row in rows]})
    finally:
        conn.close()

@preferences_bp.route('/user/exercise-preferences', methods=['GET'])
def get_exercise_preferences():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Exercise_Name FROM Exercise_Preference WHERE UserID = %s", (user_id,))
            rows = cursor.fetchall()
        return jsonify({'exercise_names': [row['Exercise_Name'] for row in rows]})
    finally:
        conn.close()

@preferences_bp.route('/user/restaurant-preferences', methods=['GET'])
def get_restaurant_preferences():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT RestaurantID FROM Restaurant_Preference WHERE UserID = %s", (user_id,))
            rows = cursor.fetchall()
        return jsonify({'restaurant_ids': [row['RestaurantID'] for row in rows]})
    finally:
        conn.close()

# PUT: 直接覆蓋偏好
@preferences_bp.route('/user/food-preferences', methods=['PUT'])
@db_transaction
def update_food_preferences(conn):
    data = request.json
    user_id = data.get('user_id')
    food_types = data.get('food_types', [])
    with conn.cursor() as cursor:
        save_food_preferences(user_id, food_types, cursor)
    return jsonify({'success': True})

@preferences_bp.route('/user/exercise-preferences', methods=['PUT'])
@db_transaction
def update_exercise_preferences(conn):
    data = request.json
    user_id = data.get('user_id')
    exercise_names = data.get('exercise_names', [])
    with conn.cursor() as cursor:
        save_exercise_preferences(user_id, exercise_names, cursor)
    return jsonify({'success': True})

@preferences_bp.route('/user/restaurant-preferences', methods=['PUT'])
@db_transaction
def update_restaurant_preferences(conn):
    data = request.json
    user_id = data.get('user_id')
    restaurant_ids = data.get('restaurant_ids', [])
    with conn.cursor() as cursor:
        save_restaurant_preferences(user_id, restaurant_ids, cursor)
    return jsonify({'success': True}) 