"""
股票数据获取模块

支持多种数据源：
1. yfinance (Yahoo Finance) - 支持A股、港股、美股
2. 本地数据文件
3. 其他API接口

A股股票代码格式：
- 上海证券交易所: 000001.SS (平安银行)
- 深圳证券交易所: 000001.SZ (平安银行)
- 创业板: 300001.SZ (特锐德)
- 科创板: 688001.SS (华兴源创)
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self, cache_dir="data"):
        """
        初始化数据获取器
        
        Args:
            cache_dir: 数据缓存目录
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_stock_data(self, symbol, period="1y", interval="1d", use_cache=True):
        """
        获取股票数据
        
        Args:
            symbol: 股票代码 (如: AAPL, 000001.SZ, 600036.SS)
            period: 数据期间 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: 数据间隔 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            use_cache: 是否使用缓存
            
        Returns:
            pandas.DataFrame: 股票数据
        """
        cache_file = os.path.join(self.cache_dir, f"{symbol}_{period}_{interval}.csv")
        
        # 检查缓存
        if use_cache and os.path.exists(cache_file):
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                print(f"从缓存加载数据: {cache_file}")
                return data
            except Exception as e:
                print(f"缓存文件读取失败: {e}")
        
        # 从网络获取数据
        try:
            print(f"正在从网络获取 {symbol} 数据...")
            
            # 使用yfinance获取数据
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"未找到 {symbol} 的数据")
                return None
            
            # 数据预处理
            data = self._preprocess_data(data)
            
            # 保存到缓存
            if use_cache:
                data.to_csv(cache_file)
                print(f"数据已保存到缓存: {cache_file}")
            
            return data
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            return None
    
    def _preprocess_data(self, data):
        """
        数据预处理
        
        Args:
            data: 原始数据
            
        Returns:
            pandas.DataFrame: 处理后的数据
        """
        # 确保索引是datetime类型
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        # 按日期排序
        data = data.sort_index()
        
        # 计算涨跌幅
        data['Change'] = data['Close'].pct_change() * 100
        
        # 计算成交量变化
        data['Volume_Change'] = data['Volume'].pct_change() * 100
        
        return data
    
    def get_multiple_stocks(self, symbols, period="1y", interval="1d"):
        """
        获取多个股票数据
        
        Args:
            symbols: 股票代码列表
            period: 数据期间
            interval: 数据间隔
            
        Returns:
            dict: 股票数据字典
        """
        stocks_data = {}
        
        for symbol in symbols:
            print(f"获取 {symbol} 数据...")
            data = self.get_stock_data(symbol, period, interval)
            if data is not None:
                stocks_data[symbol] = data
        
        return stocks_data
    
    def get_stock_info(self, symbol):
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            dict: 股票信息
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 提取关键信息
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A')
            }
            
            return stock_info
            
        except Exception as e:
            print(f"获取股票信息失败: {e}")
            return None