#!/usr/bin/env python3
"""驗證修復後的餐廳篩選"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.food_service import search_food

# 模擬前端搜尋麥當勞且設定了價格範圍的查詢
filters = {
    'name': '',
    'priceMin': '50',
    'priceMax': '300',
    'calMin': '',
    'calMax': '',
    'type': '',
    'restaurant': '麥當勞',
    'food_type': []
}

print("=" * 50)
print("搜尋麥當勞 + 價格 $50-300")
print("=" * 50)

results = search_food(filters)
print(f"找到 {len(results)} 件食物")

if len(results) > 0:
    print("\n樣本結果:")
    for i, item in enumerate(results[:5]):
        print(f"  {i+1}. {item['name']}")
        print(f"     價格: {item['price']}, 熱量: {item['calories']}, 餐廳: {item['restaurant']}")
else:
    print("\n❌ 仍然沒有找到食物")
