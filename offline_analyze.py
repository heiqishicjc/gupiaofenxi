#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线A股分析工具

使用模拟数据进行分析，无需网络连接
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from indicators.technical_indicators import TechnicalIndicators
from visualization.chart_plotter import ChartPlotter

class OfflineStockDataGenerator:
    """离线股票数据生成器"""
    
    def __init__(self):
        # A股基本信息
        self.a_stock_info = {
            "贵州茅台": {"symbol": "600519.SS", "base_price": 1600, "volatility": 0.02},
            "宁德时代": {"symbol": "300750.SZ", "base_price": 180, "volatility": 0.03},
            "五粮液": {"symbol": "000858.SZ", "base_price": 140, "volatility": 0.025},
            "中国平安": {"symbol": "601318.SS", "base_price": 45, "volatility": 0.015},
            "招商银行": {"symbol": "600036.SS", "base_price": 32, "volatility": 0.01},
            "上证指数": {"symbol": "000001.SS", "base_price": 3000, "volatility": 0.008},
            "深证成指": {"symbol": "399001.SZ", "base_price": 10000, "volatility": 0.009},
            "创业板指": {"symbol": "399006.SZ", "base_price": 2000, "volatility": 0.012}
        }
    
    def generate_stock_data(self, stock_name, days=252):
        """
        生成模拟股票数据
        
        Args:
            stock_name: 股票名称
            days: 生成的天数
            
        Returns:
            pandas.DataFrame: 模拟股票数据
        """
        if stock_name not in self.a_stock_info:
            print(f"❌ 不支持的股票: {stock_name}")
            return None
        
        info = self.a_stock_info[stock_name]
        
        # 生成日期范围（最近days个交易日）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days * 1.5)  # 考虑周末
        
        # 生成交易日（排除周末）
        dates = pd.bdate_range(start=start_date, end=end_date)[-days:]
        
        # 设置随机种子以确保可重复性
        np.random.seed(hash(stock_name) % 10000)
        
        # 生成价格序列（几何布朗运动）
        base_price = info['base_price']
        volatility = info['volatility']
        
        # 生成收益率（正态分布）
        returns = np.random.normal(0.0005, volatility, days)  # 日均收益率0.05%
        
        # 计算价格序列
        prices = base_price * np.exp(np.cumsum(returns))
        
        # 生成OHLC数据
        data = pd.DataFrame(index=dates)
        data['Close'] = prices
        
        # 生成开盘价（前一日收盘价附近）
        data['Open'] = data['Close'].shift(1) * (1 + np.random.normal(0, 0.005, days))
        data['Open'].iloc[0] = base_price * (1 + np.random.normal(0, 0.01))
        
        # 生成最高价和最低价
        daily_range = data['Close'] * volatility * 2
        data['High'] = data[['Open', 'Close']].max(axis=1) + np.random.uniform(0, daily_range)
        data['Low'] = data[['Open', 'Close']].min(axis=1) - np.random.uniform(0, daily_range)
        
        # 确保High > Low
        data['High'] = data[['High', 'Low']].max(axis=1)
        data['Low'] = data[['Low', 'High']].min(axis=1)
        
        # 生成成交量（与价格波动相关）
        price_change = data['Close'].pct_change().abs()
        base_volume = np.random.randint(1000000, 10000000)
        data['Volume'] = base_volume * (1 + price_change * 10)
        data['Volume'] = data['Volume'].fillna(base_volume)
        
        # 计算涨跌幅
        data['Change'] = data['Close'].pct_change() * 100
        
        # 计算振幅
        data['Amplitude'] = ((data['High'] - data['Low']) / data['Close'].shift(1)) * 100
        
        print(f"✅ 生成 {stock_name} 的模拟数据 ({days}个交易日)")
        print(f"   最新价格: {data['Close'].iloc[-1]:.2f}")
        print(f"   价格范围: {data['Close'].min():.2f} - {data['Close'].max():.2f}")
        
        return data
    
    def calculate_a_stock_metrics(self, data):
        """
        计算A股特有指标（离线版本）
        
        Args:
            data: 股票数据
            
        Returns:
            pandas.DataFrame: 包含A股指标的数据
        """
        result = data.copy()
        
        # 计算A股常用技术指标
        # 1. 乖离率 (BIAS)
        result['BIAS5'] = ((result['Close'] - result['Close'].rolling(5).mean()) / 
                          result['Close'].rolling(5).mean()) * 100
        result['BIAS10'] = ((result['Close'] - result['Close'].rolling(10).mean()) / 
                           result['Close'].rolling(10).mean()) * 100
        result['BIAS20'] = ((result['Close'] - result['Close'].rolling(20).mean()) / 
                           result['Close'].rolling(20).mean()) * 100
        
        # 2. 心理线 (PSY)
        up_days = (result['Close'] > result['Close'].shift(1)).rolling(12).sum()
        result['PSY'] = (up_days / 12) * 100
        
        # 3. 威廉指标 (W%R)
        high_14 = result['High'].rolling(14).max()
        low_14 = result['Low'].rolling(14).min()
        result['WR'] = ((high_14 - result['Close']) / (high_14 - low_14)) * 100
        
        return result

