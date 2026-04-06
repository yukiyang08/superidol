"""
Report service functions.
"""

from app.db import get_db_connection
from datetime import datetime, timedelta, date as dt_date
import logging
import calendar


def build_actionable_suggestions(report_info: dict, user_goals: dict, period_summary: dict, daily_trends: list[dict]) -> list[dict]:
    """Build ranked, actionable suggestion cards based on period data."""
    num_days = max(1, report_info.get('num_days_in_period', 1))
    goal_daily_calories = user_goals.get('daily_calories', 2000) or 2000
    goal_period_calories = goal_daily_calories * num_days

    intake = period_summary.get('total_calories_intake', 0) or 0
    burned = period_summary.get('total_calories_burned', 0) or 0
    expense = period_summary.get('total_food_expense', 0) or 0
    daily_budget = user_goals.get('daily_budget', 0) or 0
    budget_period_goal = daily_budget * num_days

    net_diff = intake - burned - goal_period_calories
    cards = []

    if net_diff > 150:
        cards.append({
            'level': 'high',
            'title': '熱量偏高，優先做一項修正',
            'reason': f'此期間淨熱量約超出目標 {round(net_diff)} 大卡。',
            'action': '下一餐先減少 1 份主食或含糖飲，優先保留蛋白質來源。',
            'impact': f'若減少約 200 大卡，約可回收 {min(200, round(net_diff))} 大卡。'
        })
    elif net_diff < -200:
        cards.append({
            'level': 'medium',
            'title': '熱量偏低，避免恢復不足',
            'reason': f'此期間淨熱量約低於目標 {round(abs(net_diff))} 大卡。',
            'action': '可增加一份高蛋白點心（如無糖豆漿、雞蛋、優格）。',
            'impact': '每日補充 150~250 大卡可提升恢復與穩定度。'
        })
    else:
        cards.append({
            'level': 'good',
            'title': '熱量控制穩定',
            'reason': '此期間的熱量落在目標附近。',
            'action': '維持目前節奏，持續記錄每餐份量與飲料。',
            'impact': '穩定記錄可提升長期體重管理效果。'
        })

    if daily_budget > 0 and expense > budget_period_goal:
        over_budget = round(expense - budget_period_goal)
        cards.append({
            'level': 'medium',
            'title': '飲食支出略高於預算',
            'reason': f'目前約超出預算 {over_budget} 元。',
            'action': '本週可用「主食 + 蛋白質」組合取代高價套餐 1~2 次。',
            'impact': f'預估可回收約 {min(200, over_budget)} 元。'
        })

    total_exercise_minutes = period_summary.get('total_exercise_duration_minutes', 0) or 0
    if num_days >= 7 and total_exercise_minutes < 120:
        cards.append({
            'level': 'low',
            'title': '運動量可再提高',
            'reason': f'本期累積運動 {round(total_exercise_minutes)} 分鐘。',
            'action': '每次 20~30 分鐘快走或阻力訓練，每週再補 2~3 次。',
            'impact': '可提升熱量消耗與心肺健康。'
        })

    if not daily_trends:
        cards.append({
            'level': 'low',
            'title': '紀錄資料不足',
            'reason': '目前尚無足夠趨勢資料。',
            'action': '先連續記錄 3 天飲食與運動，再看趨勢會更準確。',
            'impact': '提升建議品質與可執行性。'
        })

    level_priority = {'high': 0, 'medium': 1, 'low': 2, 'good': 3}
    cards.sort(key=lambda c: level_priority.get(c.get('level', 'low'), 9))
    return cards[:3]

