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
    update_food_record as update_food_record_service,
    cached_search_food, cached_search_food_precise, filters_to_tuple
)
from ..services.food_photo_service import (
    upload_and_estimate_food_photo,
    upload_food_photo_only,
    estimate_existing_food_photo,
)
from flask_cors import CORS
from app.db import get_db_connection, return_db_connection
from app.services.preference_service import get_restaurants, get_food_types

food_bp = Blueprint('food', __name__)
CORS(food_bp)  # 啟用 CORS

@food_bp.route('/', methods=['GET'])
def get_foods():
        """
        搜尋食物
        ---
        tags:
          - Food
        responses:
          200:
            description: 成功回傳食物列表
          500:
            description: 伺服器錯誤
        """
        try:
                filters = {
                        'name': request.args.get('name', ''),
                        'priceMin': request.args.get('priceMin', ''),
                        'priceMax': request.args.get('priceMax', ''),
                        'calMin': request.args.get('calMin', ''),
                        'calMax': request.args.get('calMax', ''),
                        'type': request.args.get('type', ''),
                        'restaurant': request.args.get('restaurant', '')
                }

                results = cached_search_food(filters_to_tuple(filters))
                if not results:
                        results = []
                return jsonify(results), 200
        except Exception as e:
                print(f"Error in get_foods: {str(e)}")
                return jsonify({'error': str(e)}), 500

@food_bp.route('/record', methods=['POST'])
def create_food_record():
        """
        添加食物消費記錄
        ---
        tags:
          - Food Record
        responses:
          201:
            description: 記錄新增成功
          400:
            description: 參數錯誤
          500:
            description: 伺服器錯誤
        """
        try:
                data = request.json

                if 'user_id' not in data:
                        return jsonify({"error": "Missing required field: user_id"}), 400

                result = add_food_record(data['user_id'], data)
                return jsonify(result), 201
        except ValueError as e:
                return jsonify({"error": str(e)}), 400
        except Exception as e:
                return jsonify({"error": str(e)}), 500

@food_bp.route('/record/photo-estimate', methods=['POST'])
def estimate_food_photo():
    """Estimate calories from a new upload or an already uploaded food photo."""
    try:
        user_id = request.form.get('user_id')
        image = request.files.get('image')
        photo_url = request.form.get('photo_url', '').strip()
        photo_path = request.form.get('photo_path', '').strip()
        photo_mime_type = request.form.get('photo_mime_type', '').strip()

        if not user_id:
            return jsonify({"error": "Missing required field: user_id"}), 400

        if image:
            result = upload_and_estimate_food_photo(user_id, image)
        elif photo_url:
            result = estimate_existing_food_photo(
                photo_url=photo_url,
                photo_path=photo_path,
                photo_mime_type=photo_mime_type or None,
            )
        else:
            return jsonify({"error": "Missing required field: image or photo_url"}), 400

        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@food_bp.route('/record/photo-upload', methods=['POST'])
def upload_food_photo():
    """Upload a food photo only, without AI estimation."""
    try:
        user_id = request.form.get('user_id')
        image = request.files.get('image')

        if not user_id:
            return jsonify({"error": "Missing required field: user_id"}), 400

        result = upload_food_photo_only(user_id, image)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/record', methods=['GET'])
def get_food_records():
    """
    獲取用戶食物記錄。
    查詢參數包含 user_id、start_date、end_date、mealtime。
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
    刪除食物記錄。
    查詢參數需要 user_id 以驗證權限。
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
    獲取用戶收藏的食物清單。
    查詢參數需要 user_id。
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
    添加食物到收藏。
    請求參數需要 user_id 與 food_id。
    """
    try:
        data = request.json
        
        if 'user_id' not in data or 'food_id' not in data:
            return jsonify({"error": "Missing required fields: user_id and food_id"}), 400
            
        result = add_to_favorites(data['user_id'], data['food_id'])
        if result.get('created'):
            return jsonify(result), 201
        return jsonify(result), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/favorites', methods=['DELETE'])
def remove_favorite():
    """
    從收藏中移除食物。
    請求參數需要 user_id 與 food_id。
    """
    try:
        data = request.json
        
        if 'user_id' not in data or 'food_id' not in data:
            return jsonify({"error": "Missing required fields: user_id and food_id"}), 400
            
        result = remove_from_favorites(data['user_id'], data['food_id'])
        if result.get('removed'):
            return jsonify(result), 200
        return jsonify(result), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@food_bp.route('/exercise/calculator', methods=['GET'])
