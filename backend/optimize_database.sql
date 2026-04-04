-- 資料庫效能優化腳本
-- 為 FoodSearch 功能添加必要的索引

-- 1. 為 Food 表添加複合索引
-- 價格範圍查詢優化
CREATE INDEX idx_food_price_range ON Food(Price) USING BTREE;

-- 熱量範圍查詢優化
CREATE INDEX idx_food_calories_range ON Food(Calories) USING BTREE;

-- 名稱搜尋優化（支援 LIKE 查詢）
CREATE INDEX idx_food_name_search ON Food(Name) USING BTREE;

-- 食物類型查詢優化
CREATE INDEX idx_food_type ON Food(Food_Type) USING BTREE;

-- 複合索引：餐廳 + 價格（常用查詢組合）
CREATE INDEX idx_food_restaurant_price ON Food(RestaurantID, Price) USING BTREE;

-- 複合索引：餐廳 + 熱量（常用查詢組合）
CREATE INDEX idx_food_restaurant_calories ON Food(RestaurantID, Calories) USING BTREE;

-- 複合索引：食物類型 + 價格（常用查詢組合）
CREATE INDEX idx_food_type_price ON Food(Food_Type, Price) USING BTREE;

-- 複合索引：食物類型 + 熱量（常用查詢組合）
CREATE INDEX idx_food_type_calories ON Food(Food_Type, Calories) USING BTREE;

-- 2. 為 Restaurant 表添加索引
CREATE INDEX idx_restaurant_name ON Restaurant(Name) USING BTREE;

-- 3. 為 Food_Records 表添加索引（推薦系統使用）
CREATE INDEX idx_food_records_user_date ON Food_Records(UserID, Date) USING BTREE;
CREATE INDEX idx_food_records_food_user ON Food_Records(FoodID, UserID) USING BTREE;

-- 4. 為 My_Favorite 表添加索引
CREATE INDEX idx_my_favorite_user_food ON My_Favorite(UserID, FoodID) USING BTREE;

-- 5. 為偏好表添加索引
CREATE INDEX idx_food_preference_user_type ON Food_Preference(UserID, Food_Type) USING BTREE;
CREATE INDEX idx_restaurant_preference_user ON Restaurant_Preference(UserID, RestaurantID) USING BTREE;

-- 6. 分析表統計資訊（MySQL 8.0+）
ANALYZE TABLE Food;
ANALYZE TABLE Restaurant;
ANALYZE TABLE Food_Records;
ANALYZE TABLE My_Favorite;
ANALYZE TABLE Food_Preference;
ANALYZE TABLE Restaurant_Preference;

-- 7. 檢查索引使用情況
-- 執行以下查詢來檢查索引是否被使用：
-- EXPLAIN SELECT f.FoodID, f.Name, f.Calories, f.Price, f.Food_Type, r.Name AS Restaurant
-- FROM Food f
-- LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
-- WHERE f.Price BETWEEN 50 AND 200 
--   AND f.Calories BETWEEN 300 AND 800
--   AND f.Name LIKE '%雞肉%'
--   AND f.Food_Type IN ('主餐', '小菜')
-- ORDER BY f.FoodID LIMIT 50; 