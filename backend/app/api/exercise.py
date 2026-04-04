"""
Exercise API endpoints.
"""

from flask import Blueprint, request, jsonify
from app.services.exercise_service import (
    log_exercise, 
    get_exercise_records, 
    get_all_exercise_items,
    update_exercise_record,
    delete_exercise_record
)
from app.services.auth_service import get_user_weight

exercise_bp = Blueprint('exercise', __name__)

@exercise_bp.route('/items', methods=['GET'])
def get_exercise_items_api():
    """
        獲取所有可用的運動項目
        ---
        tags:
            - Exercise
        responses:
            200:
                description: 運動項目列表
            500:
                description: 伺服器錯誤
    """
    try:
        print("開始獲取運動項目...")
        items = get_all_exercise_items()
        
        if not items:
            print("警告: 沒有獲取到任何運動項目")
            # 返回更詳細的錯誤信息但仍保持 200 狀態碼
            return jsonify({
                "items": [],
                "message": "沒有找到任何運動項目",
                "possible_cause": "ExerciseItem 表可能不存在或沒有數據" 
            }), 200
        
        print(f"成功獲取 {len(items)} 個運動項目")
        return jsonify({"items": items}), 200
    except Exception as e:
        error_msg = str(e)
        print(f"獲取運動項目失敗: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": error_msg,
            "message": "獲取運動項目時發生錯誤"
        }), 500

@exercise_bp.route('/log', methods=['POST'])
def log_exercise_api():

    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id 為必填欄位"}), 400
        result = log_exercise(user_id, data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exercise_bp.route('/records', methods=['GET'])
def get_exercise_records_api():
    """
    查詢使用者的運動紀錄。
    Query params:
      user_id: 使用者ID
      start_date: 起始日期（可選）
      end_date: 結束日期（可選）
    """
    try:
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if not user_id:
            return jsonify({"error": "user_id 為必填欄位"}), 400
        records = get_exercise_records(user_id, start_date, end_date)
        return jsonify({"records": records}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exercise_bp.route('/preferences', methods=['GET', 'POST'])
def manage_exercise_preferences():
    """
    Manage user's exercise preferences.
    """
    # TODO: Implement exercise preferences management
    return jsonify({"message": "Exercise preferences endpoint - to be implemented"}), 200 

@exercise_bp.route('/<int:record_id>', methods=['PUT'])
def update_exercise_record_api(record_id):
    """
    更新一筆運動紀錄。
    Path params:
      record_id: 運動紀錄ID
    Request body:
      user_id: 使用者ID
      exercise_name: 運動名稱（可選）
      duration: 持續時間（分鐘）（可選）
      date: 運動日期（可選）
    """
    try:
        data = request.get_json() or {}
        user_id = data.pop('user_id', None)
        if not user_id:
            return jsonify({"error": "user_id 為必填欄位"}), 400
        result = update_exercise_record(user_id, record_id, data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@exercise_bp.route('/<int:record_id>', methods=['DELETE'])
def delete_exercise_record_api(record_id):
   
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"error": "user_id 為必填欄位"}), 400
        result = delete_exercise_record(user_id, record_id)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@exercise_bp.route('/food/exercise/calculator', methods=['GET'])
def exercise_calculator_api():

    from app.db import get_db_connection
    calories = float(request.args.get('calories', 0))
    user_id = request.args.get('user_id', type=int)
    weight = 60
    if user_id:
        w = get_user_weight(user_id)
        if w:
            weight = w
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT Exercise_Name, MET FROM ExerciseItem")
        items = cursor.fetchall()
    conn.close()
    exercises = []
    for item in items:
        met = float(item['MET'])
        if met > 0:
            minutes = round((calories / (met * weight)) * 60)
            exercises.append({'type': item['Exercise_Name'], 'duration': minutes})
    return jsonify({'exercises': exercises}) 