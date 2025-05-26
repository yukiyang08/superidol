"""
Food API endpoints.
"""

from flask import Blueprint, request, jsonify
from ..services.food_service import (
    search_food, 
    add_food_record, 
    get_user_food_records,
    delete_food_record, 
    get_user_favorites, 
    add_to_favorites, 
    remove_from_favorites,
    update_food_record as update_food_record_service
)
from flask_cors import CORS
from app.db import get_db_connection
from app.services.preference_service import get_restaurants, get_food_types

food_bp = Blueprint('food', __name__)
CORS(food_bp)  # 啟用 CORS

@food_bp.route('/', methods=['GET'])
def get_foods():
    """
    Get all foods or search for foods based on filters
    """
    try:
        # 初始化空的過濾條件
        filters = {
            'name': request.args.get('name', ''),
            'priceMin': request.args.get('priceMin', ''),
            'priceMax': request.args.get('priceMax', ''),
            'calMin': request.args.get('calMin', ''),
            'calMax': request.args.get('calMax', ''),
            'type': request.args.get('type', ''),
            'restaurant': request.args.get('restaurant', '')
        }

        results = search_food(filters)
        if not results:
            results = []  # 確保返回空列表而不是 None
        return jsonify(results), 200
    except Exception as e:
        print(f"Error in get_foods: {str(e)}")  # 添加服務器端日誌
        return jsonify({'error': str(e)}), 500

@food_bp.route('/record', methods=['POST'])
def create_food_record():
    """
    添加食物消費記錄
    ---
    請求參數:
      user_id: 用戶ID
      food_id: 食物ID
      mealtime: 餐點類型 (早餐/午餐/晚餐/宵夜)
      quantity: 數量
      date: 日期 (YYYY-MM-DD)
    回應:
      201: 記錄創建成功
    """
    try:
        data = request.json
        
        # 檢查必要參數
        if 'user_id' not in data:
            return jsonify({"error": "Missing required field: user_id"}), 400
            
        result = add_food_record(data['user_id'], data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/record', methods=['GET'])
def get_food_records():
    """
    獲取用戶食物記錄
    ---
    查詢參數:
      user_id: 用戶ID
      start_date: 開始日期 (可選)
      end_date: 結束日期 (可選)
      mealtime: 餐點類型 (可選)
    回應:
      200: 食物記錄列表
    """
    try:
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        mealtime = request.args.get('mealtime')
        
        if not user_id:
            return jsonify({"error": "Missing required parameter: user_id"}), 400
            
        records = get_user_food_records(user_id, start_date, end_date, mealtime)
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/record/<int:record_id>', methods=['DELETE'])
def remove_food_record(record_id):
    """
    刪除食物記錄
    ---
    查詢參數:
      user_id: 用戶ID (用於驗證權限)
    回應:6
      200: 刪除成功
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "Missing required parameter: user_id"}), 400
            
        result = delete_food_record(user_id, record_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """
    獲取用戶收藏的食物清單
    ---
    查詢參數:
      user_id: 用戶ID
    回應:
      200: 收藏清單
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "Missing required parameter: user_id"}), 400
            
        favorites = get_user_favorites(user_id)
        return jsonify(favorites), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/favorites', methods=['POST'])
