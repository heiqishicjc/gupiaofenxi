#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据可视化工具

功能：
1. 股票价格走势图
2. 技术指标图表
3. 市场对比分析
4. 热力图和相关性分析
5. 投资组合可视化
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_analyzer import StockAnalyzer


class StockVisualizer:
    """A股数据可视化工具"""
    
    def __init__(self, data_dir="e:/stockdata"):
        """
        初始化可视化工具
        
        Args:
            data_dir: 股票数据目录
        """
        self.data_dir = data_dir
        self.analyzer = StockAnalyzer(data_dir)
        
        # 设置图表样式
        self._setup_style()
        
        print("A股数据可视化工具初始化完成")
    
    def _setup_style(self):
        """设置图表样式"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_stock_price(self, symbol, period='1y', save_path=None):
        """
        绘制股票价格走势图
        
        Args:
            symbol: 股票代码
            period: 时间周期 ('1m', '3m', '6m', '1y', '2y', '5y')
            save_path: 保存路径
        """
        # 获取股票数据
        analysis_result = self.analyzer.analyze_single_stock(symbol)
        if analysis_result is None:
            print(f"无法获取 {symbol} 的数据")
            return
        
        # 获取完整数据
        data = self.analyzer._get_stock_data(symbol, self.analyzer._detect_market(symbol))
        
        # 根据周期筛选数据
        if period == '1m':
            data = data.tail(22)  # 约1个月
        elif period == '3m':
            data = data.tail(66)  # 约3个月
        elif period == '6m':
            data = data.tail(132)  # 约6个月
        elif period == '1y':
            data = data.tail(252)  # 约1年
        elif period == '2y':
            data = data.tail(504)  # 约2年
        elif period == '5y':
            data = data.tail(1260)  # 约5年
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})
        
        # 价格走势图
        ax1.plot(data.index, data['close'], label='收盘价', linewidth=2, color='#2E86AB')
        ax1.plot(data.index, data['high'], label='最高价', alpha=0.5, color='#A23B72')
        ax1.plot(data.index, data['low'], label='最低价', alpha=0.5, color='#F18F01')
        
        # 添加移动平均线
        ma20 = data['close'].rolling(window=20).mean()
        ma60 = data['close'].rolling(window=60).mean()
        ax1.plot(data.index, ma20, label='MA20', color='#FF6B6B', linestyle='--')
        ax1.plot(data.index, ma60, label='MA60', color='#4ECDC4', linestyle='--')
        
        ax1.set_title(f'{symbol} 价格走势图 ({period})', fontsize=16, fontweight='bold')
        ax1.set_ylabel('价格 (元)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 成交量图
        ax2.bar(data.index, data['vol'], color='#6A0572', alpha=0.7)
        ax2.set_title('成交量', fontsize=12)
        ax2.set_ylabel('成交量', fontsize=10)
        ax2.set_xlabel('日期', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_technical_indicators(self, symbol, save_path=None):
        """
        绘制技术指标图表
        
        Args:
            symbol: 股票代码
            save_path: 保存路径
        """
        analysis_result = self.analyzer.analyze_single_stock(symbol)
        if analysis_result is None:
            print(f"无法获取 {symbol} 的数据")
            return
        
        data = self.analyzer._get_stock_data(symbol, self.analyzer._detect_market(symbol))
        data = data.tail(252)  # 最近一年数据
        
        # 创建子图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. RSI指标
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        ax1.plot(data.index, rsi, label='RSI', color='#FF6B6B', linewidth=2)
        ax1.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超买线(70)')
        ax1.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超卖线(30)')
        ax1.set_title('RSI相对强弱指标', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. MACD指标
        ema12 = data['close'].ewm(span=12).mean()
        ema26 = data['close'].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        ax2.plot(data.index, macd, label='MACD', color='#2E86AB')
        ax2.plot(data.index, signal, label='Signal', color='#A23B72')
        ax2.bar(data.index, histogram, label='Histogram', alpha=0.3, color='#F18F01')
        ax2.set_title('MACD指标', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 布林带
        bb_middle = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std
        
        ax3.plot(data.index, data['close'], label='收盘价', color='#2E86AB')
        ax3.plot(data.index, bb_upper, label='上轨', color='red', alpha=0.7)
        ax3.plot(data.index, bb_middle, label='中轨', color='orange', alpha=0.7)
        ax3.plot(data.index, bb_lower, label='下轨', color='green', alpha=0.7)
        ax3.fill_between(data.index, bb_upper, bb_lower, alpha=0.1, color='gray')
        ax3.set_title('布林带', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 成交量与价格关系
        ax4_1 = ax4.twinx()
        ax4.plot(data.index, data['close'], label='收盘价', color='#2E86AB', linewidth=2)
        ax4_1.bar(data.index, data['vol'], alpha=0.3, color='#6A0572', label='成交量')
        ax4.set_title('价格与成交量', fontsize=12)
        ax4.legend(loc='upper left')
        ax4_1.legend(loc='upper right')
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'{symbol} 技术指标分析', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"技术指标图表已保存到: {save_path}")
        
        plt.show()
    
    def plot_market_comparison(self, symbols, period='1y', save_path=None):
        """
        绘制多股票对比图
        
        Args:
            symbols: 股票代码列表
            period: 时间周期
            save_path: 保存路径
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 价格走势对比 (标准化)
        normalized_prices = {}
        
        for symbol in symbols:
            data = self.analyzer._get_stock_data(symbol, self.analyzer._detect_market(symbol))
            if data is not None and not data.empty:
                # 根据周期筛选数据
                if period == '1m':
                    data = data.tail(22)
                elif period == '3m':
                    data = data.tail(66)
                elif period == '6m':
                    data = data.tail(132)
                elif period == '1y':
                    data = data.tail(252)
                
                # 标准化价格 (以起始日为基准)
                normalized_price = (data['close'] / data['close'].iloc[0]) * 100
                normalized_prices[symbol] = normalized_price
                
                ax1.plot(data.index, normalized_price, label=symbol, linewidth=2)
        
        ax1.set_title(f'多股票价格走势对比 ({period})', fontsize=14, fontweight='bold')
        ax1.set_ylabel('标准化价格 (%)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 收益率对比
        for symbol, normalized_price in normalized_prices.items():
            returns = normalized_price.pct_change().dropna()
            cumulative_returns = (1 + returns).cumprod() - 1
            ax2.plot(cumulative_returns.index, cumulative_returns * 100, label=symbol, linewidth=2)
        
        ax2.set_title('累计收益率对比', fontsize=14, fontweight='bold')
        ax2.set_ylabel('累计收益率 (%)', fontsize=12)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"市场对比图已保存到: {save_path}")
        
        plt.show()
    
    def plot_correlation_heatmap(self, symbols, period='1y', save_path=None):
        """
        绘制相关性热力图
        
        Args:
            symbols: 股票代码列表
            period: 时间周期
            save_path: 保存路径
        """
        # 收集收益率数据
        returns_data = {}
        
        for symbol in symbols:
            data = self.analyzer._get_stock_data(symbol, self.analyzer._detect_market(symbol))
            if data is not None and not data.empty:
                # 根据周期筛选数据
                if period == '1m':
                    data = data.tail(22)
                elif period == '3m':
                    data = data.tail(66)
                elif period == '6m':
                    data = data.tail(132)
                elif period == '1y':
                    data = data.tail(252)
                
                returns = data['close'].pct_change().dropna()
                returns_data[symbol] = returns
        
        # 创建相关性矩阵
        returns_df = pd.DataFrame(returns_data)
        correlation_matrix = returns_df.corr()
        
        # 绘制热力图
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='coolwarm', 
                   center=0,
                   square=True,
                   fmt='.2f',
                   cbar_kws={'shrink': 0.8})
        
        plt.title(f'股票收益率相关性热力图 ({period})', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"相关性热力图已保存到: {save_path}")
        
        plt.show()
    
    def plot_risk_return_scatter(self, symbols, period='1y', save_path=None):
        """
        绘制风险-收益散点图
        
        Args:
            symbols: 股票代码列表
            period: 时间周期
            save_path: 保存路径
        """
        risk_return_data = []
        
        for symbol in symbols:
            data = self.analyzer._get_stock_data(symbol, self.analyzer._detect_market(symbol))
            if data is not None and not data.empty:
                # 根据周期筛选数据
                if period == '1m':
                    data = data.tail(22)
                elif period == '3m':
                    data = data.tail(66)
                elif period == '6m':
                    data = data.tail(132)
                elif period == '1y':
                    data = data.tail(252)
                
                returns = data['close'].pct_change().dropna()
                
                # 计算年化收益率和波动率
                annual_return = returns.mean() * 252 * 100  # 百分比
                annual_volatility = returns.std() * np.sqrt(252) * 100  # 百分比
                
                risk_return_data.append({
                    'symbol': symbol,
                    'return': annual_return,
                    'risk': annual_volatility,
                    'sharpe': annual_return / annual_volatility if annual_volatility > 0 else 0
                })
        
        # 创建散点图
        df = pd.DataFrame(risk_return_data)
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(df['risk'], df['return'], c=df['sharpe'], cmap='viridis', s=100, alpha=0.7)
        
        # 添加标签
        for i, row in df.iterrows():
            plt.annotate(row['symbol'], (row['risk'], row['return']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        plt.colorbar(scatter, label='夏普比率')
        plt.xlabel('年化波动率 (%)', fontsize=12)
        plt.ylabel('年化收益率 (%)', fontsize=12)
        plt.title('风险-收益散点图', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # 添加参考线
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        plt.axvline(x=df['risk'].mean(), color='blue', linestyle='--', alpha=0.5, label='平均风险')
        
        plt.legend()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"风险-收益散点图已保存到: {save_path}")
        
        plt.show()


def main():
    """主函数 - 演示可视化功能"""
    print("A股数据可视化工具演示")
    print("=" * 50)
    
    # 创建可视化工具
    visualizer = StockVisualizer()
    
    # 示例股票
    sample_stocks = ['000001.SZ', '600519.SH', '000858.SZ', '002415.SZ']
    
    # 1. 单股票价格走势
    print("1. 绘制单股票价格走势图...")
    visualizer.plot_stock_price('000001.SZ', period='1y')
    
    # 2. 技术指标分析
    print("\n2. 绘制技术指标图表...")
    visualizer.plot_technical_indicators('600519.SH')
    
    # 3. 市场对比
    print("\n3. 绘制多股票对比图...")
    visualizer.plot_market_comparison(sample_stocks, period='1y')
    
    # 4. 相关性热力图
    print("\n4. 绘制相关性热力图...")
    visualizer.plot_correlation_heatmap(sample_stocks, period='1y')
    
    # 5. 风险-收益散点图
    print("\n5. 绘制风险-收益散点图...")
    visualizer.plot_risk_return_scatter(sample_stocks, period='1y')


if __name__ == "__main__":
    main()