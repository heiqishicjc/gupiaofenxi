"""
A股数据获取模块 - Tushare 修复版本

修复权限问题，使用项目目录内的缓存
"""

import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
import os
import time

class ChinaStockFetcherTushareFixed:
    """A股数据获取器 - Tushare 修复版本"""
    
    # A股主要指数代码 (Tushare 格式)
    INDEX_SYMBOLS = {
        '上证指数': '000001.SH',
        '深证成指': '399001.SZ', 
        '创业板指': '399006.SZ',
        '沪深300': '000300.SH',
        '上证50': '000016.SH',
        '中证500': '000905.SH'
    }
    
    # 热门A股股票代码 (Tushare 格式)
    POPULAR_STOCKS = {
        '贵州茅台': '600519.SH',
        '工商银行': '601398.SH',
        '中国平安': '601318.SH',
        '招商银行': '600036.SH',
        '五粮液': '000858.SZ',
        '宁德时代': '300750.SZ',
        '比亚迪': '002594.SZ',
        '中信证券': '600030.SH',
        '万科A': '000002.SZ',
        '海康威视': '002415.SZ'
    }
    
    def __init__(self, token="46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad", 
                 cache_dir="data/tushare_cache"):
        """
        初始化A股数据获取器 - Tushare 修复版本
        
        Args:
            token: Tushare API Token
            cache_dir: 数据缓存目录（项目相对路径）
        """
        self.token = token
        
        # 使用项目相对路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cache_dir = os.path.join(project_root, cache_dir)
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 设置 Tushare Token
        ts.set_token(token)
        self.pro = ts.pro_api()
        
        print("✅ Tushare API 初始化成功")
        print(f"📁 缓存目录: {self.cache_dir}")
    
    def get_a_stock_data(self, symbol, start_date=None, end_date=None, period="1y", use_cache=True):
        """
        获取A股股票数据 - Tushare 修复版本
        
        Args:
            symbol: A股股票代码 (如: 600036.SH, 000858.SZ)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 数据期间 (1y, 6mo, 3mo, 1mo)
            use_cache: 是否使用缓存
            
        Returns:
            pandas.DataFrame: A股股票数据
        """
        # 验证A股代码格式
        if not self._validate_a_stock_symbol(symbol):
            print(f"无效的A股代码格式: {symbol}")
            return None
        
        # 处理日期参数
        start_date, end_date = self._process_dates(start_date, end_date, period)
        
        cache_file = os.path.join(self.cache_dir, f"a_stock_{symbol}_{start_date}_{end_date}.csv")
        
        # 检查缓存
        if use_cache and os.path.exists(cache_file):
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                print(f"从缓存加载A股数据: {os.path.basename(cache_file)}")
                return data
            except Exception as e:
                print(f"缓存文件读取失败: {e}")
        
        # 从 Tushare 获取数据
        try:
            print(f"正在获取A股 {symbol} 数据...")
            
            # 使用 Tushare 获取A股日线数据
            data = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            
            if data.empty:
                print(f"未找到 {symbol} 的A股数据")
                return None
            
            # 数据预处理
            data = self._preprocess_tushare_data(data)
            
            # 保存到缓存
            if use_cache:
                try:
                    data.to_csv(cache_file)
                    print(f"A股数据已保存到缓存: {os.path.basename(cache_file)}")
                except Exception as e:
                    print(f"缓存保存失败: {e}")
            
            return data
            
        except Exception as e:
            print(f"获取A股数据失败: {e}")
            return None
    
    def get_index_data(self, index_name, start_date=None, end_date=None, period="1y"):
        """获取A股指数数据"""
        if index_name not in self.INDEX_SYMBOLS:
            print(f"不支持的指数: {index_name}")
            return None
        
        symbol = self.INDEX_SYMBOLS[index_name]
        return self.get_a_stock_data(symbol, start_date, end_date, period)
    
    def get_popular_stock_data(self, stock_name, start_date=None, end_date=None, period="1y"):
        """获取热门A股数据"""
        if stock_name not in self.POPULAR_STOCKS:
            print(f"不支持的股票: {stock_name}")
            return None
        
        symbol = self.POPULAR_STOCKS[stock_name]
        return self.get_a_stock_data(symbol, start_date, end_date, period)
    
    def get_a_stock_info(self, symbol):
        """获取A股基本信息"""
        try:
            # 使用 Tushare 获取股票基本信息
            stock_basic = self.pro.stock_basic(ts_code=symbol)
            
            if stock_basic.empty:
                return None
            
            # 提取股票信息
            info = stock_basic.iloc[0]
            stock_info = {
                'symbol': symbol,
                'name': info.get('name', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market': info.get('market', 'N/A'),
                'list_date': info.get('list_date', 'N/A'),
                'area': info.get('area', 'N/A'),
                'fullname': info.get('fullname', 'N/A'),
                'enname': info.get('enname', 'N/A')
            }
            
            return stock_info
            
        except Exception as e:
            print(f"获取A股信息失败: {e}")
            return None
    
    def _validate_a_stock_symbol(self, symbol):
        """验证A股代码格式"""
        import re
        pattern = r'^\d{6}\.(SH|SZ)$'
        return re.match(pattern, symbol) is not None
    
    def _process_dates(self, start_date, end_date, period):
        """处理日期参数"""
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
        
        return start_date, end_date
    
    def _preprocess_tushare_data(self, data):
        """Tushare 数据预处理"""
        # 重命名列以匹配标准OHLC格式
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
        
        # 转换日期格式
        data['Date'] = pd.to_datetime(data['Date'], format='%Y%m%d')
        
        # 设置日期为索引
        data = data.set_index('Date')
        
        # 按日期排序
        data = data.sort_index()
        
        # 计算涨跌幅
        data['Change'] = data['Close'].pct_change() * 100
        
        # 计算成交量变化
        data['Volume_Change'] = data['Volume'].pct_change() * 100
        
        # 计算振幅
        data['Amplitude'] = ((data['High'] - data['Low']) / data['Close'].shift(1)) * 100
        
        # 保留需要的列
        columns_to_keep = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'Change', 'Volume_Change', 'Amplitude']
        data = data[[col for col in columns_to_keep if col in data.columns]]
        
        return data


