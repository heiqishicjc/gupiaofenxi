#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HTTP 405错误修复
"""

import requests
import json

def test_tushare_api():
    """测试Tushare API连接"""
    print("=== 测试Tushare API连接 ===")
    
    token = "46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"
    base_url = "http://api.tushare.pro"
    
    # 测试不同的请求方式
    test_cases = [
        {
            'name': '标准POST请求',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'data': {
                "api_name": "stock_basic",
                "token": token,
                "params": {"list_status": "L"}
            }
        },
        {
            'name': '带User-Agent的POST请求',
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'data': {
                "api_name": "stock_basic",
                "token": token,
                "params": {"list_status": "L"}
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n测试: {test['name']}")
        
        try:
            if test['method'] == 'POST':
                response = requests.post(
                    base_url, 
                    json=test['data'], 
                    headers=test['headers'],
                    timeout=10
                )
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result['code'] == 0:
                    stock_count = len(result['data']['items'])
                    print(f"  ✅ 成功获取 {stock_count} 只股票")
                    
                    # 显示前3只股票
                    print("  股票列表示例:")
                    for i in range(min(3, len(result['data']['items']))):
                        stock = result['data']['items'][i]
                        print(f"    {stock[0]}: {stock[2]}")
                    
                    return True, test['name']
                else:
                    print(f"  ❌ API错误: {result['msg']}")
            elif response.status_code == 405:
                print("  ❌ HTTP 405错误: Method Not Allowed")
                print(f"  响应内容: {response.text[:200]}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                print(f"  响应内容: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
    
    return False, None

if __name__ == "__main__":
    print("HTTP 405错误修复测试")
    print("=" * 50)
    
    success, method = test_tushare_api()
    
    print("\n" + "=" * 50)
    if success:
        print(f"✅ 测试成功！")
        print(f"有效方法: {method}")
        print("\n现在可以运行修复后的版本进行数据下载")
    else:
        print("❌ 所有测试方法都失败")
        print("\n建议检查:")
        print("1. 网络连接")
        print("2. Tushare API服务状态")
        print("3. Token有效性")