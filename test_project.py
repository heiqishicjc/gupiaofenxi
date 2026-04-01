#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目功能测试脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_data_fetcher():
    """测试数据获取模块"""
    print("=== 测试数据获取模块 ===")
    
    try:
        from data.data_fetcher import StockDataFetcher
        
        fetcher = StockDataFetcher()
        data = fetcher.get_stock_data('AAPL', period='1mo', use_cache=False)
        
        if data is not None:
            print(f"✅ 成功获取AAPL数据，共{len(data)}条记录")
            print(f"   数据时间范围: {data.index[0]} 到 {data.index[-1]}")
            print(f"   最新收盘价: {data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ 数据获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据获取模块测试失败: {e}")
        return False

def test_technical_indicators():
    """测试技术指标模块"""
    print("\n=== 测试技术指标模块 ===")
    
    try:
        import pandas as pd
        import numpy as np
        from indicators.technical_indicators import TechnicalIndicators
        
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        test_data = pd.DataFrame({
            'Open': prices + np.random.randn(100) * 0.1,
            'High': prices + np.abs(np.random.randn(100) * 0.2),
            'Low': prices - np.abs(np.random.randn(100) * 0.2),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        indicators = TechnicalIndicators(test_data)
        
        # 测试移动平均线
        ma20 = indicators.moving_average(20)
        print(f"✅ 移动平均线计算成功，长度: {len(ma20)}")
        
        # 测试RSI
        rsi = indicators.rsi(14)
        print(f"✅ RSI计算成功，长度: {len(rsi)}")
        
        # 测试MACD
        macd_line, signal_line, histogram = indicators.macd()
        print(f"✅ MACD计算成功，长度: {len(macd_line)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 技术指标模块测试失败: {e}")
        return False

def test_helpers():
    """测试工具函数模块"""
    print("\n=== 测试工具函数模块 ===")
    
    try:
        from utils.helpers import validate_stock_data, format_currency, format_percentage
        import pandas as pd
        
        # 测试数据验证
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [103, 104, 105],
            'Volume': [1000000, 2000000, 3000000]
        })
        
        is_valid, message = validate_stock_data(test_data)
        print(f"✅ 数据验证测试: {message}")
        
        # 测试格式化函数
        currency_str = format_currency(1234567)
        percentage_str = format_percentage(12.34)
        print(f"✅ 货币格式化: {currency_str}")
        print(f"✅ 百分比格式化: {percentage_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具函数模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试股票分析工具项目...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # 运行测试
    if test_data_fetcher():
        tests_passed += 1
    
    if test_technical_indicators():
        tests_passed += 1
    
    if test_helpers():
        tests_passed += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"测试完成: {tests_passed}/{total_tests} 个测试通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！项目功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)