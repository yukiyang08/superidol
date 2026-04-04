#!/usr/bin/env python3
"""測試餐廳篩選功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db import get_db_connection, return_db_connection

def test_mcdonald():
    """測試麥當勞的食物"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 查詢所有餐廳
        print("=" * 50)
        print("1. 檢查所有餐廳")
        print("=" * 50)
        cursor.execute("SELECT RestaurantID, Name FROM Restaurant LIMIT 10")
        restaurants = cursor.fetchall()
        for r in restaurants:
            print(f"  ID: {r['RestaurantID']}, Name: {r['Name']}")
        
        # 2. 查詢麥當勞的食物數量
        print("\n" + "=" * 50)
        print("2. 檢查麥當勞的食物")
        print("=" * 50)
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM Food f
            LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
            WHERE r.Name LIKE '%麥當勞%'
        """)
        result = cursor.fetchone()
        count = result['cnt'] if result else 0
        print(f"  麥當勞食物數量: {count}")
        
        # 3. 顯示麥當勞的食物樣本
        if count > 0:
            print("\n  樣本食物:")
            cursor.execute("""
                SELECT f.FoodID, f.Name, f.Price, r.Name as Restaurant
                FROM Food f
                LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
                WHERE r.Name LIKE '%麥當勞%'
                LIMIT 5
            """)
            foods = cursor.fetchall()
            for food in foods:
                print(f"    ID: {food['FoodID']}, Name: {food['Name']}, Price: {food['Price']}, Restaurant: {food['Restaurant']}")
        
        # 4. 查詢所有食物中有多少沒有關聯餐廳（RestaurantID = NULL）
        print("\n" + "=" * 50)
        print("3. 檢查沒有餐廳的食物")
        print("=" * 50)
        cursor.execute("SELECT COUNT(*) as cnt FROM Food WHERE RestaurantID IS NULL")
        result = cursor.fetchone()
        null_count = result['cnt'] if result else 0
        print(f"  沒有關聯餐廳的食物: {null_count}")
        
        # 5. 查詢所有食物總數
        print("\n" + "=" * 50)
        print("4. 食物總數")
        print("=" * 50)
        cursor.execute("SELECT COUNT(*) as cnt FROM Food")
        result = cursor.fetchone()
        total_count = result['cnt'] if result else 0
        print(f"  所有食物數量: {total_count}")
        
        # 6. 顯示各餐廳的食物數量
        print("\n" + "=" * 50)
        print("5. 各餐廳的食物數量")
        print("=" * 50)
        cursor.execute("""
            SELECT COALESCE(r.Name, '未指定餐廳') as RestaurantName, COUNT(*) as FoodCount
            FROM Food f
            LEFT JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
            GROUP BY f.RestaurantID, r.Name
            ORDER BY FoodCount DESC
        """)
        stats = cursor.fetchall()
        for stat in stats:
            print(f"  {stat['RestaurantName']}: {stat['FoodCount']} 件食物")
        
    finally:
        cursor.close()
        return_db_connection(conn)

if __name__ == '__main__':
    test_mcdonald()
