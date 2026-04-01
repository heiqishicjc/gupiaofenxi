"""
A股数据获取模块

专门针对中国A股市场的数据获取功能
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

class ChinaStockFetcher:
    """A股数据获取器"""
    
    # A股主要指数代码
    INDEX_SYMBOLS = {
        '上证指数': '000001.SS',
        '深证成指': '399001.SZ', 
        '创业板指': '399006.SZ',
        '沪深300': '000300.SS',
        '上证50': '000016.SS',
        '中证500': '000905.SS'
    }
    
    # 热门A股股票代码
    POPULAR_STOCKS = {
        '贵州茅台': '600519.SS',
        '工商银行': '601398.SS',
        '中国平安': '601318.SS',
        '招商银行': '600036.SS',
        '五粮液': '000858.SZ',
        '宁德时代': '300750.SZ',
        '比亚迪': '002594.SZ',
        '中信证券': '600030.SS',
        '万科A': '000002.SZ',
        '海康威视': '002415.SZ'
    }
    
    def __init__(self, cache_dir="data"):
        """
        初始化A股数据获取器
        
        Args:
            cache_dir: 数据缓存目录
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_a_stock_data(self, symbol, period="1y", interval="1d", use_cache=True):
        """
        获取A股股票数据
        
        Args:
            symbol: A股股票代码 (如: 600036.SS, 000001.SZ)
            period: 数据期间
            interval: 数据间隔
            use_cache: 是否使用缓存
            
        Returns:
            pandas.DataFrame: A股股票数据
        """
        # 验证A股代码格式
        if not self._validate_a_stock_symbol(symbol):
            print(f"无效的A股代码格式: {symbol}")
            return None
        
        cache_file = os.path.join(self.cache_dir, f"a_stock_{symbol}_{period}_{interval}.csv")
        
        # 检查缓存
        if use_cache and os.path.exists(cache_file):
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                print(f"从缓存加载A股数据: {cache_file}")
                return data
            except Exception as e:
                print(f"缓存文件读取失败: {e}")
        
        # 从网络获取数据
        try:
            print(f"正在获取A股 {symbol} 数据...")
            
            # 使用yfinance获取A股数据
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"未找到 {symbol} 的A股数据")
                return None
            
            # A股数据预处理
            data = self._preprocess_a_stock_data(data)
            
            # 保存到缓存
            if use_cache:
                data.to_csv(cache_file)
                print(f"A股数据已保存到缓存: {cache_file}")
            
            return data
            
        except Exception as e:
            print(f"获取A股数据失败: {e}")
            return None
    
    def get_index_data(self, index_name, period="1y", interval="1d"):
        """
        获取A股指数数据
        
        Args:
            index_name: 指数名称 (如: 上证指数, 沪深300)
            period: 数据期间
            interval: 数据间隔
            
        Returns:
            pandas.DataFrame: 指数数据
        """
        if index_name not in self.INDEX_SYMBOLS:
            print(f"不支持的指数: {index_name}")
            print(f"支持的指数: {', '.join(self.INDEX_SYMBOLS.keys())}")
            return None
        
        symbol = self.INDEX_SYMBOLS[index_name]
        return self.get_a_stock_data(symbol, period, interval)
    
    def get_popular_stock_data(self, stock_name, period="1y", interval="1d"):
        """
        获取热门A股数据
        
        Args:
            stock_name: 股票名称 (如: 贵州茅台, 宁德时代)
            period: 数据期间
            interval: 数据间隔
            
        Returns:
            pandas.DataFrame: 股票数据
        """
        if stock_name not in self.POPULAR_STOCKS:
            print(f"不支持的股票: {stock_name}")
            print(f"支持的股票: {', '.join(self.POPULAR_STOCKS.keys())}")
            return None
        
        symbol = self.POPULAR_STOCKS[stock_name]
        return self.get_a_stock_data(symbol, period, interval)
    
    def get_multiple_a_stocks(self, symbols, period="1y", interval="1d"):
        """
        获取多个A股数据
        
        Args:
            symbols: A股代码列表
            period: 数据期间
            interval: 数据间隔
            
        Returns:
            dict: A股数据字典
        """
        stocks_data = {}
        
        for symbol in symbols:
            print(f"获取A股 {symbol} 数据...")
            data = self.get_a_stock_data(symbol, period, interval)
            if data is not None:
                stocks_data[symbol] = data
        
        return stocks_data
    
    def _validate_a_stock_symbol(self, symbol):
        """
        验证A股代码格式
        
        Args:
            symbol: 股票代码
            
        Returns:
            bool: 是否有效
        """
        # A股代码格式: 6位数字 + .SS 或 .SZ
        import re
        pattern = r'^\d{6}\.(SS|SZ)$'
        return re.match(pattern, symbol) is not None
    
    def _preprocess_a_stock_data(self, data):
        """
        A股数据预处理
        
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
        
        # 计算涨跌幅 (A股通常使用百分比)
        data['Change'] = data['Close'].pct_change() * 100
        
        # 计算成交量变化
        data['Volume_Change'] = data['Volume'].pct_change() * 100
        
        # 计算振幅 (A股常用指标)
        data['Amplitude'] = ((data['High'] - data['Low']) / data['Close'].shift(1)) * 100
        
        # 计算换手率 (需要流通股本数据，这里简化处理)
        # 实际应用中需要获取流通股本数据
        
        return data
    
    def get_a_stock_info(self, symbol):
        """
        获取A股基本信息
        
        Args:
            symbol: A股代码
            
        Returns:
            dict: 股票信息
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 提取A股相关信息
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'currency': info.get('currency', 'CNY')
            }
            
            return stock_info
            
        except Exception as e:
            print(f"获取A股信息失败: {e}")
            return None
    
    def get_a_stock_financials(self, symbol):
        """
        获取A股财务数据 (简化版)
        
        Args:
            symbol: A股代码
            
        Returns:
            dict: 财务数据
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # 获取财务指标
            financials = {
                'revenue': ticker.financials.loc['Total Revenue'] if hasattr(ticker, 'financials') else 'N/A',
                'net_income': ticker.financials.loc['Net Income'] if hasattr(ticker, 'financials') else 'N/A',
                'eps': ticker.financials.loc['Basic EPS'] if hasattr(ticker, 'financials') else 'N/A'
            }
            
            return financials
            
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return None
    
    def calculate_a_stock_metrics(self, data):
        """
        计算A股特有指标
        
        Args:
            data: 股票数据
            
        Returns:
            pandas.DataFrame: 包含A股指标的数据
        """
        result = data.copy()
        
        # 计算A股常用技术指标
        # 1. 乖离率 (BIAS)
        result['BIAS5'] = ((result['Close'] - result['Close'].rolling(5).mean()) / result['Close'].rolling(5).mean()) * 100
        result['BIAS10'] = ((result['Close'] - result['Close'].rolling(10).mean()) / result['Close'].rolling(10).mean()) * 100
        result['BIAS20'] = ((result['Close'] - result['Close'].rolling(20).mean()) / result['Close'].rolling(20).mean()) * 100
        
        # 2. 心理线 (PSY)
        up_days = (result['Close'] > result['Close'].shift(1)).rolling(12).sum()
        result['PSY'] = (up_days / 12) * 100
        
        # 3. 威廉指标 (W%R)
        high_14 = result['High'].rolling(14).max()
        low_14 = result['Low'].rolling(14).min()
        result['WR'] = ((high_14 - result['Close']) / (high_14 - low_14)) * 100
        
        return result