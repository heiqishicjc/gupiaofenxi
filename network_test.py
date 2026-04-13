#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络连接测试工具
用于诊断Tushare API连接问题
"""

import requests
import socket
import time

def test_dns_resolution():
    """测试DNS解析"""
    print("\n🔍 测试DNS解析...")
    
    domains = ["api.tushare.pro", "github.com", "baidu.com"]
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"   ✅ {domain} -> {ip}")
        except socket.gaierror as e:
            print(f"   ❌ {domain}: DNS解析失败 - {e}")

def test_http_connection():
    """测试HTTP连接"""
    print("\n🌐 测试HTTP连接...")
    
    urls = [
        "http://api.tushare.pro",
        "http://116.62.129.122",
        "http://47.107.33.27",
        "http://www.baidu.com"
    ]
    
    for url in urls:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                print(f"   ✅ {url} - 状态码: {response.status_code} (耗时: {end_time-start_time:.2f}s)")
            else:
                print(f"   ⚠️  {url} - 状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {url} - 连接失败: {type(e).__name__}")

def test_tushare_api():
    """测试Tushare API连接"""
    print("\n📊 测试Tushare API...")
    
    token = "46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"
    
    # 测试不同的服务器
    servers = [
        "http://api.tushare.pro",
        "http://116.62.129.122",
        "http://47.107.33.27"
    ]
    
    payload = {
        "api_name": "stock_basic",
        "token": token,
        "params": {"list_status": "L"}
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for server in servers:
        try:
            print(f"   测试服务器: {server}")
            response = requests.post(server, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    print(f"   ✅ API调用成功 - 返回数据条数: {len(result.get('data', {}).get('items', []))}")
                else:
                    print(f"   ⚠️  API错误: {result.get('msg')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 连接失败: {type(e).__name__}: {e}")

def main():
    print("=" * 50)
    print("网络连接诊断工具")
    print("=" * 50)
    
    test_dns_resolution()
    test_http_connection()
    test_tushare_api()
    
    print("\n" + "=" * 50)
    print("诊断完成")
    print("=" * 50)

if __name__ == "__main__":
    main()