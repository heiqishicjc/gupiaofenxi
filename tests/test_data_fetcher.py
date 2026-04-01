"""
数据获取模块测试
"""

import unittest
import pandas as pd
import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.data_fetcher import StockDataFetcher

class TestStockDataFetcher(unittest.TestCase):
    """股票数据获取器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.fetcher = StockDataFetcher(cache_dir="./test_cache")
    
    def test_get_stock_data(self):
        """测试获取股票数据"""
        # 测试获取AAPL数据
        data = self.fetcher.get_stock_data("AAPL", period="1mo", use_cache=False)
        
        self.assertIsNotNone(data)
        self.assertFalse(data.empty)
        self.assertIn('Close', data.columns)
        self.assertIn('Volume', data.columns)
    
    def test_data_preprocessing(self):
        """测试数据预处理"""
        # 创建测试数据
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [103, 104, 105],
            'Volume': [1000000, 2000000, 3000000]
        })
        
        # 测试预处理
        processed_data = self.fetcher._preprocess_data(test_data)
        
        self.assertIn('Change', processed_data.columns)
        self.assertIn('Volume_Change', processed_data.columns)
    
    def test_get_multiple_stocks(self):
        """测试获取多个股票数据"""
        symbols = ["AAPL", "MSFT"]
        stocks_data = self.fetcher.get_multiple_stocks(symbols, period="1mo")
        
        self.assertEqual(len(stocks_data), len(symbols))
        for symbol in symbols:
            self.assertIn(symbol, stocks_data)
    
    def tearDown(self):
        """测试后清理"""
        # 清理测试缓存文件
        import shutil
        if os.path.exists("./test_cache"):
            shutil.rmtree("./test_cache")

if __name__ == "__main__":
    unittest.main()