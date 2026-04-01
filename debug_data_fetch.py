#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取调试脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_import():
    """测试基本导入"""
    print("=== 测试基本导入 ===")
    try:
        from data.china_stock_fetcher import ChinaStockFetcher
        print("✅ ChinaStockFetcher 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_yfinance():
    """测试yfinance库"""
    print("\n=== 测试yfinance库 ===")
    try:
        import yfinance as yf
        print("✅ yfinance 导入成功")
        
        # 测试简单的yfinance功能
        ticker = yf.Ticker("000001.SS")
        info = ticker.info
        print("✅ yfinance Ticker创建成功")
        
        return True
    except Exception as e:
        print(f"❌ yfinance测试失败: {e}")
        return False

def test_network_connection():
    """测试网络连接"""
    print("\n=== 测试网络连接 ===")
    try:
        import requests
        
        # 测试连接到yahoo finance
        response = requests.get("https://finance.yahoo.com", timeout=10)
        if response.status_code == 200:
            print("✅ 网络连接正常")
            return True
        else:
            print(f"❌ 网络连接异常，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 网络连接测试失败: {e}")
        return False

def test_simple_data_fetch():
    """测试简单数据获取"""
    print("\n=== 测试简单数据获取 ===")
    try:
        from data.china_stock_fetcher import ChinaStockFetcher
        
        fetcher = ChinaStockFetcher()
        print("✅ 数据获取器创建成功")
        
        # 使用非常短的周期测试
        data = fetcher.get_a_stock_data("000001.SS", period="5d", use_cache=False)
        
        if data is not None:
            print(f"✅ 数据获取成功，共{len(data)}条记录")
            if len(data) > 0:
                print(f"   最新收盘价: {data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ 数据获取返回None")
            return False
            
    except Exception as e:
        print(f"❌ 数据获取测试失败: {e}")
        return False

def test_alternative_symbols():
    """测试替代的股票代码"""
    print("\n=== 测试替代股票代码 ===")
    
    # 尝试不同的A股代码格式
    test_symbols = [
        "000001.SS",  # 上证指数
        "399001.SZ",  # 深证成指
        "600036.SS",  # 招商银行
        "000858.SZ",  # 五粮液
    ]
    
    from data.china_stock_fetcher import ChinaStockFetcher
    fetcher = ChinaStockFetcher()
    
    for symbol in test_symbols:
        try:
            print(f"\n测试 {symbol}...")
            data = fetcher.get_a_stock_data(symbol, period="5d", use_cache=False)
            
            if data is not None and not data.empty:
                print(f"✅ {symbol} 数据获取成功")
                print(f"   记录数: {len(data)}")
                print(f"   最新价: {data['Close'].iloc[-1]:.2f}")
                return True
            else:
                print(f"❌ {symbol} 数据获取失败")
                
        except Exception as e:
            print(f"❌ {symbol} 测试异常: {e}")
    
    return False

def main():
    """主调试函数"""
    print("开始调试A股数据获取问题...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # 运行测试
    if test_basic_import():
        tests_passed += 1
    
    if test_yfinance():
        tests_passed += 1
    
    if test_network_connection():
        tests_passed += 1
    
    if test_simple_data_fetch():
        tests_passed += 1
    
    if test_alternative_symbols():
        tests_passed += 1
    
    # 输出诊断结果
    print("\n" + "=" * 50)
    print(f"诊断完成: {tests_passed}/{total_tests} 个测试通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！数据获取功能正常")
    else:
        print("\n🔍 问题诊断:")
        
        if tests_passed < 3:
            print("❌ 基本环境配置有问题")
            print("💡 建议: 检查Python环境和依赖包安装")
        
        if tests_passed >= 3 and tests_passed < 5:
            print("❌ 数据获取功能可能受网络或API限制")
            print("💡 建议:")
            print("   1. 检查网络连接")
            print("   2. 尝试使用VPN")
            print("   3. 稍后重试（API可能有限制）")
    
    print("\n💡 临时解决方案:")
    print("   1. 使用本地数据文件进行分析")
    print("   2. 联系我为您创建离线分析版本")

if __name__ == "__main__":
    main()