def test_fixed_version():
    """测试修复版本"""
    print("=== 测试修复的 Tushare 版本 ===")
    
    try:
        # 创建数据获取器
        fetcher = ChinaStockFetcherTushareFixed()
        
        # 测试获取单只股票数据
        print("\n1. 测试获取贵州茅台数据...")
        data = fetcher.get_a_stock_data("600519.SH", period="1mo")
        if data is not None:
            print(f"✅ 数据获取成功，共{len(data)}条记录")
            print(f"   最新收盘价: {data['Close'].iloc[-1]:.2f}")
            print(f"   数据范围: {data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}")
        else:
            print("❌ 数据获取失败")
        
        # 测试获取指数数据
        print("\n2. 测试获取上证指数数据...")
        index_data = fetcher.get_index_data("上证指数", period="1mo")
        if index_data is not None:
            print(f"✅ 指数数据获取成功，共{len(index_data)}条记录")
        else:
            print("❌ 指数数据获取失败")
        
        # 测试获取股票信息
        print("\n3. 测试获取股票基本信息...")
        stock_info = fetcher.get_a_stock_info("600519.SH")
        if stock_info is not None:
            print(f"✅ 股票信息获取成功")
            print(f"   股票名称: {stock_info.get('name', 'N/A')}")
            print(f"   所属行业: {stock_info.get('industry', 'N/A')}")
        else:
            print("❌ 股票信息获取失败")
        
        print("\n✅ 修复版本测试完成!")
        
    except Exception as e:
        print(f"❌ 修复版本测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fixed_version()