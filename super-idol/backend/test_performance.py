#!/usr/bin/env python3
"""
推薦系統性能測試腳本
"""

import time
import requests
import statistics

def test_recommendation_performance(user_id=23, test_count=5):
    """
    測試推薦API的性能
    
    Args:
        user_id: 測試用戶ID
        test_count: 測試次數
    """
    url = f"http://localhost:5000/api/food/recommend?user_id={user_id}"
    response_times = []
    recommendation_counts = []
    
    print(f"開始測試推薦系統性能...")
    print(f"測試用戶ID: {user_id}")
    print(f"測試次數: {test_count}")
    print("-" * 50)
    
    for i in range(test_count):
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 轉換為毫秒
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                total_recommendations = sum(len(cat.get('foods', [])) for cat in categories)
                recommendation_counts.append(total_recommendations)
                
                print(f"測試 {i+1}: {response_time:.1f}ms | "
                      f"推薦類別: {len(categories)} | "
                      f"總推薦數: {total_recommendations}")
                
                # 顯示每個類別的詳細信息
                for j, category in enumerate(categories):
                    print(f"  - {category.get('title', '未知')}: {len(category.get('foods', []))} 項")
                    
            else:
                print(f"測試 {i+1}: 請求失敗 (HTTP {response.status_code})")
                
        except requests.RequestException as e:
            print(f"測試 {i+1}: 網路錯誤 - {e}")
        except Exception as e:
            print(f"測試 {i+1}: 未知錯誤 - {e}")
        
        print()
    
    # 計算統計資料
    if response_times:
        print("=" * 50)
        print("性能統計結果:")
        print(f"平均回應時間: {statistics.mean(response_times):.1f}ms")
        print(f"最快回應時間: {min(response_times):.1f}ms")
        print(f"最慢回應時間: {max(response_times):.1f}ms")
        
        if len(response_times) > 1:
            print(f"回應時間標準差: {statistics.stdev(response_times):.1f}ms")
        
        if recommendation_counts:
            print(f"平均推薦數量: {statistics.mean(recommendation_counts):.1f}")
            print(f"推薦數量範圍: {min(recommendation_counts)} - {max(recommendation_counts)}")
        
        # 性能評級
        avg_time = statistics.mean(response_times)
        if avg_time < 200:
            grade = "優秀 🟢"
        elif avg_time < 500:
            grade = "良好 🟡"
        elif avg_time < 1000:
            grade = "普通 🟠"
        else:
            grade = "需要優化 🔴"
            
        print(f"性能評級: {grade}")
    else:
        print("測試失敗：沒有成功的回應")

if __name__ == "__main__":
    test_recommendation_performance() 