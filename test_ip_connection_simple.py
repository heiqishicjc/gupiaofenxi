#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP直连测试脚本 - 验证Tushare API连接（简化版）
"""

import requests
import time

def test_ip_connection():
    """测试IP直连功能"""
    print("=== IP直连测试 ===")
    
    # Tushare API IP地址列表
    ip_addresses = [
        "116.62.129.122",  # Tushare API IP地址1
        "47.107.33.27",    # Tushare API IP地址2
        "api.tushare.pro"  # 域名（备用）
    ]
    
    token = "46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"
    
    for i, ip in enumerate(ip_addresses, 1):
        print(f"\n测试服务器 {i}: {ip}")
        
        # 构建URL
        if ip.startswith("api."):
            url = f"http://{ip}"
        else:
            url = f"http://{ip}"
        
        # 测试连接
        try:
            # 测试基本连接
            print(f"  测试基本连接...", end="")
            response = requests.get(url, timeout=5)
            print(" [OK] (连接成功)")
            
            # 测试API调用
            print(f"  测试API调用...", end="")
            payload = {
                "api_name": "stock_basic",
                "token": token,
                "params": {"list_status": "L"}
            }
            
            api_response = requests.post(url, json=payload, timeout=10)
            
            if api_response.status_code == 200:
                result = api_response.json()
                if result['code'] == 0:
                    stock_count = len(result['data']['items'])
                    print(f" [OK] (成功获取{stock_count}只股票)")
                    
                    # 显示前5只股票
                    print("  股票列表示例:")
                    for j in range(min(5, len(result['data']['items']))):
                        stock = result['data']['items'][j]
                        print(f"    {stock[0]}: {stock[2]} ({stock[1]})")
                    
                    return True, ip, stock_count
                else:
                    print(f" [ERROR] (API错误: {result['msg']})")
            else:
                print(f" [ERROR] (HTTP错误: {api_response.status_code})")
                
        except requests.exceptions.ConnectTimeout:
            print(" [ERROR] (连接超时)")
        except requests.exceptions.ConnectionError as e:
            print(f" [ERROR] (连接错误: {e})")
        except Exception as e:
            print(f" [ERROR] (未知错误: {e})")
        
        # 等待1秒再试下一个
        if i < len(ip_addresses):
            time.sleep(1)
    
    return False, None, 0

def test_dns_resolution():
    """测试DNS解析问题"""
    print("\n=== DNS解析测试 ===")
    
    test_urls = [
        "http://api.tushare.pro",
        "http://116.62.129.122",
        "http://47.107.33.27"
    ]
    
    for url in test_urls:
        print(f"\n测试 {url}...", end="")
        
        try:
            response = requests.get(url, timeout=5)
            print(" [OK] (DNS解析成功)")
        except requests.exceptions.ConnectionError as e:
            print(f" [ERROR] (DNS解析失败: {e})")
        except Exception as e:
            print(f" [ERROR] (其他错误: {e})")

if __name__ == "__main__":
    print("Tushare API IP直连测试工具")
    print("=" * 50)
    
    # 测试DNS解析
    test_dns_resolution()
    
    # 测试IP直连
    success, working_ip, stock_count = test_ip_connection()
    
    print("\n" + "=" * 50)
    if success:
        print(f"[SUCCESS] 测试成功！")
        print(f"可用服务器: {working_ip}")
        print(f"股票数量: {stock_count}")
        print("\n建议使用IP直连版本进行数据下载")
    else:
        print("[FAILED] 所有服务器测试失败")
        print("可能原因:")
        print("1. 网络连接问题")
        print("2. Tushare API服务暂时不可用")
        print("3. Token无效或过期")
        print("\n请检查网络连接后重试")