def get_user_goals(user_id: int, cursor) -> dict:
    """獲取用戶目標"""
    cursor.execute("SELECT WeekCalorieLimit, Budget, weight FROM Users WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        daily_calories_goal = (user['WeekCalorieLimit'] / 7) if user['WeekCalorieLimit'] else 0
        return {
            "daily_calories": round(daily_calories_goal) if daily_calories_goal else 2000, # 預設2000
            "daily_budget": round(user['Budget'] / 30) if user['Budget'] else 0, # 假設月預算轉日預算
            "user_weight_kg": user.get('weight') or 0 # 獲取體重，用於 MET 計算
            # TODO: 增加蛋白質、碳水、脂肪目標 (需 Users 表支援)
        }
    return {
        "daily_calories": 2000, # 預設值
        "daily_budget": 0,
        "user_weight_kg": 0
    }

def _determine_date_range(report_type: str, start_date_str: str | None, end_date_str: str | None) -> tuple[dt_date, dt_date]:
    today = dt_date.today()
    actual_start_date = None
    actual_end_date = None

    if report_type == 'daily':
        if start_date_str:
            actual_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            actual_start_date = today
        actual_end_date = actual_start_date
    elif report_type == 'weekly':
        if start_date_str:
            current_day = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            current_day = today
        actual_start_date = current_day - timedelta(days=current_day.weekday()) # Monday
        if end_date_str:
            temp_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if temp_end_date >= actual_start_date and (temp_end_date - actual_start_date).days <= 6:
                actual_end_date = temp_end_date
            else:
                actual_end_date = actual_start_date + timedelta(days=6)
        else:
            actual_end_date = actual_start_date + timedelta(days=6)
    elif report_type == 'monthly':
        if not start_date_str:
            raise ValueError("start_date is required for monthly report_type")
        # start_date_str 應為該月1日
        actual_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        year = actual_start_date.year
        month = actual_start_date.month
        last_day = calendar.monthrange(year, month)[1]
        actual_end_date = dt_date(year, month, last_day)
    elif report_type == 'custom':
        if not start_date_str or not end_date_str:
            raise ValueError("start_date and end_date are required for custom report_type")
        actual_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        actual_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if actual_end_date < actual_start_date:
            raise ValueError("end_date must be after start_date for custom report_type")
    else:
        raise ValueError(f"Unsupported report_type: {report_type}")
    return actual_start_date, actual_end_date

def get_food_summary_for_period(user_id: int, start_date: dt_date, end_date: dt_date, cursor) -> dict:
    """獲取每週食物相關摘要"""
    sql = """
        SELECT 
            SUM(COALESCE(f.Calories, fr.CustomCalories, 0) * fr.Quantity) AS total_calories_intake,
            SUM(COALESCE(f.Price, fr.CustomPrice, 0) * fr.Quantity) AS total_food_expense,
            COUNT(DISTINCT fr.Date) AS food_days_logged
            -- TODO: SUM(f.Protein * fr.Quantity) AS total_protein, etc. (需 Food 表支援)
        FROM Food_Records fr
        LEFT JOIN Food f ON fr.FoodID = f.FoodID
        WHERE fr.UserID = %s AND fr.Date BETWEEN %s AND %s
    """
    cursor.execute(sql, (user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    summary = cursor.fetchone()
    return {
        "total_calories_intake": round(summary['total_calories_intake']) if summary['total_calories_intake'] else 0,
        "total_food_expense": round(summary['total_food_expense']) if summary['total_food_expense'] else 0,
        "food_days_logged": summary['food_days_logged'] or 0
    }

def get_exercise_summary_for_period(user_id: int, start_date: dt_date, end_date: dt_date, user_weight_kg: float, cursor) -> dict:
    """獲取每週運動相關摘要"""
    sql = """
        SELECT 
            COUNT(er.RecordID) AS exercise_count,
            SUM(er.Duration) AS total_exercise_duration_minutes,
            SUM(
                CASE
                    WHEN u.weight IS NOT NULL AND ei.MET IS NOT NULL AND er.Duration IS NOT NULL
                    THEN ei.MET * u.weight * (er.Duration / 60.0)
                    ELSE 0
                END
            ) AS total_calories_burned
        FROM Exercise_Records er
        JOIN ExerciseItem ei ON er.Exercise_Name = ei.Exercise_Name
        JOIN Users u ON er.UserID = u.UserID
        WHERE er.UserID = %s AND er.Date BETWEEN %s AND %s
    """
    cursor.execute(sql, (user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    summary = cursor.fetchone()
    
    return {
        "exercise_count": summary['exercise_count'] or 0,
        "total_exercise_duration_minutes": round(summary['total_exercise_duration_minutes']) if summary['total_exercise_duration_minutes'] else 0,
        "total_calories_burned": round(summary['total_calories_burned']) if summary['total_calories_burned'] else 0
    }

def get_daily_trends_for_period(user_id: int, start_date_dt: dt_date, end_date_dt: dt_date, user_weight_kg: float, cursor) -> list:
    """獲取每日趨勢數據"""
    daily_trends = []
    current_date = start_date_dt
    while current_date <= end_date_dt:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # 每日食物數據
        food_sql = """
            SELECT 
                SUM(COALESCE(f.Calories, fr.CustomCalories, 0) * fr.Quantity) AS daily_calories_intake,
                SUM(COALESCE(f.Price, fr.CustomPrice, 0) * fr.Quantity) AS daily_food_expense
            FROM Food_Records fr
            LEFT JOIN Food f ON fr.FoodID = f.FoodID
            WHERE fr.UserID = %s AND fr.Date = %s
        """
        cursor.execute(food_sql, (user_id, date_str))
        food_day = cursor.fetchone()
        
        # 每日運動數據
        exercise_sql = """
            SELECT 
                SUM(er.Duration) AS daily_exercise_duration,
                SUM(
                    CASE
                        WHEN u.weight IS NOT NULL AND ei.MET IS NOT NULL AND er.Duration IS NOT NULL
                        THEN ei.MET * u.weight * (er.Duration / 60.0)
                        ELSE 0
                    END
                ) AS daily_calories_burned
            FROM Exercise_Records er
            JOIN ExerciseItem ei ON er.Exercise_Name = ei.Exercise_Name
            JOIN Users u ON er.UserID = u.UserID
            WHERE er.UserID = %s AND er.Date = %s
        """
        cursor.execute(exercise_sql, (user_id, date_str))
        exercise_day = cursor.fetchone()
        
        daily_trends.append({
            "date": date_str,
            "calories_intake": round(food_day['daily_calories_intake']) if food_day and food_day['daily_calories_intake'] else 0,
            "food_expense": round(food_day['daily_food_expense']) if food_day and food_day['daily_food_expense'] else 0,
            "exercise_duration_minutes": round(exercise_day['daily_exercise_duration']) if exercise_day and exercise_day['daily_exercise_duration'] else 0,
            "calories_burned": round(exercise_day['daily_calories_burned']) if exercise_day and exercise_day['daily_calories_burned'] else 0
        })
        current_date += timedelta(days=1)
    return daily_trends

def get_summary_report(user_id: int, report_type: str, start_date_str: str | None, end_date_str: str | None) -> dict:
    """生成指定時間段的摘要報告 (日報/週報/月報/自訂)"""
    conn = get_db_connection()
    try:
        actual_start_date, actual_end_date = _determine_date_range(report_type, start_date_str, end_date_str)
        weekly_summaries = []
        with conn.cursor() as cursor:
            user_goals_data = get_user_goals(user_id, cursor) 
            user_weight_kg = user_goals_data.get("user_weight_kg", 0) 

            food_summary = get_food_summary_for_period(user_id, actual_start_date, actual_end_date, cursor)
            exercise_summary = get_exercise_summary_for_period(user_id, actual_start_date, actual_end_date, user_weight_kg, cursor)
            daily_trends = get_daily_trends_for_period(user_id, actual_start_date, actual_end_date, user_weight_kg, cursor)

            # Calculate number of days in the report period for averages
            num_days_in_period = (actual_end_date - actual_start_date).days + 1

            period_summary = {
                **food_summary,
                **exercise_summary,
                "avg_daily_calories_intake": round(food_summary['total_calories_intake'] / num_days_in_period) if num_days_in_period > 0 and food_summary['total_calories_intake'] else 0,
                "avg_daily_calories_burned": round(exercise_summary['total_calories_burned'] / num_days_in_period) if num_days_in_period > 0 and exercise_summary['total_calories_burned'] else 0,
                "avg_daily_exercise_duration_minutes": round(exercise_summary['total_exercise_duration_minutes'] / num_days_in_period) if num_days_in_period > 0 and exercise_summary['total_exercise_duration_minutes'] else 0,
            }

            # 新增：月報告時，計算本月每週 summary
            if report_type == 'monthly':
                from datetime import timedelta
                week_start = actual_start_date
                while week_start <= actual_end_date:
                    week_end = min(week_start + timedelta(days=6), actual_end_date)
                    food_sum = get_food_summary_for_period(user_id, week_start, week_end, cursor)
                    exercise_sum = get_exercise_summary_for_period(user_id, week_start, week_end, user_weight_kg, cursor)
                    num_days = (week_end - week_start).days + 1
                    weekly_summaries.append({
                        "week_start": week_start.strftime('%Y-%m-%d'),
                        "week_end": week_end.strftime('%Y-%m-%d'),
                        "total_calories_intake": food_sum['total_calories_intake'],
                        "total_food_expense": food_sum['total_food_expense'],
                        "food_days_logged": food_sum['food_days_logged'],
                        "total_calories_burned": exercise_sum['total_calories_burned'],
                        "exercise_count": exercise_sum['exercise_count'],
                        "total_exercise_duration_minutes": exercise_sum['total_exercise_duration_minutes'],
                        "avg_daily_calories_intake": round(food_sum['total_calories_intake']/num_days) if num_days > 0 and food_sum['total_calories_intake'] else 0,
                        "avg_daily_calories_burned": round(exercise_sum['total_calories_burned']/num_days) if num_days > 0 and exercise_sum['total_calories_burned'] else 0,
                        "avg_daily_exercise_duration_minutes": round(exercise_sum['total_exercise_duration_minutes']/num_days) if num_days > 0 and exercise_sum['total_exercise_duration_minutes'] else 0,
                    })
                    week_start = week_end + timedelta(days=1)

            report = {
                "report_info": {
                    "type": report_type,
                    "actual_start_date": actual_start_date.strftime('%Y-%m-%d'),
                    "actual_end_date": actual_end_date.strftime('%Y-%m-%d'),
                    "num_days_in_period": num_days_in_period
                },
                "user_id": user_id,
                "user_profile": { # 新增 user_profile key
                    "weight_kg": user_weight_kg 
                },
                "user_goals": { # user_goals 只包含目標相關
                    "daily_calories": user_goals_data.get("daily_calories", 2000),
                    "daily_budget": user_goals_data.get("daily_budget", 0)
                    # TODO: "protein": user_goals_data.get("protein_goal", 0) 等
                },
                "period_summary": period_summary,
                "daily_trends": daily_trends,
                "suggestions": []
            }

            suggestion_cards = build_actionable_suggestions(
                report["report_info"],
                report["user_goals"],
                period_summary,
                daily_trends,
            )
            report["suggestion_cards"] = suggestion_cards
            report["suggestions"] = [card["title"] for card in suggestion_cards]

            if report_type == 'monthly':
                report["weekly_summaries"] = weekly_summaries
            return report
    except ValueError as ve:
        logging.error(f"ValueError in report generation: {ve}")
        raise # Re-raise to be caught by API layer for 400 type error
    except Exception as e:
        logging.error(f"Error generating {report_type} report for user {user_id}: {e}", exc_info=True)
        raise
    finally:
        conn.close()

def get_trends(user_id, weeks=4, end_date=None):
    """
    Get user's trends over multiple weeks.
    
    Args:
        user_id (int): User ID
        weeks (int, optional): Number of weeks to analyze. Defaults to 4.
        end_date (str, optional): End date (YYYY-MM-DD). Defaults to current date.
        
    Returns:
        dict: Trend analysis data
    """
    # TODO: Implement trend analysis
    return {
        "weekly_data": [],
        "total_calories_consumed": 0,
        "total_calories_burned": 0,
        "total_exercise_duration": 0,
        "average_unhealthy_expense": 0
    } 