from flask import Blueprint, request, jsonify
from app.services.food_service import get_user_favorites, add_to_favorites, remove_from_favorites
import traceback

my_favorite_bp = Blueprint('my_favorite', __name__)

@my_favorite_bp.route('/favorites', methods=['GET'])
def get_favorites():
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400
        favorites = get_user_favorites(user_id)
        return jsonify(favorites), 200
    except Exception as e:
        print(f"獲取收藏發生錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@my_favorite_bp.route('/favorites', methods=['POST'])
def add_favorite():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        user_id = data.get('user_id')
        food_id = data.get('food_id')
        if user_id is None or food_id is None:
            return jsonify({"error": "user_id and food_id are required"}), 400
        result = add_to_favorites(user_id, food_id)
        return jsonify(result), 201
    except Exception as e:
        print(f"新增收藏發生錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@my_favorite_bp.route('/favorites', methods=['DELETE'])
def delete_favorite():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        user_id = data.get('user_id')
        food_id = data.get('food_id')
        if user_id is None or food_id is None:
            return jsonify({"error": "user_id and food_id are required"}), 400
        result = remove_from_favorites(user_id, food_id)
        return jsonify(result), 200
    except Exception as e:
        print(f"刪除收藏發生錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500