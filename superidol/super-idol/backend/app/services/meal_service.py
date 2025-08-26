"""餐點服務模塊"""
from typing import Optional, List
from datetime import datetime
from ..database.models import Meal
from ..extensions import db
from ..schemas.meal import MealCreate, MealUpdate

class MealService:
    @staticmethod
    def get_meal_by_id(meal_id: int) -> Optional[Meal]:
        """根據 ID 獲取餐點"""
        return Meal.query.get(meal_id)

    @staticmethod
    def get_meals() -> List[Meal]:
        """獲取所有餐點"""
        return Meal.query.all()

    @staticmethod
    def create_meal(meal_data: MealCreate) -> Meal:
        """創建新餐點"""
        meal = Meal(**meal_data.dict())
        db.session.add(meal)
        db.session.commit()
        return meal

    @staticmethod
    def update_meal(meal: Meal, meal_data: MealUpdate) -> Meal:
        """更新餐點信息"""
        for key, value in meal_data.dict(exclude_unset=True).items():
            setattr(meal, key, value)
        meal.updated_at = datetime.utcnow()
        db.session.commit()
        return meal

    @staticmethod
    def delete_meal(meal: Meal) -> None:
        """刪除餐點"""
        db.session.delete(meal)
        db.session.commit() 