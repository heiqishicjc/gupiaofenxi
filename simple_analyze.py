#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单A股分析工具

使用内置示例数据进行技术分析演示
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

def create_sample_data():
    """创建示例A股数据"""
    # 生成最近252个交易日的数据（约1年）
    dates = pd.bdate_range(end=datetime.now(), periods=252)
    
    # 设置随机种子以确保可重复性
    np.random.seed(42)
    
    # 生成价格序列（模拟A股走势）
    # 初始价格
    base_price = 100
    
    # 生成收益率序列
    returns = np.random.normal(0.0008, 0.02, len(dates))  # 日均收益率0.08%，波动率2%
    
    # 计算价格序列
    prices = base_price * np.exp(np.cumsum(returns))
    
    # 创建DataFrame
    data = pd.DataFrame(index=dates)
    data['Close'] = prices
    
    # 生成开盘价（前一日收盘价附近）
    data['Open'] = data['Close'].shift(1) * (1 + np.random.normal(0, 0.005, len(dates)))
    data['Open'].iloc[0] = base_price
    
    # 生成最高价和最低价
    daily_range = data['Close'] * 0.03  # 3%的日内波动
    data['High'] = data[['Open', 'Close']].max(axis=1) + np.random.uniform(0, daily_range)
    data['Low'] = data[['Open', 'Close']].min(axis=1) - np.random.uniform(0, daily_range)
    
    # 确保High > Low
    data['High'] = data[['High', 'Low']].max(axis=1)
    data['Low'] = data[['Low', 'High']].min(axis=1)
    
    # 生成成交量
    price_change = data['Close'].pct_change().abs()
    base_volume = 1000000
    data['Volume'] = base_volume * (1 + price_change * 20)
    data['Volume'] = data['Volume'].fillna(base_volume)
    
    return data

def calculate_a_stock_indicators(data):
    """计算A股特有技术指标"""
    result = data.copy()
    
    # 计算涨跌幅
    result['Change'] = result['Close'].pct_change() * 100
    
    # 计算振幅
    result['Amplitude'] = ((result['High'] - result['Low']) / result['Close'].shift(1)) * 100
    
    # 乖离率 (BIAS)
    result['BIAS5'] = ((result['Close'] - result['Close'].rolling(5).mean()) / 
                      result['Close'].rolling(5).mean()) * 100
    result['BIAS20'] = ((result['Close'] - result['Close'].rolling(20).mean()) / 
                       result['Close'].rolling(20).mean()) * 100
    
    # 心理线 (PSY)
    up_days = (result['Close'] > result['Close'].shift(1)).rolling(12).sum()
    result['PSY'] = (up_days / 12) * 100
    
    return result

def analyze_sample_stock():
    """分析示例股票数据"""
    print("=== A股技术分析演示 ===")
    print("💡 使用内置示例数据演示技术指标计算方法")
    print("=" * 50)
    
    # 1. 创建示例数据
    print("\n1️⃣ 创建示例A股数据...")
    data = create_sample_data()
    print(f"✅ 生成 {len(data)} 个交易日数据")
    print(f"   时间范围: {data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}")
    
    # 2. 计算A股特有指标
    print("\n2️⃣ 计算A股特有指标...")
    data = calculate_a_stock_indicators(data)
    
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
    print("─" * 40)
    
    latest = data.iloc[-1]
    
    print("💰 价格信息:")
    print(f"   收盘价: {latest['Close']:.2f}")
    print(f"   涨跌幅: {latest['Change']:+.2f}%")
    print(f"   振幅: {latest['Amplitude']:.2f}%")
    
    print("\n📈 移动平均线:")
    print(f"   MA5: {latest['MA5']:.2f}")
    print(f"   MA20: {latest['MA20']:.2f}")
    print(f"   MA60: {latest['MA60']:.2f}")
    
    print("\n🎯 A股特有指标:")
    print(f"   乖离率(5日): {latest['BIAS5']:.2f}%")
    print(f"   乖离率(20日): {latest['BIAS20']:.2f}%")
    print(f"   心理线: {latest['PSY']:.2f}")
    
    print("\n📊 技术指标:")
    rsi = latest['RSI']
    if rsi > 70:
        rsi_status = "🔴 超买"
    elif rsi < 30:
        rsi_status = "🟢 超卖"
    else:
        rsi_status = "🟡 正常"
    print(f"   RSI(14): {rsi:.2f} {rsi_status}")
    
    macd_hist = latest['MACD_Histogram']
    if macd_hist > 0:
        macd_status = "🟢 金叉"
    else:
        macd_status = "🔴 死叉"
    print(f"   MACD柱状图: {macd_hist:.4f} {macd_status}")
    
    # 5. 生成图表
    print("\n5️⃣ 生成技术分析图表...")
    plotter = ChartPlotter(data)
    
    # 价格与移动平均线
    plotter.plot_price_with_ma("示例A股技术分析")
    
    # 技术指标综合图
    plotter.plot_technical_indicators("示例A股技术指标")
    
    print("\n✅ 技术分析演示完成!")
    print("💡 这个演示展示了如何计算和解读各种技术指标")
    print("💡 实际使用时，只需将示例数据替换为真实A股数据即可")

def show_technical_indicators_explanation():
    """显示技术指标说明"""
    print("\n" + "="*60)
    print("📚 技术指标说明")
    print("="*60)
    
    indicators_info = {
        "移动平均线(MA)": "反映股价趋势，短期均线上穿长期均线为买入信号",
        "相对强弱指数(RSI)": "衡量超买超卖，低于30超卖(买入机会)，高于70超买(卖出机会)",
        "乖离率(BIAS)": "股价偏离移动平均线的程度，偏离过大可能回归",
        "心理线(PSY)": "投资者心理预期，高于75超买，低于25超卖",
        "MACD": "趋势判断，金叉(买入信号) vs 死叉(卖出信号)",
        "布林带(Bollinger Bands)": "价格波动范围，触及上轨可能回调，触及下轨可能反弹"
    }
    
    for indicator, explanation in indicators_info.items():
        print(f"\n📖 {indicator}:")
        print(f"   {explanation}")

def main():
    """主函数"""
    try:
        # 分析示例数据
        analyze_sample_stock()
        
        # 显示技术指标说明
        show_technical_indicators_explanation()
        
        print("\n" + "="*60)
        print("🎯 如何使用真实A股数据:")
        print("="*60)
        print("""
1. 获取A股数据文件(CSV格式)：
   - 从券商软件导出
   - 从财经网站下载
   - 使用其他数据源

2. 修改代码加载真实数据：
   data = pd.read_csv('your_stock_data.csv', index_col=0, parse_dates=True)

3. 运行相同的分析流程

💡 当前演示版本已包含完整的技术指标计算逻辑
💡 只需替换数据源即可分析真实A股
        """)
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        print("💡 请检查Python环境和依赖包是否安装正确")

if __name__ == "__main__":
    main()