from pydantic import BaseModel
from typing import Optional, Literal

class FoodItemCreate(BaseModel):
    name: str
    calories: float
    price: float
    food_type: Optional[Literal['Burger', 'Snacks', 'Beverages']] = None
    set_type: Literal['單點', '套餐']
    restaurant_id: int

class FoodItemUpdate(BaseModel):
    name: Optional[str] = None
    calories: Optional[float] = None
    price: Optional[float] = None
    food_type: Optional[Literal['Burger', 'Snacks', 'Beverages']] = None
    set_type: Optional[Literal['單點', '套餐']] = None
