#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版API测试
"""

import requests
import json

def test_api():
    """测试API连接"""
    print("=== 测试Tushare API连接 ===")
    
    token = "46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"
    base_url = "http://api.tushare.pro"
    
    # 标准POST请求
    payload = {
        "api_name": "stock_basic",
        "token": token,
        "params": {"list_status": "L"}
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print("发送请求...")
        response = requests.post(base_url, json=payload, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result['code'] == 0:
                stock_count = len(result['data']['items'])
                print(f"[SUCCESS] 成功获取 {stock_count} 只股票")
                
                # 显示前3只股票
                print("股票列表示例:")
                for i in range(min(3, len(result['data']['items']))):
                    stock = result['data']['items'][i]
                    print(f"  {stock[0]}: {stock[2]}")
                
                return True
            else:
                print(f"[ERROR] API错误: {result['msg']}")
        elif response.status_code == 405:
            print("[ERROR] HTTP 405错误: Method Not Allowed")
        else:
            print(f"[ERROR] HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
    
    return False

if __name__ == "__main__":
    print("API连接测试")
    print("=" * 50)
    
    success = test_api()
    
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] 测试成功！")
        print("HTTP 405错误已修复")
        print("现在可以运行修复后的版本进行数据下载")
    else:
        print("[FAILED] 测试失败")