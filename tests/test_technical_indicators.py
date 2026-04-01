"""
技术指标计算模块测试
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from indicators.technical_indicators import TechnicalIndicators

class TestTechnicalIndicators(unittest.TestCase):
    """技术指标计算器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        # 生成随机价格数据
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        self.test_data = pd.DataFrame({
            'Open': prices + np.random.randn(100) * 0.1,
            'High': prices + np.abs(np.random.randn(100) * 0.2),
            'Low': prices - np.abs(np.random.randn(100) * 0.2),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        self.indicators = TechnicalIndicators(self.test_data)
    
    def test_moving_average(self):
        """测试移动平均线计算"""
        ma20 = self.indicators.moving_average(20)
        
        self.assertEqual(len(ma20), len(self.test_data))
        self.assertTrue(pd.notna(ma20.iloc[19]))  # 第20个值应该不是NaN
        self.assertTrue(pd.isna(ma20.iloc[0]))    # 第一个值应该是NaN
    
    def test_exponential_moving_average(self):
        """测试指数移动平均线计算"""
        ema12 = self.indicators.exponential_moving_average(12)
        
        self.assertEqual(len(ema12), len(self.test_data))
        self.assertTrue(pd.notna(ema12.iloc[11]))  # 第12个值应该不是NaN
    
    def test_rsi(self):
        """测试RSI计算"""
        rsi = self.indicators.rsi(14)
        
        self.assertEqual(len(rsi), len(self.test_data))
        # RSI值应该在0-100之间
        valid_rsi = rsi.dropna()
        self.assertTrue((valid_rsi >= 0).all() and (valid_rsi <= 100).all())
    
    def test_macd(self):
        """测试MACD计算"""
        macd_line, signal_line, histogram = self.indicators.macd()
        
        self.assertEqual(len(macd_line), len(self.test_data))
        self.assertEqual(len(signal_line), len(self.test_data))
        self.assertEqual(len(histogram), len(self.test_data))
    
    def test_bollinger_bands(self):
        """测试布林带计算"""
        upper, middle, lower = self.indicators.bollinger_bands()
        
        self.assertEqual(len(upper), len(self.test_data))
        self.assertEqual(len(middle), len(self.test_data))
        self.assertEqual(len(lower), len(self.test_data))
        
        # 上轨应该大于中轨，中轨应该大于下轨
        valid_data = middle.dropna()
        if len(valid_data) > 0:
            self.assertTrue((upper > middle).all())
            self.assertTrue((middle > lower).all())
    
    def test_stochastic(self):
        """测试随机指标计算"""
        k_line, d_line = self.indicators.stochastic()
        
        self.assertEqual(len(k_line), len(self.test_data))
        self.assertEqual(len(d_line), len(self.test_data))
        
        # 随机指标应该在0-100之间
        valid_k = k_line.dropna()
        valid_d = d_line.dropna()
        
        if len(valid_k) > 0:
            self.assertTrue((valid_k >= 0).all() and (valid_k <= 100).all())
        if len(valid_d) > 0:
            self.assertTrue((valid_d >= 0).all() and (valid_d <= 100).all())
    
    def test_calculate_all_indicators(self):
        """测试计算所有指标"""
        all_indicators = self.indicators.calculate_all_indicators()
        
        expected_columns = [
            'MA5', 'MA10', 'MA20', 'MA60', 'EMA12', 'EMA26', 
            'RSI14', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'BB_Upper', 'BB_Middle', 'BB_Lower', 'Stoch_K', 'Stoch_D',
            'Volume_MA20', 'Volume_Ratio', 'ATR14'
        ]
        
        for col in expected_columns:
            self.assertIn(col, all_indicators.columns)

if __name__ == "__main__":
    unittest.main()