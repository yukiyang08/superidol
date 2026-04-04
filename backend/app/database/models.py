from app.extensions import db

class FoodItem(db.Model):
    __tablename__ = 'Food'

    FoodID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Calories = db.Column(db.Numeric(10, 2), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Food_Type = db.Column(db.Enum('Burger', 'Snacks', 'Beverages'), nullable=True)
    Set_Type = db.Column(db.Enum('單點', '套餐'), nullable=False)
    RestaurantID = db.Column(db.Integer, db.ForeignKey('Restaurant.RestaurantID'), nullable=False)

class Restaurant(db.Model):
    __tablename__ = 'Restaurant'

    RestaurantID = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(100), nullable=True)
    Name = db.Column(db.String(255), nullable=True)
    AveragePrice = db.Column(db.Numeric(10, 2), nullable=True)

    # 一間餐廳可以有多個食物
    foods = db.relationship("FoodItem", backref="restaurant", lazy=True)