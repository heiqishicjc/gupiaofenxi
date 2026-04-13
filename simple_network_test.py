#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单网络连接测试工具
"""

import requests
import socket
import time

def test_dns_resolution():
    """测试DNS解析"""
    print("\n测试DNS解析...")
    
    domains = ["api.tushare.pro", "github.com", "baidu.com"]
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"   SUCCESS {domain} -> {ip}")
        except socket.gaierror as e:
            print(f"   FAILED {domain}: DNS error - {e}")

def test_http_connection():
    """测试HTTP连接"""
    print("\n测试HTTP连接...")
    
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
                print(f"   SUCCESS {url} - Status: {response.status_code} (Time: {end_time-start_time:.2f}s)")
            else:
                print(f"   WARNING {url} - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   FAILED {url} - Error: {type(e).__name__}")

def main():
    print("=" * 50)
    print("网络连接诊断工具")
    print("=" * 50)
    
    test_dns_resolution()
    test_http_connection()
    
    print("\n" + "=" * 50)
    print("诊断完成")
    print("=" * 50)

if __name__ == "__main__":
    main()