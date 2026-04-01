"""
数据可视化模块

提供多种股票图表：
1. K线图
2. 价格与移动平均线
3. 技术指标图表
4. 成交量图表
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.pylab import date2num
import pandas as pd
import numpy as np

class ChartPlotter:
    """图表绘制器"""
    
    def __init__(self, data):
        """
        初始化图表绘制器
        
        Args:
            data: 股票数据DataFrame
        """
        self.data = data
        plt.style.use('seaborn-v0_8')
    
    def plot_price_with_ma(self, symbol, ma_windows=[5, 10, 20, 60]):
        """
        绘制价格与移动平均线
        
        Args:
            symbol: 股票代码
            ma_windows: 移动平均窗口列表
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                      gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制价格和移动平均线
        ax1.plot(self.data.index, self.data['Close'], label='收盘价', linewidth=1.5, color='black')
        
        colors = ['red', 'blue', 'green', 'orange']
        for i, window in enumerate(ma_windows):
            if i < len(colors):
                ma = self.data['Close'].rolling(window=window).mean()
                ax1.plot(self.data.index, ma, label=f'MA{window}', 
                        linewidth=1, color=colors[i], alpha=0.8)
        
        ax1.set_title(f'{symbol} - 价格与移动平均线', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 绘制成交量
        ax2.bar(self.data.index, self.data['Volume'], 
               color=['green' if x >= 0 else 'red' for x in self.data['Change']], 
               alpha=0.7)
        ax2.set_ylabel('成交量', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        
        plt.tight_layout()
        plt.show()
    
    def plot_candlestick(self, symbol, last_n_days=60):
        """
        绘制K线图
        
        Args:
            symbol: 股票代码
            last_n_days: 显示最近N天的数据
        """
        from mplfinance.original_flavor import candlestick_ohlc
        
        # 获取最近的数据
        recent_data = self.data.tail(last_n_days).copy()
        
        # 准备OHLC数据
        recent_data['Date_num'] = date2num(recent_data.index.to_pydatetime())
        ohlc_data = recent_data[['Date_num', 'Open', 'High', 'Low', 'Close']].values
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                      gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制K线图
        candlestick_ohlc(ax1, ohlc_data, width=0.6, colorup='red', colordown='green', alpha=0.8)
        
        # 添加移动平均线
        ax1.plot(recent_data.index, recent_data['Close'].rolling(5).mean(), 
                label='MA5', color='blue', linewidth=1)
        ax1.plot(recent_data.index, recent_data['Close'].rolling(20).mean(), 
                label='MA20', color='orange', linewidth=1)
        
        ax1.set_title(f'{symbol} - K线图 (最近{last_n_days}天)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 绘制成交量
        ax2.bar(recent_data.index, recent_data['Volume'], 
               color=['green' if x >= 0 else 'red' for x in recent_data['Change']], 
               alpha=0.7)
        ax2.set_ylabel('成交量', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        
        plt.tight_layout()
        plt.show()
    
    def plot_technical_indicators(self, symbol):
        """
        绘制技术指标图表
        
        Args:
            symbol: 股票代码
        """
        fig, axes = plt.subplots(4, 1, figsize=(12, 14))
        
        # RSI图表
        axes[0].plot(self.data.index, self.data['Close'], label='收盘价', color='black', linewidth=1)
        axes[0].set_title(f'{symbol} - 价格', fontsize=12)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 计算RSI（如果不存在）
        if 'RSI' not in self.data.columns:
            delta = self.data['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = self.data['RSI']
        
        # RSI图表
        axes[1].plot(self.data.index, rsi, label='RSI(14)', color='purple', linewidth=1)
        axes[1].axhline(y=70, color='r', linestyle='--', alpha=0.7, label='超买线')
        axes[1].axhline(y=30, color='g', linestyle='--', alpha=0.7, label='超卖线')
        axes[1].set_title('RSI相对强弱指数', fontsize=12)
        axes[1].set_ylim(0, 100)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # MACD图表
        if 'MACD' not in self.data.columns:
            # 计算MACD
            ema12 = self.data['Close'].ewm(span=12).mean()
            ema26 = self.data['Close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
        else:
            macd_line = self.data['MACD']
            signal_line = self.data['MACD_Signal']
            histogram = self.data['MACD_Histogram']
        
        axes[2].plot(self.data.index, macd_line, label='MACD', color='blue', linewidth=1)
        axes[2].plot(self.data.index, signal_line, label='信号线', color='red', linewidth=1)
        axes[2].bar(self.data.index, histogram, label='柱状图', color='gray', alpha=0.5)
        axes[2].set_title('MACD指标', fontsize=12)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # 成交量图表
        axes[3].bar(self.data.index, self.data['Volume'], 
                   color=['green' if x >= 0 else 'red' for x in self.data['Change']], 
                   alpha=0.7)
        axes[3].set_title('成交量', fontsize=12)
        axes[3].grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        
        plt.tight_layout()
        plt.show()
    
    def plot_comparison(self, symbols_data):
        """
        绘制多股票对比图表
        
        Args:
            symbols_data: 股票数据字典 {symbol: data}
        """
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        
        # 绘制价格对比（标准化）
        for i, (symbol, data) in enumerate(symbols_data.items()):
            if i < len(colors):
                # 标准化价格
                normalized_price = data['Close'] / data['Close'].iloc[0] * 100
                axes[0].plot(data.index, normalized_price, 
                           label=symbol, color=colors[i], linewidth=1.5)
        
        axes[0].set_title('股票价格对比 (标准化)', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('标准化价格 (%)', fontsize=12)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 绘制收益率对比
        for i, (symbol, data) in enumerate(symbols_data.items()):
            if i < len(colors):
                returns = data['Close'].pct_change().cumsum() * 100
                axes[1].plot(data.index, returns, 
                           label=symbol, color=colors[i], linewidth=1.5)
        
        axes[1].set_title('累计收益率对比', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('累计收益率 (%)', fontsize=12)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
        
        plt.tight_layout()
        plt.show()