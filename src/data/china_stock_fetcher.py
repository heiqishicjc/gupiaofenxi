"""
A股数据获取模块 - 兼容版本

支持 Tushare 和 yfinance 两种数据源
默认使用 Tushare (推荐)，失败时回退到 yfinance
"""

import pandas as pd
from datetime import datetime, timedelta
import os
import warnings

# 尝试导入 Tushare，失败时使用 yfinance
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    warnings.warn("Tushare 不可用，将使用 yfinance")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    warnings.warn("yfinance 不可用，数据获取功能受限")


class ChinaStockFetcher:
    """A股数据获取器 - 兼容版本"""
    
    # A股主要指数代码 (兼容两种格式)
    INDEX_SYMBOLS = {
        '上证指数': {'tushare': '000001.SH', 'yfinance': '000001.SS'},
        '深证成指': {'tushare': '399001.SZ', 'yfinance': '399001.SZ'}, 
        '创业板指': {'tushare': '399006.SZ', 'yfinance': '399006.SZ'},
        '沪深300': {'tushare': '000300.SH', 'yfinance': '000300.SS'},
        '上证50': {'tushare': '000016.SH', 'yfinance': '000016.SS'},
        '中证500': {'tushare': '000905.SH', 'yfinance': '000905.SS'}
    }
    
    # 热门A股股票代码 (兼容两种格式)
    POPULAR_STOCKS = {
        '贵州茅台': {'tushare': '600519.SH', 'yfinance': '600519.SS'},
        '工商银行': {'tushare': '601398.SH', 'yfinance': '601398.SS'},
        '中国平安': {'tushare': '601318.SH', 'yfinance': '601318.SS'},
        '招商银行': {'tushare': '600036.SH', 'yfinance': '600036.SS'},
        '五粮液': {'tushare': '000858.SZ', 'yfinance': '000858.SZ'},
        '宁德时代': {'tushare': '300750.SZ', 'yfinance': '300750.SZ'},
        '比亚迪': {'tushare': '002594.SZ', 'yfinance': '002594.SZ'},
        '中信证券': {'tushare': '600030.SH', 'yfinance': '600030.SS'},
        '万科A': {'tushare': '000002.SZ', 'yfinance': '000002.SZ'},
        '海康威视': {'tushare': '002415.SZ', 'yfinance': '002415.SZ'}
    }
    
    def __init__(self, token="46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad", 
                 cache_dir="data", prefer_tushare=True):
        """
        初始化A股数据获取器 - 兼容版本
        
        Args:
            token: Tushare API Token
            cache_dir: 数据缓存目录
            prefer_tushare: 是否优先使用 Tushare
        """
        self.token = token
        self.cache_dir = cache_dir
        self.prefer_tushare = prefer_tushare
        os.makedirs(cache_dir, exist_ok=True)
        
        # 初始化 Tushare
        if TUSHARE_AVAILABLE:
            try:
                ts.set_token(token)
                self.pro = ts.pro_api()
                print("✅ Tushare API 初始化成功")
            except Exception as e:
                print(f"❌ Tushare 初始化失败: {e}")
                self.pro = None
        else:
            self.pro = None
        
        if YFINANCE_AVAILABLE:
            print("✅ yfinance 可用")
        
        if not TUSHARE_AVAILABLE and not YFINANCE_AVAILABLE:
            raise ImportError("没有可用的数据源，请安装 tushare 或 yfinance")
    
    def get_a_stock_data(self, symbol, period="1y", interval="1d", use_cache=True, start_date=None, end_date=None):
        """
        获取A股股票数据 - 兼容版本
        
        Args:
            symbol: A股股票代码
            period: 数据期间
            interval: 数据间隔
            use_cache: 是否使用缓存
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            pandas.DataFrame: A股股票数据
        """
        # 验证A股代码格式
        if not self._validate_a_stock_symbol(symbol):
            print(f"无效的A股代码格式: {symbol}")
            return None
        
        # 生成缓存文件名
        if start_date and end_date:
            cache_file = os.path.join(self.cache_dir, f"a_stock_{symbol}_{start_date}_{end_date}.csv")
        else:
            cache_file = os.path.join(self.cache_dir, f"a_stock_{symbol}_{period}_{interval}.csv")
        
        # 检查缓存
        if use_cache and os.path.exists(cache_file):
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                print(f"从缓存加载A股数据: {cache_file}")
                return data
            except Exception as e:
                print(f"缓存文件读取失败: {e}")
        
        # 优先使用 Tushare
        if self.prefer_tushare and TUSHARE_AVAILABLE and self.pro:
            data = self._get_data_tushare(symbol, period, start_date, end_date)
            if data is not None:
                # 保存到缓存
                if use_cache:
                    data.to_csv(cache_file)
                    print(f"A股数据已保存到缓存: {cache_file}")
                return data
        
        # 回退到 yfinance
        if YFINANCE_AVAILABLE:
            data = self._get_data_yfinance(symbol, period, interval)
            if data is not None:
                # 保存到缓存
                if use_cache:
                    data.to_csv(cache_file)
                    print(f"A股数据已保存到缓存: {cache_file}")
                return data
        
        print(f"无法获取 {symbol} 的A股数据")
        return None
    
    def _get_data_tushare(self, symbol, period, start_date=None, end_date=None):
        """使用 Tushare 获取数据"""
        try:
            print(f"使用 Tushare 获取A股 {symbol} 数据...")
            
            # 处理日期参数
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            if start_date is None:
                # 根据期间计算开始日期
                end_dt = datetime.strptime(end_date, '%Y%m%d')
                
                if period == "1y":
                    start_dt = end_dt - timedelta(days=365)
                elif period == "6mo":
                    start_dt = end_dt - timedelta(days=180)
                elif period == "3mo":
                    start_dt = end_dt - timedelta(days=90)
                elif period == "1mo":
                    start_dt = end_dt - timedelta(days=30)
                else:
                    start_dt = end_dt - timedelta(days=365)
                
                start_date = start_dt.strftime('%Y%m%d')
            
            # 获取数据
            data = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            
            if data.empty:
                return None
            
            # 数据预处理
            data = self._preprocess_tushare_data(data)
            return data
            
        except Exception as e:
            print(f"Tushare 获取数据失败: {e}")
            return None
    
    def _get_data_yfinance(self, symbol, period, interval):
        """使用 yfinance 获取数据"""
        try:
            print(f"使用 yfinance 获取A股 {symbol} 数据...")
            
            # 转换代码格式
            yf_symbol = symbol.replace('.SH', '.SS').replace('.SZ', '.SZ')
            
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
            
            # 数据预处理
            data = self._preprocess_yfinance_data(data)
            return data
            
        except Exception as e:
            print(f"yfinance 获取数据失败: {e}")
            return None
    
    def get_index_data(self, index_name, period="1y", interval="1d"):
        """获取A股指数数据"""
        if index_name not in self.INDEX_SYMBOLS:
            print(f"不支持的指数: {index_name}")
            return None
        
        # 根据偏好选择数据源
        if self.prefer_tushare and TUSHARE_AVAILABLE:
            symbol = self.INDEX_SYMBOLS[index_name]['tushare']
        else:
            symbol = self.INDEX_SYMBOLS[index_name]['yfinance']
        
        return self.get_a_stock_data(symbol, period, interval)
    
    def get_popular_stock_data(self, stock_name, period="1y", interval="1d"):
        """获取热门A股数据"""
        if stock_name not in self.POPULAR_STOCKS:
            print(f"不支持的股票: {stock_name}")
            return None
        
        # 根据偏好选择数据源
        if self.prefer_tushare and TUSHARE_AVAILABLE:
            symbol = self.POPULAR_STOCKS[stock_name]['tushare']
        else:
            symbol = self.POPULAR_STOCKS[stock_name]['yfinance']
        
        return self.get_a_stock_data(symbol, period, interval)
    
    def _validate_a_stock_symbol(self, symbol):
        """验证A股代码格式"""
        import re
        # 支持 Tushare 和 yfinance 格式
        tushare_pattern = r'^\d{6}\.(SH|SZ)$'
        yfinance_pattern = r'^\d{6}\.(SS|SZ)$'
        
        return (re.match(tushare_pattern, symbol) is not None or 
                re.match(yfinance_pattern, symbol) is not None)
    
    def _preprocess_tushare_data(self, data):
        """Tushare 数据预处理"""
        # 重命名列
        column_mapping = {
            'trade_date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume',
            'amount': 'Amount'
        }
        
        data = data.rename(columns=column_mapping)
        data['Date'] = pd.to_datetime(data['Date'], format='%Y%m%d')
        data = data.set_index('Date').sort_index()
        
        # 计算技术指标
        data['Change'] = data['Close'].pct_change() * 100
        data['Volume_Change'] = data['Volume'].pct_change() * 100
        data['Amplitude'] = ((data['High'] - data['Low']) / data['Close'].shift(1)) * 100
        
        return data[['Open', 'High', 'Low', 'Close', 'Volume', 'Change', 'Volume_Change', 'Amplitude']]
    
    def _preprocess_yfinance_data(self, data):
        """yfinance 数据预处理"""
        # 确保索引是datetime
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        data = data.sort_index()
        
        # 计算技术指标
        data['Change'] = data['Close'].pct_change() * 100
        data['Volume_Change'] = data['Volume'].pct_change() * 100
        data['Amplitude'] = ((data['High'] - data['Low']) / data['Close'].shift(1)) * 100
        
        return data[['Open', 'High', 'Low', 'Close', 'Volume', 'Change', 'Volume_Change', 'Amplitude']]


def test_compatibility():
    """测试兼容性"""
    print("=== 测试 A股数据获取器兼容性 ===")
    
    # 创建数据获取器
    fetcher = ChinaStockFetcher()
    
    # 测试获取股票数据
    print("\n1. 测试获取贵州茅台数据...")
    data = fetcher.get_a_stock_data("600519.SH", period="1mo")
    if data is not None:
        print(f"数据获取成功，共{len(data)}条记录")
        print(f"最新收盘价: {data['Close'].iloc[-1]:.2f}")
    
    # 测试获取指数数据
    print("\n2. 测试获取上证指数数据...")
    index_data = fetcher.get_index_data("上证指数", period="1mo")
    if index_data is not None:
        print(f"上证指数数据获取成功，共{len(index_data)}条记录")
    
    print("\n✅ 兼容性测试完成!")


if __name__ == "__main__":
    test_compatibility()