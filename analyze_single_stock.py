#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个A股股票分析示例

这个脚本演示如何对单只A股股票进行详细的技术分析
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.china_stock_fetcher import ChinaStockFetcher
from indicators.technical_indicators import TechnicalIndicators
from visualization.chart_plotter import ChartPlotter

def analyze_single_stock(symbol, stock_name, period="1y"):
    """
    分析单只A股股票的完整流程
    
    Args:
        symbol: 股票代码 (如: 600519.SS)
        stock_name: 股票名称 (如: 贵州茅台)
        period: 分析周期 (如: 3mo, 6mo, 1y, 2y)
    """
    print(f"\n{'='*60}")
    print(f"📊 开始分析: {stock_name} ({symbol})")
    print(f"📅 分析周期: {period}")
    print(f"{'='*60}")
    
    # 1. 创建数据获取器
    fetcher = ChinaStockFetcher()
    
    # 2. 获取股票数据
    print("\n1️⃣ 数据获取中...")
    data = fetcher.get_a_stock_data(symbol, period=period)
    
    if data is None or data.empty:
        print(f"❌ 无法获取 {stock_name} 的数据")
        return
    
    print(f"✅ 成功获取 {len(data)} 个交易日数据")
    print(f"   时间范围: {data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}")
    
    # 3. 计算A股特有指标
    print("\n2️⃣ 计算A股特有指标...")
    data = fetcher.calculate_a_stock_metrics(data)
    
    # 4. 计算通用技术指标
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
    
    # 5. 显示分析结果
    print("\n4️⃣ 技术分析结果:")
    print(f"{'─'*40}")
    
    latest = data.iloc[-1]
    
    # 价格信息
    print("💰 价格信息:")
    print(f"   最新收盘价: {latest['Close']:.2f}")
    print(f"   当日涨跌幅: {latest['Change']:+.2f}%")
    print(f"   当日振幅: {latest['Amplitude']:.2f}%")
    
    # 移动平均线分析
    print("\n📈 移动平均线分析:")
    print(f"   5日均线: {latest['MA5']:.2f} (偏离: {(latest['Close']/latest['MA5']-1)*100:+.2f}%)")
    print(f"   20日均线: {latest['MA20']:.2f} (偏离: {(latest['Close']/latest['MA20']-1)*100:+.2f}%)")
    print(f"   60日均线: {latest['MA60']:.2f} (偏离: {(latest['Close']/latest['MA60']-1)*100:+.2f}%)")
    
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
    
    # MACD分析
    print("\n📉 MACD指标分析:")
    macd_histogram = latest['MACD_Histogram']
    if macd_histogram > 0:
        macd_status = "🟢 金叉向上"
    else:
        macd_status = "🔴 死叉向下"
    print(f"   MACD柱状图: {macd_histogram:.4f} {macd_status}")
    
    # 布林带分析
    print("\n📏 布林带分析:")
    close_price = latest['Close']
    bb_upper = latest['BB_Upper']
    bb_lower = latest['BB_Lower']
    
    if close_price > bb_upper:
        bb_status = "🔴 上轨上方(超买)"
    elif close_price < bb_lower:
        bb_status = "🟢 下轨下方(超卖)"
    else:
        bb_status = "🟡 轨道内(正常)"
    print(f"   布林带位置: {bb_status}")
    
    # 6. 生成图表
    print("\n5️⃣ 生成分析图表...")
    plotter = ChartPlotter(data)
    
    # 价格与移动平均线图
    plotter.plot_price_with_ma(f"{stock_name}({symbol})")
    
    # 技术指标综合图
    plotter.plot_technical_indicators(f"{stock_name}({symbol})")
    
    print(f"\n✅ {stock_name} 分析完成!")
    print(f"💡 提示: 图表已显示，可以查看详细的技术指标走势")

def get_stock_recommendation(data):
    """
    基于技术指标给出简单的投资建议
    
    Args:
        data: 包含技术指标的股票数据
        
    Returns:
        str: 投资建议
    """
    latest = data.iloc[-1]
    
    # 评分系统
    score = 0
    reasons = []
    
    # RSI评分
    rsi = latest['RSI']
    if rsi < 30:
        score += 2
        reasons.append("RSI超卖，存在反弹机会")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI超买，注意回调风险")
    
    # 乖离率评分
    bias20 = latest['BIAS20']
    if bias20 < -5:
        score += 1
        reasons.append("乖离率偏低，股价偏离均线")
    elif bias20 > 5:
        score -= 1
        reasons.append("乖离率偏高，注意均值回归")
    
    # MACD评分
    macd_hist = latest['MACD_Histogram']
    if macd_hist > 0:
        score += 1
        reasons.append("MACD金叉向上")
    else:
        score -= 1
        reasons.append("MACD死叉向下")
    
    # 布林带评分
    close_price = latest['Close']
    bb_lower = latest['BB_Lower']
    if close_price < bb_lower:
        score += 1
        reasons.append("股价在布林带下轨附近")
    
    # 根据评分给出建议
    if score >= 3:
        recommendation = "🟢 强烈关注"
    elif score >= 1:
        recommendation = "🟡 谨慎关注"
    elif score >= -1:
        recommendation = "🟠 中性观望"
    elif score >= -3:
        recommendation = "🔴 注意风险"
    else:
        recommendation = "⚫ 高度警惕"
    
    return recommendation, reasons

def main():
    """主函数 - 演示多个A股的分析"""
    print("=== A股单个股票分析工具 ===")
    
    # 定义要分析的股票列表
    stocks_to_analyze = [
        ("600519.SS", "贵州茅台"),
        ("300750.SZ", "宁德时代"), 
        ("000858.SZ", "五粮液"),
        ("601318.SS", "中国平安"),
        ("600036.SS", "招商银行")
    ]
    
    print("\n可选分析周期:")
    print("  1m - 1个月")
    print("  3m - 3个月") 
    print("  6m - 6个月")
    print("  1y - 1年 (默认)")
    print("  2y - 2年")
    
    # 用户选择分析周期
    period = input("\n请输入分析周期 (默认1y): ").strip() or "1y"
    
    print(f"\n开始分析以下{len(stocks_to_analyze)}只A股...")
    
    for symbol, name in stocks_to_analyze:
        try:
            analyze_single_stock(symbol, name, period)
            
            # 短暂暂停，避免请求过于频繁
            import time
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ 分析 {name} 时出错: {e}")
            continue
    
    print(f"\n🎉 所有股票分析完成!")
    print("💡 提示: 您可以修改代码中的股票列表来定制分析")

if __name__ == "__main__":
    main()