from flask import Blueprint, request, jsonify
from app.services.food_service import get_user_favorites, add_to_favorites, remove_from_favorites
from app.config import Config
import jwt
import traceback

my_favorite_bp = Blueprint('my_favorite', __name__)


def _get_token_user_id():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ', 1)[1].strip()
    if not token:
        return None

    payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
    user_id = payload.get('user_id')
    return int(user_id) if user_id is not None else None


def _resolve_user_id(payload=None):
    token_user_id = _get_token_user_id()
    req_user_id = None

    if payload is not None:
        req_user_id = payload.get('user_id')
    else:
        req_user_id = request.args.get('user_id', type=int)

    if token_user_id is not None:
        if req_user_id is not None and int(req_user_id) != token_user_id:
            raise PermissionError('user_id does not match token')
        return token_user_id

    if req_user_id is None:
        raise ValueError('user_id is required')

    return int(req_user_id)

@my_favorite_bp.route('/favorites', methods=['GET'])
def get_favorites():
    try:
        user_id = _resolve_user_id()
        favorites = get_user_favorites(user_id)
        return jsonify(favorites), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except (jwt.PyJWTError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"獲取收藏發生錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@my_favorite_bp.route('/favorites', methods=['POST'])
def add_favorite():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json() or {}
        user_id = _resolve_user_id(data)
        food_id = data.get('food_id')
        if food_id is None:
            return jsonify({"error": "food_id is required"}), 400

        result = add_to_favorites(user_id, food_id)
        if result.get('created'):
            return jsonify(result), 201
        return jsonify(result), 409
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except (jwt.PyJWTError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"新增收藏發生錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@my_favorite_bp.route('/favorites', methods=['DELETE'])
def delete_favorite():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json() or {}
        user_id = _resolve_user_id(data)
        food_id = data.get('food_id')
        if food_id is None:
            return jsonify({"error": "food_id is required"}), 400

        result = remove_from_favorites(user_id, food_id)
        if result.get('removed'):
            return jsonify(result), 200
        return jsonify(result), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except (jwt.PyJWTError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"刪除收藏發生錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500