def calculate_exercise():
    """
    計算消耗卡路里需要的運動量（根據 MET 與體重動態計算）
    查詢參數:
      calories: 要消耗的卡路里
      user_id: 用戶ID（可選，無則預設 60kg）
    回應:
      200: 運動量建議
    """
    try:
        calories = request.args.get('calories')
        user_id = request.args.get('user_id')
        if not calories:
            return jsonify({"error": "Missing required parameter: calories"}), 400
        calories = float(calories)
        
        # 1. 取得體重
        weight = 60.0
        if user_id:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT Weight FROM Users WHERE UserID = %s", (user_id,))
                row = cursor.fetchone()
                if row and (row.get('Weight') or row.get('weight')):
                    weight = float(row.get('Weight') or row.get('weight'))
            conn.close()

        # 2. 查詢所有運動及 MET
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT Exercise_Name, MET FROM ExerciseItem")
            items = cursor.fetchall()
        conn.close()

        # 3. 計算每種運動所需分鐘數
        # 消耗卡路里公式: Cal = MET × 體重(kg) × 時間(hr) × 1.05
        # => 時間(分鐘) = (calories / (MET × 體重 × 1.05)) × 60
        exercises = []
        for item in items:
            met = float(item['MET'])
            if met > 0:
                minutes = (calories / (met * weight * 1.05)) * 60
                exercises.append({
                    "type": item['Exercise_Name'],
                    "met": met,
                    "duration": int(round(minutes))
                })
        
        return jsonify({
            "calories": calories,
            "weight": weight,
            "exercises": exercises
        }), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@food_bp.route('/record/<int:record_id>', methods=['PUT'])
