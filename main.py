#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票分析工具主程序

功能：
1. A股数据获取和分析
2. 技术指标计算
3. 数据可视化
4. 回测功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.china_stock_fetcher import ChinaStockFetcher
from indicators.technical_indicators import TechnicalIndicators
from visualization.chart_plotter import ChartPlotter

def analyze_a_stock():
    """分析单只A股"""
    print("\n=== A股个股分析 ===")
    
    # 示例：分析贵州茅台
    stock_name = "贵州茅台"
    symbol = "600519.SS"
    period = "1y"
    
    print(f"正在分析 {stock_name} ({symbol})...")
    
    try:
        # 获取A股数据
        fetcher = ChinaStockFetcher()
        data = fetcher.get_a_stock_data(symbol, period)
        
        if data is not None:
            print(f"✅ 成功获取 {len(data)} 条A股数据")
            print(f"   数据时间范围: {data.index[0]} 到 {data.index[-1]}")
            
            # 计算A股特有指标
            data = fetcher.calculate_a_stock_metrics(data)
            
            # 计算技术指标
            indicators = TechnicalIndicators(data)
            
            # 计算移动平均线
            data['MA5'] = indicators.moving_average(5)
            data['MA20'] = indicators.moving_average(20)
            data['MA60'] = indicators.moving_average(60)
            
            # 计算RSI
            data['RSI'] = indicators.rsi(14)
            
            # 显示最新数据
            latest_data = data.iloc[-1]
            print(f"\n📊 最新数据:")
            print(f"   收盘价: {latest_data['Close']:.2f}")
            print(f"   涨跌幅: {latest_data['Change']:.2f}%")
            print(f"   5日移动平均: {latest_data['MA5']:.2f}")
            print(f"   20日移动平均: {latest_data['MA20']:.2f}")
            print(f"   60日移动平均: {latest_data['MA60']:.2f}")
            print(f"   RSI(14): {latest_data['RSI']:.2f}")
            print(f"   乖离率(20): {latest_data['BIAS20']:.2f}%")
            
            # 生成图表
            plotter = ChartPlotter(data)
            plotter.plot_price_with_ma(stock_name)
            
        else:
            print("❌ 获取A股数据失败")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")

def analyze_index():
    """分析A股指数"""
    print("\n=== A股指数分析 ===")
    
    # 示例：分析上证指数
    index_name = "上证指数"
    period = "1y"
    
    print(f"正在分析 {index_name}...")
    
    try:
        fetcher = ChinaStockFetcher()
        data = fetcher.get_index_data(index_name, period)
        
        if data is not None:
            print(f"✅ 成功获取 {len(data)} 条指数数据")
            
            # 显示指数信息
            latest_data = data.iloc[-1]
            print(f"\n📈 指数最新数据:")
            print(f"   收盘点位: {latest_data['Close']:.2f}")
            print(f"   涨跌幅: {latest_data['Change']:.2f}%")
            print(f"   振幅: {latest_data['Amplitude']:.2f}%")
            
            # 生成图表
            plotter = ChartPlotter(data)
            plotter.plot_price_with_ma(index_name)
            
        else:
            print("❌ 获取指数数据失败")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")

def show_popular_stocks():
    """显示热门A股"""
    print("\n=== 热门A股列表 ===")
    
    fetcher = ChinaStockFetcher()
    
    print("热门A股股票:")
    for i, (name, symbol) in enumerate(fetcher.POPULAR_STOCKS.items(), 1):
        print(f"  {i:2d}. {name:8} ({symbol})")
    
    print("\n主要A股指数:")
    for i, (name, symbol) in enumerate(fetcher.INDEX_SYMBOLS.items(), 1):
        print(f"  {i:2d}. {name:8} ({symbol})")

def main():
    """主程序入口"""
    print("=== A股股票分析工具 ===")
    print("功能：")
    print("1. 分析单只A股")
    print("2. 分析A股指数")
    print("3. 查看热门A股")
    print("4. 技术指标计算")
    print("5. 数据可视化")
    print()
    
    # 显示热门A股
    show_popular_stocks()
    
    # 分析示例A股
    analyze_a_stock()
    
    # 分析示例指数
    analyze_index()
    
    print("\n🎯 A股分析工具已就绪！")
    print("💡 提示: 您可以修改代码中的股票代码和时间周期来定制分析")

if __name__ == "__main__":
    main()