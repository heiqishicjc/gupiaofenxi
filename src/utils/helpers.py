"""
工具函数模块

提供常用的辅助函数：
1. 数据验证和清理
2. 日期处理
3. 文件操作
4. 数学计算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

def validate_stock_data(data):
    """
    验证股票数据的完整性
    
    Args:
        data: 股票数据DataFrame
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if data is None or data.empty:
        return False, "数据为空"
    
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        return False, f"缺少必要列: {missing_columns}"
    
    # 检查数据有效性
    if data['Close'].isna().any():
        return False, "存在空值数据"
    
    if (data['Close'] <= 0).any():
        return False, "存在无效价格数据"
    
    return True, "数据有效"

def clean_stock_data(data):
    """
    清理股票数据
    
    Args:
        data: 原始股票数据
        
    Returns:
        pandas.DataFrame: 清理后的数据
    """
    cleaned_data = data.copy()
    
    # 删除重复行
    cleaned_data = cleaned_data.drop_duplicates()
    
    # 按日期排序
    cleaned_data = cleaned_data.sort_index()
    
    # 处理缺失值
    cleaned_data = cleaned_data.ffill()  # 前向填充
    cleaned_data = cleaned_data.bfill()  # 后向填充
    
    # 删除仍然有缺失值的行
    cleaned_data = cleaned_data.dropna()
    
    # 确保价格数据有效
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        cleaned_data = cleaned_data[cleaned_data[col] > 0]
    
    return cleaned_data

def calculate_returns(data, period=1):
    """
    计算收益率
    
    Args:
        data: 股票数据
        period: 收益率计算周期
        
    Returns:
        pandas.Series: 收益率序列
    """
    return data['Close'].pct_change(periods=period)

def calculate_volatility(data, window=20):
    """
    计算波动率
    
    Args:
        data: 股票数据
        window: 计算窗口
        
    Returns:
        pandas.Series: 波动率序列
    """
    returns = calculate_returns(data)
    return returns.rolling(window=window).std() * np.sqrt(252)  # 年化波动率

def format_currency(value):
    """
    格式化货币显示
    
    Args:
        value: 数值
        
    Returns:
        str: 格式化后的货币字符串
    """
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

def format_percentage(value):
    """
    格式化百分比显示
    
    Args:
        value: 数值
        
    Returns:
        str: 格式化后的百分比字符串
    """
    return f"{value:.2f}%"

def get_date_range(days=365):
    """
    获取日期范围
    
    Args:
        days: 天数
        
    Returns:
        tuple: (开始日期, 结束日期)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def save_to_json(data, filename):
    """
    保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        filename: 文件名
        
    Returns:
        bool: 是否保存成功
    """
    try:
        # 处理DataFrame类型
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return True
    except Exception as e:
        print(f"保存JSON文件失败: {e}")
        return False

def load_from_json(filename):
    """
    从JSON文件加载数据
    
    Args:
        filename: 文件名
        
    Returns:
        dict or list: 加载的数据
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败: {e}")
        return None

def calculate_correlation_matrix(stocks_data):
    """
    计算股票相关性矩阵
    
    Args:
        stocks_data: 股票数据字典 {symbol: data}
        
    Returns:
        pandas.DataFrame: 相关性矩阵
    """
    # 提取收盘价数据
    close_prices = pd.DataFrame()
    
    for symbol, data in stocks_data.items():
        close_prices[symbol] = data['Close']
    
    # 计算收益率
    returns = close_prices.pct_change().dropna()
    
    # 计算相关性矩阵
    correlation_matrix = returns.corr()
    
    return correlation_matrix

def detect_anomalies(data, column='Close', threshold=3):
    """
    检测数据异常值
    
    Args:
        data: 股票数据
        column: 检测列
        threshold: 异常值阈值（标准差倍数）
        
    Returns:
        pandas.Series: 异常值布尔序列
    """
    values = data[column]
    z_scores = (values - values.mean()) / values.std()
    
    return abs(z_scores) > threshold

def calculate_portfolio_returns(weights, returns):
    """
    计算投资组合收益率
    
    Args:
        weights: 权重数组
        returns: 收益率DataFrame
        
    Returns:
        pandas.Series: 投资组合收益率
    """
    return (returns * weights).sum(axis=1)

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率
        
    Returns:
        float: 夏普比率
    """
    excess_returns = returns - risk_free_rate / 252  # 日化无风险利率
    
    if len(excess_returns) == 0:
        return 0
    
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    return sharpe_ratio

def calculate_max_drawdown(returns):
    """
    计算最大回撤
    
    Args:
        returns: 收益率序列
        
    Returns:
        tuple: (最大回撤, 回撤开始日期, 回撤结束日期)
    """
    cumulative_returns = (1 + returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    
    max_drawdown = drawdown.min()
    max_drawdown_end = drawdown.idxmin()
    
    # 找到回撤开始日期
    running_max_until_drawdown = running_max.loc[:max_drawdown_end]
    if not running_max_until_drawdown.empty:
        max_drawdown_start = running_max_until_drawdown.idxmax()
    else:
        max_drawdown_start = max_drawdown_end
    
    return max_drawdown, max_drawdown_start, max_drawdown_end