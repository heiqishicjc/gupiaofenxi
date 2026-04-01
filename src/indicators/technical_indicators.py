"""
技术指标计算模块

包含常用的技术分析指标：
1. 移动平均线 (MA)
2. 相对强弱指数 (RSI)
3. 移动平均收敛散度 (MACD)
4. 布林带 (Bollinger Bands)
5. 随机指标 (Stochastic)
6. 成交量指标
"""

import pandas as pd
import numpy as np

class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self, data):
        """
        初始化技术指标计算器
        
        Args:
            data: 股票数据DataFrame
        """
        self.data = data.copy()
    
    def moving_average(self, window, column='Close'):
        """
        计算移动平均线
        
        Args:
            window: 移动平均窗口大小
            column: 计算列名
            
        Returns:
            pandas.Series: 移动平均线
        """
        return self.data[column].rolling(window=window).mean()
    
    def exponential_moving_average(self, window, column='Close'):
        """
        计算指数移动平均线
        
        Args:
            window: 移动平均窗口大小
            column: 计算列名
            
        Returns:
            pandas.Series: 指数移动平均线
        """
        return self.data[column].ewm(span=window).mean()
    
    def rsi(self, window=14, column='Close'):
        """
        计算相对强弱指数 (RSI)
        
        Args:
            window: RSI计算窗口
            column: 计算列名
            
        Returns:
            pandas.Series: RSI值
        """
        delta = self.data[column].diff()
        
        # 计算涨跌幅
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均涨跌幅
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        # 计算RS
        rs = avg_gain / avg_loss
        
        # 计算RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def macd(self, fast=12, slow=26, signal=9, column='Close'):
        """
        计算MACD指标
        
        Args:
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
            column: 计算列名
            
        Returns:
            tuple: (MACD线, 信号线, 柱状图)
        """
        # 计算EMA
        ema_fast = self.exponential_moving_average(fast, column)
        ema_slow = self.exponential_moving_average(slow, column)
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        signal_line = macd_line.ewm(span=signal).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def bollinger_bands(self, window=20, num_std=2, column='Close'):
        """
        计算布林带
        
        Args:
            window: 移动平均窗口
            num_std: 标准差倍数
            column: 计算列名
            
        Returns:
            tuple: (上轨, 中轨, 下轨)
        """
        # 计算中轨（移动平均）
        middle_band = self.moving_average(window, column)
        
        # 计算标准差
        rolling_std = self.data[column].rolling(window=window).std()
        
        # 计算上下轨
        upper_band = middle_band + (rolling_std * num_std)
        lower_band = middle_band - (rolling_std * num_std)
        
        return upper_band, middle_band, lower_band
    
    def stochastic(self, k_window=14, d_window=3):
        """
        计算随机指标
        
        Args:
            k_window: %K计算窗口
            d_window: %D计算窗口
            
        Returns:
            tuple: (%K线, %D线)
        """
        # 计算最高价和最低价
        high_max = self.data['High'].rolling(window=k_window).max()
        low_min = self.data['Low'].rolling(window=k_window).min()
        
        # 计算%K
        k_line = ((self.data['Close'] - low_min) / (high_max - low_min)) * 100
        
        # 计算%D
        d_line = k_line.rolling(window=d_window).mean()
        
        return k_line, d_line
    
    def volume_indicators(self, window=20):
        """
        计算成交量指标
        
        Args:
            window: 计算窗口
            
        Returns:
            tuple: (成交量移动平均, 成交量比率)
        """
        # 成交量移动平均
        volume_ma = self.moving_average(window, 'Volume')
        
        # 成交量比率
        volume_ratio = self.data['Volume'] / volume_ma
        
        return volume_ma, volume_ratio
    
    def atr(self, window=14):
        """
        计算平均真实波幅 (ATR)
        
        Args:
            window: 计算窗口
            
        Returns:
            pandas.Series: ATR值
        """
        # 计算真实波幅
        high_low = self.data['High'] - self.data['Low']
        high_close_prev = abs(self.data['High'] - self.data['Close'].shift())
        low_close_prev = abs(self.data['Low'] - self.data['Close'].shift())
        
        # 真实波幅
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        
        # 平均真实波幅
        atr = true_range.rolling(window=window).mean()
        
        return atr
    
    def calculate_all_indicators(self):
        """
        计算所有常用技术指标
        
        Returns:
            pandas.DataFrame: 包含所有指标的数据
        """
        result = self.data.copy()
        
        # 移动平均线
        result['MA5'] = self.moving_average(5)
        result['MA10'] = self.moving_average(10)
        result['MA20'] = self.moving_average(20)
        result['MA60'] = self.moving_average(60)
        
        # 指数移动平均线
        result['EMA12'] = self.exponential_moving_average(12)
        result['EMA26'] = self.exponential_moving_average(26)
        
        # RSI
        result['RSI14'] = self.rsi(14)
        
        # MACD
        macd_line, signal_line, histogram = self.macd()
        result['MACD'] = macd_line
        result['MACD_Signal'] = signal_line
        result['MACD_Histogram'] = histogram
        
        # 布林带
        upper, middle, lower = self.bollinger_bands()
        result['BB_Upper'] = upper
        result['BB_Middle'] = middle
        result['BB_Lower'] = lower
        
        # 随机指标
        k_line, d_line = self.stochastic()
        result['Stoch_K'] = k_line
        result['Stoch_D'] = d_line
        
        # 成交量指标
        volume_ma, volume_ratio = self.volume_indicators()
        result['Volume_MA20'] = volume_ma
        result['Volume_Ratio'] = volume_ratio
        
        # ATR
        result['ATR14'] = self.atr(14)
        
        return result