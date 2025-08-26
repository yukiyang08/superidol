#!/usr/bin/env python3
"""
FoodSearch 效能測試腳本
用於測試優化前後的查詢效能
"""

import time
import requests
import statistics
from typing import List, Dict
import json

class SearchPerformanceTester:
    """搜尋效能測試器"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
    
    def test_search_query(self, filters: Dict, test_name: str, iterations: int = 10) -> Dict:
        """
        測試特定搜尋查詢的效能
        
        Args:
            filters: 搜尋過濾條件
            test_name: 測試名稱
            iterations: 測試次數
        
        Returns:
            測試結果字典
        """
        print(f"\n🧪 測試: {test_name}")
        print(f"📊 過濾條件: {json.dumps(filters, ensure_ascii=False, indent=2)}")
        
        response_times = []
        success_count = 0
        error_count = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                # 構建查詢參數
                params = []
                for key, value in filters.items():
                    if value is not None and value != '':
                        if isinstance(value, list):
                            params.append(f"{key}={','.join(map(str, value))}")
                        else:
                            params.append(f"{key}={value}")
                
                query_string = '&'.join(params)
                url = f"{self.base_url}/api/food/?{query_string}"
                
                # 發送請求
                response = requests.get(url, timeout=30)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # 轉換為毫秒
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    success_count += 1
                    print(f"  ✅ 第 {i+1} 次: {response_time:.2f}ms")
                else:
                    error_count += 1
                    print(f"  ❌ 第 {i+1} 次: HTTP {response.status_code}")
                
            except Exception as e:
                error_count += 1
                print(f"  ❌ 第 {i+1} 次: {str(e)}")
        
        # 計算統計資料
        if response_times:
            stats = {
                'test_name': test_name,
                'filters': filters,
                'iterations': iterations,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': (success_count / iterations) * 100,
                'response_times_ms': response_times,
                'min_time': min(response_times),
                'max_time': max(response_times),
                'avg_time': statistics.mean(response_times),
                'median_time': statistics.median(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            }
        else:
            stats = {
                'test_name': test_name,
                'filters': filters,
                'iterations': iterations,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': 0,
                'response_times_ms': [],
                'min_time': 0,
                'max_time': 0,
                'avg_time': 0,
                'median_time': 0,
                'std_dev': 0
            }
        
        self.test_results.append(stats)
        return stats
    
    def print_test_summary(self, test_result: Dict):
        """印出測試結果摘要"""
        print(f"\n📈 測試結果摘要: {test_result['test_name']}")
        print(f"   🔄 測試次數: {test_result['iterations']}")
        print(f"   ✅ 成功次數: {test_result['success_count']}")
        print(f"   ❌ 失敗次數: {test_result['error_count']}")
        print(f"   📊 成功率: {test_result['success_rate']:.1f}%")
        
        if test_result['response_times_ms']:
            print(f"   ⏱️  響應時間統計 (毫秒):")
            print(f"     最小: {test_result['min_time']:.2f}")
            print(f"     最大: {test_result['max_time']:.2f}")
            print(f"     平均: {test_result['avg_time']:.2f}")
            print(f"     中位數: {test_result['median_time']:.2f}")
            print(f"     標準差: {test_result['std_dev']:.2f}")
        else:
            print("   ⚠️  無成功的響應時間資料")
    
    def run_performance_tests(self):
        """執行所有效能測試"""
        print("🚀 開始 FoodSearch 效能測試")
        print("=" * 50)
        
        # 測試案例 1: 基本搜尋（無過濾條件）
        self.test_search_query(
            filters={},
            test_name="基本搜尋（無過濾）",
            iterations=5
        )
        
        # 測試案例 2: 名稱搜尋
        self.test_search_query(
            filters={'name': '雞肉'},
            test_name="名稱搜尋",
            iterations=10
        )
        
        # 測試案例 3: 價格範圍搜尋
        self.test_search_query(
            filters={'priceMin': 50, 'priceMax': 200},
            test_name="價格範圍搜尋",
            iterations=10
        )
        
        # 測試案例 4: 熱量範圍搜尋
        self.test_search_query(
            filters={'calMin': 300, 'calMax': 800},
            test_name="熱量範圍搜尋",
            iterations=10
        )
        
        # 測試案例 5: 複合條件搜尋
        self.test_search_query(
            filters={
                'name': '雞肉',
                'priceMax': 200,
                'calMax': 600,
                'food_type': ['主餐', '小菜']
            },
            test_name="複合條件搜尋",
            iterations=10
        )
        
        # 測試案例 6: 餐廳搜尋
        self.test_search_query(
            filters={'restaurant': '麥當勞'},
            test_name="餐廳搜尋",
            iterations=10
        )
        
        # 測試案例 7: 大量結果搜尋
        self.test_search_query(
            filters={'priceMax': 500},
            test_name="大量結果搜尋",
            iterations=5
        )
        
        # 印出所有測試結果
        self.print_all_results()
    
    def print_all_results(self):
        """印出所有測試結果的比較"""
        print("\n" + "=" * 60)
        print("📊 所有測試結果比較")
        print("=" * 60)
        
        # 按平均響應時間排序
        sorted_results = sorted(self.test_results, key=lambda x: x['avg_time'])
        
        print(f"{'測試名稱':<20} {'平均時間(ms)':<12} {'成功率(%)':<10} {'測試次數':<8}")
        print("-" * 60)
        
        for result in sorted_results:
            print(f"{result['test_name']:<20} {result['avg_time']:<12.2f} {result['success_rate']:<10.1f} {result['iterations']:<8}")
        
        # 計算整體統計
        all_times = []
        total_success = 0
        total_tests = 0
        
        for result in self.test_results:
            all_times.extend(result['response_times_ms'])
            total_success += result['success_count']
            total_tests += result['iterations']
        
        if all_times:
            print("\n🎯 整體效能統計:")
            print(f"   總測試次數: {total_tests}")
            print(f"   總成功次數: {total_success}")
            print(f"   整體成功率: {(total_success/total_tests)*100:.1f}%")
            print(f"   所有響應時間平均: {statistics.mean(all_times):.2f}ms")
            print(f"   所有響應時間中位數: {statistics.median(all_times):.2f}ms")
            print(f"   最快響應時間: {min(all_times):.2f}ms")
            print(f"   最慢響應時間: {max(all_times):.2f}ms")
    
    def export_results(self, filename: str = "search_performance_results.json"):
        """匯出測試結果到 JSON 檔案"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 測試結果已匯出到: {filename}")
        except Exception as e:
            print(f"\n❌ 匯出失敗: {e}")

def main():
    """主函數"""
    print("🍔 FoodSearch 效能測試工具")
    print("請確保後端服務正在運行在 http://localhost:5000")
    
    # 創建測試器
    tester = SearchPerformanceTester()
    
    try:
        # 執行測試
        tester.run_performance_tests()
        
        # 匯出結果
        tester.export_results()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  測試被用戶中斷")
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
    
    print("\n✨ 效能測試完成！")

if __name__ == "__main__":
    main() 