def add_favorite():
    """
    添加食物到收藏
    ---
    請求參數:
      user_id: 用戶ID
      food_id: 食物ID
    回應:
      201: 添加成功
    """
    try:
        data = request.json
        
        if 'user_id' not in data or 'food_id' not in data:
            return jsonify({"error": "Missing required fields: user_id and food_id"}), 400
            
        result = add_to_favorites(data['user_id'], data['food_id'])
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/favorites', methods=['DELETE'])
def remove_favorite():
    """
    從收藏中移除食物
    ---
    請求參數:
      user_id: 用戶ID
      food_id: 食物ID
    回應:
      200: 移除成功
    """
    try:
        data = request.json
        
        if 'user_id' not in data or 'food_id' not in data:
            return jsonify({"error": "Missing required fields: user_id and food_id"}), 400
            
        result = remove_from_favorites(data['user_id'], data['food_id'])
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/exercise/calculator', methods=['GET'])
def calculate_exercise():
    """
    計算消耗卡路里需要的運動量
    ---
    查詢參數:
      calories: 要消耗的卡路里
    回應:
      200: 運動量建議
    """
    try:
        calories = request.args.get('calories')
        
        if not calories:
            return jsonify({"error": "Missing required parameter: calories"}), 400
            
        calories = float(calories)
        
        # 簡易的運動消耗計算
        exercises = [
            {
                "type": "跑步",
                "duration": round(calories / 10),  # 假設跑步消耗10大卡/分鐘
                "met": 10
            },
            {
                "type": "游泳",
                "duration": round(calories / 8),  # 假設游泳消耗8大卡/分鐘
                "met": 8
            },
            {
                "type": "騎腳踏車",
                "duration": round(calories / 7),  # 假設騎車消耗7大卡/分鐘
                "met": 7
            },
            {
                "type": "健走",
                "duration": round(calories / 5),  # 假設健走消耗5大卡/分鐘
                "met": 5
            }
        ]
        
        return jsonify({
            "calories": calories,
            "exercises": exercises
        }), 200
    except ValueError:
        return jsonify({"error": "Invalid calories value"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/record/<int:record_id>', methods=['PUT'])
def update_food_record(record_id):
    """
    修改食物記錄
    ---
    路徑參數:
      record_id: 食物記錄ID
    請求參數:
      user_id: 用戶ID (驗證權限)
      mealtime: 餐點類型 (可選)
      quantity: 數量 (可選)
      date: 日期 (可選)
    回應:
      200: 修改成功
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "Missing required field: user_id"}), 400
        # 允許部分欄位更新
        updates = {}
        for field in ['mealtime', 'quantity', 'date']:
            if field in data:
                updates[field] = data[field]
        if not updates:
            return jsonify({"error": "No fields to update"}), 400
        result = update_food_record_service(user_id, record_id, updates)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/recommend', methods=['GET'])
def recommend_foods():
    """
    根據用戶資料推薦食物（分類推薦，含推薦原因）
    查詢參數: user_id
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 取得用戶基本資料
            cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"error": "User not found"}), 404

            # 2. 取得偏好
            cursor.execute("SELECT Food_Type FROM Food_Preference WHERE UserID = %s", (user_id,))
            food_types = [row['Food_Type'] for row in cursor.fetchall()]
            cursor.execute("SELECT r.Name FROM Restaurant_Preference rp JOIN Restaurant r ON rp.RestaurantID = r.RestaurantID WHERE rp.UserID = %s", (user_id,))
            restaurants = [row['Name'] for row in cursor.fetchall()]

            # 3. 取得歷史紀錄
            records = get_user_food_records(user_id)
            favorites = get_user_favorites(user_id)

            # 4. 推薦邏輯
            categories = []
            seen_food_ids = set()

            # (0) 多條件綜合推薦（優化：直接用 SQL 多條件查詢）
            multi_filters = {}
            if restaurants:
                multi_filters['restaurant'] = restaurants[0] if len(restaurants) == 1 else restaurants
            if food_types:
                multi_filters['type'] = food_types[0] if len(food_types) == 1 else food_types
            if user.get('Budget'):
                multi_filters['priceMax'] = user['Budget']
            if user.get('WeekCalorieLimit'):
                per_meal = int(user['WeekCalorieLimit']) // 21
                multi_filters['calMax'] = per_meal
            # 只查出前 200 筆
            candidate_foods = search_food(multi_filters)[:200]
            scored_foods = []
            for food in candidate_foods:
                score = 0
                reasons = []
                if restaurants and (food['restaurant'] in restaurants):
                    score += 2
                    reasons.append(f"餐廳({food['restaurant']})")
                if food_types and (food['type'] in food_types or food['food_type'] in food_types):
                    score += 2
                    reasons.append(f"類型({food['type'] or food['food_type']})")
                if user.get('Budget') and food['price'] is not None and float(food['price']) <= float(user['Budget']):
                    score += 1
                    reasons.append(f"預算({user['Budget']}元內)")
                if user.get('WeekCalorieLimit') and food['calories'] is not None:
                    if float(food['calories']) <= per_meal:
                        score += 1
                        reasons.append(f"卡路里({per_meal}大卡內)")
                if any(f.get('food_id', -1) == food['id'] for f in records):
                    score += 1
                    reasons.append("你曾記錄過")
                if any(f.get('food_id', -1) == food['id'] for f in favorites):
                    score += 1
                    reasons.append("你收藏過")
                if score >= 3:
                    scored_foods.append({"food": food, "score": score, "reasons": reasons})
            scored_foods = sorted(scored_foods, key=lambda x: -x['score'])[:6]
            if scored_foods:
                categories.append({
                    "title": "多條件綜合推薦",
                    "reason": "同時符合多項偏好條件：" + ", ".join(sorted({r for f in scored_foods for r in f['reasons']})),
                    "foods": [f["food"] for f in scored_foods]
                })
                seen_food_ids.update(f["food"]["id"] for f in scored_foods)

            # (1) 餐廳偏好推薦
            for rest in restaurants:
                foods = search_food({'restaurant': rest})[:6]
                foods = [f for f in foods if f['id'] not in seen_food_ids]
                seen_food_ids.update(f['id'] for f in foods)
                if foods:
                    categories.append({
                        "title": f"根據你常吃的餐廳推薦",
                        "reason": f"你常在 {rest} 用餐",
                        "foods": foods
                    })

            # (2) 食物類型偏好推薦
            for ftype in food_types:
                foods = search_food({'type': ftype})[:6]
                foods = [f for f in foods if f['id'] not in seen_food_ids]
                seen_food_ids.update(f['id'] for f in foods)
                if foods:
                    categories.append({
                        "title": f"根據你最愛的食物類型推薦",
                        "reason": f"你偏好 {ftype} 類型",
                        "foods": foods
                    })

            # (3) 預算推薦
            if user.get('Budget'):
                foods = search_food({'priceMax': user['Budget']})[:6]
                foods = [f for f in foods if f['id'] not in seen_food_ids]
                seen_food_ids.update(f['id'] for f in foods)
                if foods:
                    categories.append({
                        "title": f"根據你每餐預算推薦",
                        "reason": f"你設定每餐預算為 {user['Budget']} 元",
                        "foods": foods
                    })

            # (4) 卡路里推薦
            if user.get('WeekCalorieLimit'):
                per_meal = int(user['WeekCalorieLimit']) // 21  # 7天3餐
                foods = search_food({'calMax': per_meal})[:6]
                foods = [f for f in foods if f['id'] not in seen_food_ids]
                seen_food_ids.update(f['id'] for f in foods)
                if foods:
                    categories.append({
                        "title": f"根據你每餐卡路里建議推薦",
                        "reason": f"你每週卡路里上限，建議每餐不超過 {per_meal} 大卡",
                        "foods": foods
                    })

            # (5) 歷史紀錄
            if records:
                foods = [f for f in records if f['food_id'] not in seen_food_ids]
                seen_food_ids.update(f['food_id'] for f in foods)
                if foods:
                    categories.append({
                        "title": "你曾經記錄過的食物",
                        "reason": "你過去有記錄過這些食物",
                        "foods": foods[:6]
                    })

            # (6) 最愛
            if favorites:
                foods = [f for f in favorites if f['food_id'] not in seen_food_ids]
                seen_food_ids.update(f['food_id'] for f in foods)
                if foods:
                    categories.append({
                        "title": "你收藏的最愛",
                        "reason": "你收藏過這些食物",
                        "foods": foods[:6]
                    })

            return jsonify({"categories": categories}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@food_bp.route('/restaurants', methods=['GET'])
def api_get_restaurants():
    try:
        restaurants = get_restaurants()
        return jsonify(restaurants)
    except Exception as e:
        print("發生錯誤:", e)
        import traceback; print(traceback.format_exc())
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@food_bp.route('/types', methods=['GET'])
def api_get_food_types():
    try:
        types = get_food_types()
        return jsonify([t['name'] for t in types])
    except Exception as e:
        print("發生錯誤:", e)
        import traceback; print(traceback.format_exc())
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500 