def update_food_record(record_id):
    """
    修改食物記錄。
    路徑參數為 record_id，請求參數需要 user_id，並可選 mealtime、quantity、date。
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
    根據用戶資料推薦食物
    查詢參數: user_id
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 一次性取得所有用戶相關資料
            cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"error": "User not found"}), 404

            # 取得所有偏好資料
            cursor.execute("""
                SELECT 'food_type' as type, Food_Type as value FROM Food_Preference WHERE UserID = %s
                UNION ALL
                SELECT 'restaurant' as type, r.Name as value 
                FROM Restaurant_Preference rp 
                JOIN Restaurant r ON rp.RestaurantID = r.RestaurantID 
                WHERE rp.UserID = %s
            """, (user_id, user_id))
            
            preferences = cursor.fetchall()
            food_types = [p['value'] for p in preferences if p['type'] == 'food_type']
            restaurants = [p['value'] for p in preferences if p['type'] == 'restaurant']

            # 一次性取得歷史紀錄和收藏（限制數量，避免全量掃描）
            cursor.execute(
                """
                SELECT
                    fr.FoodID,
                    COALESCE(f.Price, fr.CustomPrice) AS Price,
                    COALESCE(f.Calories, fr.CustomCalories) AS Calories,
                    COALESCE(f.Name, fr.CustomName) AS Name,
                    COALESCE(r.Name, fr.CustomRestaurant) AS Restaurant,
                    COALESCE(f.Food_Type, fr.CustomType) AS Food_Type,
                    f.Set_Type,
                    fr.Date
                FROM Food_Records fr
                LEFT JOIN Food f ON fr.FoodID = f.FoodID
                LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
                WHERE fr.UserID = %s
                ORDER BY fr.Date DESC, fr.RecordID DESC
                LIMIT 10
                """,
                (user_id,)
            )
            records_raw = cursor.fetchall()
            records = [
                {
                    'food_id': record.get('FoodID'),
                    'name': record.get('Name'),
                    'restaurant': record.get('Restaurant'),
                    'price': record.get('Price'),
                    'calories': record.get('Calories'),
                    'food_type': record.get('Food_Type'),
                    'type': record.get('Set_Type'),
                    'date': record.get('Date').strftime('%Y-%m-%d') if record.get('Date') else None
                }
                for record in records_raw
            ]

            cursor.execute(
                """
                SELECT f.FoodID, f.Name, r.Name AS Restaurant, f.Price, f.Calories, f.Food_Type, f.Set_Type
                FROM My_Favorite mf
                JOIN Food f ON mf.FoodID = f.FoodID
                LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
                WHERE mf.UserID = %s
                ORDER BY mf.FavoriteID DESC
                LIMIT 50
                """,
                (user_id,)
            )
            favorites_raw = cursor.fetchall()
            favorites = [
                {
                    'food_id': fav.get('FoodID'),
                    'name': fav.get('Name'),
                    'restaurant': fav.get('Restaurant'),
                    'price': fav.get('Price'),
                    'calories': fav.get('Calories'),
                    'food_type': fav.get('Food_Type'),
                    'type': fav.get('Set_Type')
                }
                for fav in favorites_raw
            ]
            
            # 分析用戶習慣
            historical_food_ids = set()
            favorite_food_ids = set()
            price_range = {'min': float('inf'), 'max': 0, 'avg': 0}
            calorie_range = {'min': float('inf'), 'max': 0, 'avg': 0}
            
            total_price = 0
            total_calories = 0
            count = 0
            
            for record in records:
                if record.get('food_id'):
                    historical_food_ids.add(record['food_id'])
                    if record.get('price'):
                        price = float(record['price'])
                        price_range['min'] = min(price_range['min'], price)
                        price_range['max'] = max(price_range['max'], price)
                        total_price += price
                        count += 1
                    if record.get('calories'):
                        calories = float(record['calories'])
                        calorie_range['min'] = min(calorie_range['min'], calories)
                        calorie_range['max'] = max(calorie_range['max'], calories)
                        total_calories += calories
            
            if count > 0:
                price_range['avg'] = total_price / count
                calorie_range['avg'] = total_calories / count
            
            for fav in favorites:
                if fav.get('food_id'):
                    favorite_food_ids.add(fav['food_id'])

            # 2. 計算推薦參數（更智能的預算和卡路里計算）
            budget_limit = user.get('Budget')
            calorie_limit = None
            if user.get('WeekCalorieLimit'):
                calorie_limit = int(user['WeekCalorieLimit']) // 21

            # 根據歷史數據調整推薦範圍
            if count > 5:  # 有足夠歷史數據時使用用戶習慣
                if not budget_limit or budget_limit > price_range['avg'] * 1.5:
                    budget_limit = int(price_range['avg'] * 1.3)  # 比平均消費高30%
                if not calorie_limit or calorie_limit > calorie_range['avg'] * 1.5:
                    calorie_limit = int(calorie_range['avg'] * 1.2)  # 比平均卡路里高20%

            # 3. 高精準度推薦策略
            recommendation_strategies = []
            seen_food_ids = set()

            # 策略1: 超精準個人化推薦（最嚴格的篩選）
            if (food_types and restaurants) or len(historical_food_ids) >= 3:
                filters = {}
                if restaurants:
                    filters['restaurant'] = restaurants[0] if len(restaurants) == 1 else ','.join(restaurants[:2])
                if food_types:
                    filters['food_type'] = food_types[0] if len(food_types) == 1 else ','.join(food_types[:2])
                if budget_limit:
                    filters['priceMax'] = budget_limit
                if calorie_limit:
                    filters['calMax'] = calorie_limit

                candidate_foods = cached_search_food_precise(filters_to_tuple(filters), 50)  # 使用精準搜尋
                
                # 高精準度評分算法
                high_score_foods = []
                for food in candidate_foods:
                    if food['id'] in seen_food_ids:
                        continue
                        
                    score = 0
                    reasons = []
                    
                    # 偏好匹配 (高權重)
                    if restaurants and food.get('restaurant') in restaurants:
                        score += 5
                        reasons.append("最愛餐廳")
                    
                    if food_types and (food.get('type') in food_types or food.get('food_type') in food_types):
                        score += 5
                        reasons.append("偏愛類型")
                    
                    # 收藏和歷史加分 (超高權重)
                    if food['id'] in favorite_food_ids:
                        score += 8
                        reasons.append("已收藏")
                    
                    if food['id'] in historical_food_ids:
                        score += 4
                        reasons.append("常吃")
                    
                    # 價格匹配度
                    if food.get('price') and budget_limit:
                        price = float(food['price'])
                        if count > 0 and price_range['avg'] > 0:
                            # 根據歷史價格偏好評分
                            price_diff = abs(price - price_range['avg']) / price_range['avg']
                            if price_diff <= 0.2:  # 價格差異在20%內
                                score += 3
                                reasons.append("符合消費習慣")
                            elif price <= budget_limit * 0.8:
                                score += 2
                                reasons.append("經濟實惠")
                        elif price <= budget_limit:
                            score += 2
                            reasons.append("符合預算")
                    
                    # 卡路里匹配度
                    if food.get('calories') and calorie_limit:
                        calories = float(food['calories'])
                        if count > 0 and calorie_range['avg'] > 0:
                            cal_diff = abs(calories - calorie_range['avg']) / calorie_range['avg']
                            if cal_diff <= 0.3:  # 卡路里差異在30%內
                                score += 2
                                reasons.append("熱量適中")
                        elif calories <= calorie_limit:
                            score += 1
                            reasons.append("健康選擇")
                    
                    # 高分門檻確保精準度
                    if score >= 8:  # 提高門檻
                        high_score_foods.append({"food": food, "score": score, "reasons": reasons})

                if high_score_foods:
                    high_score_foods.sort(key=lambda x: (-x['score'], -len(x['reasons'])))
                    top_foods = high_score_foods[:3]  # 只推薦3個
                    recommendation_strategies.append({
                        "title": "專屬精選",
                        "reason": "根據你的喜好和習慣精心挑選",
                        "foods": [f["food"] for f in top_foods]
                    })
                    seen_food_ids.update(f["food"]["id"] for f in top_foods)

            # 策略2: 餐廳精選（只選最符合的）
            if restaurants and len(recommendation_strategies) < 2:
                # 選擇用戶最常去的餐廳
                primary_restaurant = restaurants[0]
                filters = {'restaurant': primary_restaurant}
                if budget_limit:
                    filters['priceMax'] = budget_limit
                
                restaurant_foods = cached_search_food_precise(filters_to_tuple(filters), 120)
                scored_restaurant_foods = []
                
                for food in restaurant_foods:
                    if food['id'] in seen_food_ids:
                        continue
                    
                    score = 3  # 基礎分數
                    if food['id'] in favorite_food_ids:
                        score += 4
                    if food['id'] in historical_food_ids:
                        score += 2
                    if food_types and (food.get('type') in food_types or food.get('food_type') in food_types):
                        score += 2
                    
                    scored_restaurant_foods.append({"food": food, "score": score})
                
                if scored_restaurant_foods:
                    scored_restaurant_foods.sort(key=lambda x: -x['score'])
                    top_restaurant_foods = [f["food"] for f in scored_restaurant_foods[:3]]
                    
                    recommendation_strategies.append({
                        "title": f"{primary_restaurant} 精選",
                        "reason": f"你最愛的 {primary_restaurant} 優質推薦",
                        "foods": top_restaurant_foods
                    })
                    seen_food_ids.update(f['id'] for f in top_restaurant_foods)

            # 策略3: 健康精選（如果有卡路里限制）
            if calorie_limit and len(recommendation_strategies) < 3:
                health_filters = {'calMax': int(calorie_limit * 0.8)}  # 控制在80%以內
                if budget_limit:
                    health_filters['priceMax'] = budget_limit
                
                healthy_foods = cached_search_food_precise(filters_to_tuple(health_filters), 120)
                healthy_foods = [f for f in healthy_foods if f['id'] not in seen_food_ids]
                
                # 選擇營養均衡的食物
                balanced_foods = []
                for food in healthy_foods:
                    if food.get('Protein') and food.get('Carb'):
                        protein = float(food['Protein'] or 0)
                        carb = float(food['Carb'] or 0)
                        if protein >= 10 and carb <= 50:  # 高蛋白低碳水
                            balanced_foods.append(food)
                
                if balanced_foods:
                    recommendation_strategies.append({
                        "title": "健康精選",
                        "reason": f"控制在 {int(calorie_limit * 0.8)} 大卡以內的健康選擇",
                        "foods": balanced_foods[:3]
                    })
                    seen_food_ids.update(f['id'] for f in balanced_foods[:3])

            # 策略4: 探索新品（只在前面推薦不足時添加）
            if len(recommendation_strategies) < 2:
                # 尋找用戶從未嘗試過的食物
                explore_filters = {}
                if budget_limit:
                    explore_filters['priceMax'] = budget_limit
                if restaurants:
                    explore_filters['restaurant'] = ','.join(restaurants)
                
                all_foods = cached_search_food_precise(filters_to_tuple(explore_filters), 120)
                new_foods = [f for f in all_foods if f['id'] not in historical_food_ids and f['id'] not in favorite_food_ids and f['id'] not in seen_food_ids]
                
                if new_foods:
                    # 選擇評分較高的新食物
                    scored_new_foods = []
                    for food in new_foods:
                        score = 1  # 基礎探索分數
                        if food_types and (food.get('type') in food_types or food.get('food_type') in food_types):
                            score += 2
                        if restaurants and food.get('restaurant') in restaurants:
                            score += 2
                        scored_new_foods.append({"food": food, "score": score})
                    
                    scored_new_foods.sort(key=lambda x: -x['score'])
                    recommendation_strategies.append({
                        "title": "發現新美味",
                        "reason": "為你推薦從未嘗試過的美食",
                        "foods": [f["food"] for f in scored_new_foods[:3]]
                    })

            # 確保至少有一個推薦類別
            if not recommendation_strategies:
                # 降級推薦：直接推薦收藏或歷史記錄
                if favorites:
                    recommendation_strategies.append({
                        "title": "經典回味",
                        "reason": "你的收藏美食",
                        "foods": favorites[:3]
                    })
                elif records:
                    recommendation_strategies.append({
                        "title": "再次品嚐",
                        "reason": "你最近吃過的美食",
                        "foods": records[:3]
                    })

            return jsonify({"categories": recommendation_strategies}), 200

    except Exception as e:
        import traceback
        print(f"推薦系統錯誤: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        return_db_connection(conn)

@food_bp.route('/restaurants', methods=['GET'])
def api_get_restaurants():
    try:
        restaurants = list(get_restaurants())
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