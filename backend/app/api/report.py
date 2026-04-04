"""
Report API endpoints.
"""

from flask import Blueprint, request, jsonify
from app.services.report_service import get_summary_report
from flask_cors import CORS
import logging
from datetime import datetime, timedelta

report_bp = Blueprint('report', __name__)
CORS(report_bp)

@report_bp.route('/summary', methods=['GET'])
def summary_report_api():
    """
        獲取摘要報告
        ---
        tags:
            - Reports
        responses:
            200:
                description: 成功回傳報表資料
            400:
                description: 參數錯誤
            500:
                description: 伺服器錯誤
    """
    user_id = request.args.get('user_id')
    report_type = request.args.get('report_type')

    if not user_id:
        return jsonify({"error": "Missing required parameter: user_id"}), 400
    if not report_type:
        return jsonify({"error": "Missing required parameter: report_type"}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400
    
    if report_type not in ['daily', 'weekly', 'monthly', 'custom']:
        return jsonify({"error": "Invalid report_type. Must be 'daily', 'weekly', 'monthly', or 'custom'"}), 400

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # 日期格式驗證 (簡單示例，可進一步完善)
    try:
        if start_date_str:
            datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        # 注意：get_summary_report 函數簽名將包含 report_type
        report_data = get_summary_report(user_id, report_type, start_date_str, end_date_str)
        return jsonify(report_data), 200
    except Exception as e:
        logging.error(f"API error in /summary for user {user_id}, type {report_type}: {e}", exc_info=True)
        return jsonify({"error": "Error generating summary report"}), 500

@report_bp.route('/trends', methods=['GET'])
def get_trends():
    """
    Get user's trends over multiple weeks.
    """
    # TODO: Implement trend analysis
    return jsonify({"message": "Trends endpoint - to be implemented"}), 200 