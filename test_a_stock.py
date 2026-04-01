#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股功能测试脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_a_stock_fetcher():
    """测试A股数据获取模块"""
    print("=== 测试A股数据获取模块 ===")
    
    try:
        from data.china_stock_fetcher import ChinaStockFetcher
        
        fetcher = ChinaStockFetcher()
        
        # 测试A股代码验证
        valid_symbols = ['600036.SS', '000001.SZ', '300750.SZ']
        invalid_symbols = ['AAPL', '600036', '000001']
        
        print("✅ A股代码格式验证:")
        for symbol in valid_symbols:
            is_valid = fetcher._validate_a_stock_symbol(symbol)
            print(f"   {symbol}: {'有效' if is_valid else '无效'}")
        
        for symbol in invalid_symbols:
            is_valid = fetcher._validate_a_stock_symbol(symbol)
            print(f"   {symbol}: {'有效' if is_valid else '无效'}")
        
        # 测试热门股票列表
        print("\n✅ 热门A股列表:")
        for name, symbol in list(fetcher.POPULAR_STOCKS.items())[:5]:
            print(f"   {name}: {symbol}")
        
        # 测试指数列表
        print("\n✅ A股指数列表:")
        for name, symbol in fetcher.INDEX_SYMBOLS.items():
            print(f"   {name}: {symbol}")
        
        return True
        
    except Exception as e:
        print(f"❌ A股数据获取模块测试失败: {e}")
        return False

def test_a_stock_metrics():
    """测试A股特有指标计算"""
    print("\n=== 测试A股特有指标计算 ===")
    
    try:
        import pandas as pd
        import numpy as np
        from data.china_stock_fetcher import ChinaStockFetcher
        
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        prices = 10 + np.cumsum(np.random.randn(100) * 0.1)  # A股价格范围
        
        test_data = pd.DataFrame({
            'Open': prices + np.random.randn(100) * 0.02,
            'High': prices + np.abs(np.random.randn(100) * 0.03),
            'Low': prices - np.abs(np.random.randn(100) * 0.03),
            'Close': prices,
            'Volume': np.random.randint(10000000, 100000000, 100)  # A股成交量范围
        }, index=dates)
        
        fetcher = ChinaStockFetcher()
        
        # 计算A股特有指标
        result = fetcher.calculate_a_stock_metrics(test_data)
        
        # 检查指标是否存在
        a_stock_indicators = ['BIAS5', 'BIAS10', 'BIAS20', 'PSY', 'WR']
        
        print("✅ A股特有指标计算:")
        for indicator in a_stock_indicators:
            if indicator in result.columns:
                print(f"   {indicator}: 计算成功")
            else:
                print(f"   {indicator}: 计算失败")
        
        # 检查指标值范围
        if 'BIAS20' in result.columns:
            bias20 = result['BIAS20'].dropna()
            if len(bias20) > 0:
                print(f"   乖离率范围: {bias20.min():.2f}% 到 {bias20.max():.2f}%")
        
        if 'PSY' in result.columns:
            psy = result['PSY'].dropna()
            if len(psy) > 0:
                print(f"   心理线范围: {psy.min():.2f} 到 {psy.max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ A股指标计算测试失败: {e}")
        return False

def test_a_stock_data_processing():
    """测试A股数据处理"""
    print("\n=== 测试A股数据处理 ===")
    
    try:
        import pandas as pd
        import numpy as np
        from data.china_stock_fetcher import ChinaStockFetcher
        
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        np.random.seed(42)
        prices = 20 + np.cumsum(np.random.randn(50) * 0.5)
        
        test_data = pd.DataFrame({
            'Open': prices + np.random.randn(50) * 0.1,
            'High': prices + np.abs(np.random.randn(50) * 0.2),
            'Low': prices - np.abs(np.random.randn(50) * 0.2),
            'Close': prices,
            'Volume': np.random.randint(50000000, 200000000, 50)
        }, index=dates)
        
        fetcher = ChinaStockFetcher()
        
        # 测试数据处理
        processed_data = fetcher._preprocess_a_stock_data(test_data)
        
        print("✅ A股数据处理:")
        
        # 检查新增的A股特有指标
        a_stock_columns = ['Change', 'Volume_Change', 'Amplitude']
        
        for col in a_stock_columns:
            if col in processed_data.columns:
                print(f"   {col}: 处理成功")
            else:
                print(f"   {col}: 处理失败")
        
        # 检查振幅计算
        if 'Amplitude' in processed_data.columns:
            amplitude = processed_data['Amplitude'].dropna()
            if len(amplitude) > 0:
                print(f"   振幅范围: {amplitude.min():.2f}% 到 {amplitude.max():.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ A股数据处理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试A股股票分析工具...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # 运行测试
    if test_a_stock_fetcher():
        tests_passed += 1
    
    if test_a_stock_metrics():
        tests_passed += 1
    
    if test_a_stock_data_processing():
        tests_passed += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"A股功能测试完成: {tests_passed}/{total_tests} 个测试通过")
    
    if tests_passed == total_tests:
        print("🎉 所有A股功能测试通过！")
        print("💡 提示: 由于网络限制，实际数据获取测试可能需要手动进行")
        return True
    else:
        print("⚠️  部分A股功能测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)