def analyze_offline_stock(stock_name, days=252):
    """
    离线分析单只A股股票
    
    Args:
        stock_name: 股票名称
        days: 分析天数
    """
    print(f"\n{'='*60}")
    print(f"📊 离线分析: {stock_name}")
    print(f"📅 分析天数: {days}个交易日")
    print(f"{'='*60}")
    
    # 1. 生成模拟数据
    print("\n1️⃣ 生成模拟数据...")
    generator = OfflineStockDataGenerator()
    data = generator.generate_stock_data(stock_name, days)
    
    if data is None:
        return
    
    # 2. 计算A股特有指标
    print("2️⃣ 计算A股特有指标...")
    data = generator.calculate_a_stock_metrics(data)
    
    # 3. 计算通用技术指标
    print("3️⃣ 计算通用技术指标...")
    indicators = TechnicalIndicators(data)
    
    # 移动平均线
    data['MA5'] = indicators.moving_average(5)
    data['MA10'] = indicators.moving_average(10)
    data['MA20'] = indicators.moving_average(20)
    data['MA60'] = indicators.moving_average(60)
    
    # RSI
    data['RSI'] = indicators.rsi(14)
    
    # MACD
    data['MACD'], data['MACD_Signal'], data['MACD_Histogram'] = indicators.macd()
    
    # 布林带
    data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = indicators.bollinger_bands()
    
    # 4. 显示分析结果
    print("\n4️⃣ 技术分析结果:")
    print(f"{'─'*40}")
    
    latest = data.iloc[-1]
    
    # 价格信息
    print("💰 价格信息:")
    print(f"   模拟收盘价: {latest['Close']:.2f}")
    print(f"   模拟涨跌幅: {latest['Change']:+.2f}%")
    print(f"   模拟振幅: {latest['Amplitude']:.2f}%")
    
    # 移动平均线分析
    print("\n📈 移动平均线分析:")
    print(f"   5日均线: {latest['MA5']:.2f}")
    print(f"   20日均线: {latest['MA20']:.2f}")
    print(f"   60日均线: {latest['MA60']:.2f}")
    
    # A股特有指标
    print("\n🎯 A股特有指标:")
    print(f"   乖离率(5日): {latest['BIAS5']:.2f}%")
    print(f"   乖离率(20日): {latest['BIAS20']:.2f}%")
    print(f"   心理线(PSY): {latest['PSY']:.2f}")
    print(f"   威廉指标(W%R): {latest['WR']:.2f}")
    
    # RSI分析
    print("\n📊 RSI指标分析:")
    rsi_value = latest['RSI']
    if rsi_value > 70:
        rsi_status = "🔴 超买"
    elif rsi_value < 30:
        rsi_status = "🟢 超卖"
    else:
        rsi_status = "🟡 正常"
    print(f"   RSI(14): {rsi_value:.2f} {rsi_status}")
    
    # 投资建议
    print("\n💡 模拟投资建议:")
    print("   这是基于模拟数据的分析，实际投资请参考真实市场数据")
    print("   建议结合基本面分析和其他技术指标进行综合判断")
    
    # 5. 生成图表
    print("\n5️⃣ 生成分析图表...")
    plotter = ChartPlotter(data)
    
    # 价格与移动平均线图
    plotter.plot_price_with_ma(f"{stock_name}(模拟数据)")
    
    print(f"\n✅ {stock_name} 离线分析完成!")

def main():
    """主函数"""
    print("=== A股离线分析工具 ===")
    print("💡 使用模拟数据进行技术分析，无需网络连接")
    
    # 可分析的股票列表
    available_stocks = [
        "贵州茅台", "宁德时代", "五粮液", 
        "中国平安", "招商银行", "上证指数",
        "深证成指", "创业板指"
    ]
    
    print(f"\n📋 可分析股票 ({len(available_stocks)}只):")
    for i, stock in enumerate(available_stocks, 1):
        print(f"   {i}. {stock}")
    
    print("\n📅 分析周期选项:")
    print("   1. 短期分析 (60个交易日)")
    print("   2. 中期分析 (120个交易日)")
    print("   3. 长期分析 (252个交易日 - 默认)")
    
    # 用户选择
    try:
        choice = input("\n请选择分析周期 (1/2/3，默认3): ").strip()
        if choice == "1":
            days = 60
        elif choice == "2":
            days = 120
        else:
            days = 252
        
        print(f"\n开始分析所有{len(available_stocks)}只股票...")
        
        for stock in available_stocks:
            analyze_offline_stock(stock, days)
            
            # 短暂暂停，让用户有时间查看图表
            input("\n按回车键继续分析下一只股票...")
        
        print(f"\n🎉 所有股票离线分析完成!")
        print("💡 提示: 这是模拟数据分析，用于演示技术指标计算方法")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断分析")
    except Exception as e:
        print(f"\n❌ 分析过程中出错: {e}")

if __name__ == "__main__":
    main()