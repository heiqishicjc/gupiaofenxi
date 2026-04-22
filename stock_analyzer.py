#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票分析器 - 核心分析模块

功能：
1. 多维度技术分析
2. 基本面指标计算
3. 市场情绪分析
4. 风险评估
5. 投资建议生成
"""

import sys
import os

# 首先检查基本依赖
try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"[错误] 缺少必要依赖: {e}")
    print("请运行: pip install pandas numpy")
    sys.exit(1)

from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 设置控制台编码为GBK以支持中文显示
import sys
import io

if sys.platform == "win32":
    try:
        # 设置标准输出编码为GBK
        if sys.stdout.encoding != 'gbk':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gbk', errors='replace')
        if sys.stderr.encoding != 'gbk':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='gbk', errors='replace')
    except Exception:
        pass


# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from indicators.technical_indicators import TechnicalIndicators
    from visualization.chart_plotter import ChartPlotter
    HAS_SRC_MODULES = True
except ImportError:
    print("[!] 注意: 未找到 src 模块，部分功能可能受限")
    HAS_SRC_MODULES = False


class StockAnalyzer:
    """A股股票分析器"""
    
    def __init__(self, data_dir="e:/stockdata"):
        """
        初始化股票分析器
        
        Args:
            data_dir: 股票数据目录
        """
        self.data_dir = data_dir
        self.market_data = {}
        
        # 检查目录是否存在
        import os
        if not os.path.exists(data_dir):
            print(f"[!] 注意: 数据目录 {data_dir} 不存在")
            print(f"将尝试创建目录...")
            os.makedirs(data_dir, exist_ok=True)
            print(f"[OK] 已创建目录: {data_dir}")
        
        # 加载市场数据
        self._load_market_data()
        
        print("[OK] A股股票分析器初始化完成")
        print(f"[文件夹] 数据目录: {data_dir}")
        
        # 显示可用数据统计
        self.show_data_statistics()
    
    def _load_market_data(self):
        """加载各市场数据"""
        market_files = {
            '深圳股市': 'stocksz.csv',
            '上海股市': 'stocksh.csv',
            '其他股市': 'stockother.csv'
        }
        
        for market_name, filename in market_files.items():
            file_path = os.path.join(self.data_dir, filename)
            
            try:
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    self.market_data[market_name] = df
                    print(f"[OK] 成功加载 {market_name} 数据: {len(df)} 条记录")
                else:
                    print(f"[警告] {market_name} 数据文件不存在")
                    
            except Exception as e:
                print(f"[错误] 加载 {market_name} 数据失败: {e}")
    
    def show_data_statistics(self):
        """显示数据统计信息"""
        print("\n[数据统计] 数据统计信息:")
        print("=" * 50)
        
        for market_name, data in self.market_data.items():
            if data is not None and not data.empty:
                stock_count = data['ts_code'].nunique()
                date_count = data['trade_date'].nunique()
                date_range = f"{data['trade_date'].min()} 到 {data['trade_date'].max()}"
                
                print(f"{market_name}:")
                print(f"   股票数量: {stock_count} 只")
                print(f"   交易日数: {date_count} 天")
                print(f"   时间范围: {date_range}")
                print()
    
    def analyze_single_stock(self, symbol, market_name=None):
        """
        分析单只股票
        
        Args:
            symbol: 股票代码 (如: 000001.SZ)
            market_name: 市场名称 (自动检测)
            
        Returns:
            dict: 分析结果
        """
        print(f"\n[分析] 开始分析股票: {symbol}")
        print("-" * 40)
        
        # 自动检测市场
        if market_name is None:
            market_name = self._detect_market(symbol)
        
        if market_name not in self.market_data:
            print(f"错误: 无法找到 {symbol} 的市场数据")
            return None
        
        # 获取股票数据
        stock_data = self._get_stock_data(symbol, market_name)
        
        if stock_data is None or stock_data.empty:
            print(f"错误: 无法获取 {symbol} 的数据")
            return None
        
        print(f"[OK] 成功获取数据: {len(stock_data)} 个交易日")
        
        # 执行分析
        analysis_result = self._perform_analysis(stock_data, symbol)
        
        return analysis_result
    
    def _detect_market(self, symbol):
        """检测股票所属市场"""
        if symbol.endswith('.SZ'):
            return '深圳股市'
        elif symbol.endswith('.SH'):
            return '上海股市'
        elif any(symbol.endswith(suffix) for suffix in ['.BJ', '.NQ', '.OC']):
            return '其他股市'
        else:
            return '未知市场'
    
    def _get_stock_data(self, symbol, market_name):
        """获取指定股票的数据"""
        market_data = self.market_data[market_name]
        
        # 筛选指定股票的数据
        stock_data = market_data[market_data['ts_code'] == symbol].copy()
        
        if stock_data.empty:
            return None
        
        # 转换为时间序列格式
        stock_data['trade_date'] = pd.to_datetime(stock_data['trade_date'], format='%Y%m%d')
        stock_data = stock_data.sort_values('trade_date')
        stock_data.set_index('trade_date', inplace=True)
        
        return stock_data
    
    def _perform_analysis(self, data, symbol):
        """执行完整分析"""
        analysis_result = {
            'symbol': symbol,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': f"{data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}",
            'total_days': len(data)
        }
        
        # 1. 基础统计分析
        print("[1/9] 执行基础统计分析...")
        analysis_result['basic_stats'] = self._calculate_basic_stats(data)
        
        # 2. 技术指标分析
        print("[2/9] 计算技术指标...")
        analysis_result['technical_indicators'] = self._calculate_technical_indicators(data)
        
        # 3. 趋势分析
        print("[3/9] 分析趋势...")
        analysis_result['trend_analysis'] = self._analyze_trend(data)
        
        # 4. 风险评估
        print("[4/9] 评估风险...")
        analysis_result['risk_assessment'] = self._assess_risk(data)
        
        # 5. 资金流向分析
        print("[5/9] 分析资金流向...")
        analysis_result['money_flow'] = self._analyze_money_flow(data)
        
        # 6. 相对强度分析
        print("[6/9] 计算相对强度...")
        analysis_result['relative_strength'] = self._calculate_relative_strength(data)
        
        # 7. 模式识别
        print("[7/9] 识别价格模式...")
        analysis_result['pattern_recognition'] = self._recognize_price_patterns(data)
        
        # 8. 市场情绪分析
        print("[8/9] 分析市场情绪...")
        analysis_result['market_sentiment'] = self._analyze_market_sentiment(data)
        
        # 9. 投资建议
        print("[9/9] 生成投资建议...")
        analysis_result['investment_advice'] = self._generate_advice(analysis_result)
        
        return analysis_result
    
    def _calculate_basic_stats(self, data):
        """计算基础统计指标"""
        stats = {}
        
        # 确保数据足够
        if len(data) < 2:
            return {
                'price_stats': {
                    'current_price': data['close'].iloc[-1] if len(data) > 0 else 0,
                    'price_change_1d': 0,
                    'price_change_1d_pct': 0,
                    'price_change_5d': 0,
                    'price_change_5d_pct': 0,
                    'price_change_1m': None,
                    'price_change_3m': None,
                    'price_change_6m': None,
                    'price_change_1y': None,
                    'high_52w': data['high'].max() if len(data) > 0 else 0,
                    'low_52w': data['low'].min() if len(data) > 0 else 0,
                    'avg_volume': data['vol'].mean() if len(data) > 0 else 0,
                    'avg_amount': data['amount'].mean() if len(data) > 0 else 0,
                    'volume_ratio': None
                },
                'volatility_stats': {
                    'daily_volatility': 0,
                    'annual_volatility': 0,
                    'max_drawdown': 0,
                    'sharpe_ratio': 0,
                    'sortino_ratio': 0,
                    'var_95': 0
                },
                'distribution_stats': {
                    'skewness': 0,
                    'kurtosis': 0,
                    'positive_days': 0,
                    'negative_days': 0
                }
            }
        
        # 价格统计
        price_stats = {
            'current_price': data['close'].iloc[-1],
            'high_52w': data['high'].max(),
            'low_52w': data['low'].min(),
            'avg_volume': data['vol'].mean(),
            'avg_amount': data['amount'].mean(),
        }
        
        # 计算日涨跌
        if len(data) >= 2:
            price_stats['price_change_1d'] = data['close'].iloc[-1] - data['close'].iloc[-2]
            price_stats['price_change_1d_pct'] = ((data['close'].iloc[-1] - data['close'].iloc[-2]) / data['close'].iloc[-2]) * 100 if data['close'].iloc[-2] != 0 else 0
        else:
            price_stats['price_change_1d'] = 0
            price_stats['price_change_1d_pct'] = 0
            
        # 计算5日涨跌
        if len(data) >= 6:
            price_stats['price_change_5d'] = data['close'].iloc[-1] - data['close'].iloc[-6]
            price_stats['price_change_5d_pct'] = ((data['close'].iloc[-1] - data['close'].iloc[-6]) / data['close'].iloc[-6]) * 100 if data['close'].iloc[-6] != 0 else 0
        else:
            price_stats['price_change_5d'] = 0
            price_stats['price_change_5d_pct'] = 0
            
        # 计算其他时间段的涨跌
        price_stats['price_change_1m'] = data['close'].iloc[-1] - data['close'].iloc[-22] if len(data) > 22 else None
        price_stats['price_change_3m'] = data['close'].iloc[-1] - data['close'].iloc[-66] if len(data) > 66 else None
        price_stats['price_change_6m'] = data['close'].iloc[-1] - data['close'].iloc[-132] if len(data) > 132 else None
        price_stats['price_change_1y'] = data['close'].iloc[-1] - data['close'].iloc[-252] if len(data) > 252 else None
        
        # 计算成交量比率
        if len(data) >= 20:
            vol_ma20 = data['vol'].rolling(20).mean()
            if not pd.isna(vol_ma20.iloc[-1]) and vol_ma20.iloc[-1] != 0:
                price_stats['volume_ratio'] = data['vol'].iloc[-1] / vol_ma20.iloc[-1]
            else:
                price_stats['volume_ratio'] = None
        else:
            price_stats['volume_ratio'] = None
            
        stats['price_stats'] = price_stats
        
        # 波动率统计
        returns = data['close'].pct_change().dropna()
        if len(returns) > 0:
            daily_vol = returns.std() * 100
            annual_vol = returns.std() * np.sqrt(252) * 100 if returns.std() > 0 else 0
            sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            sortino = self._calculate_sortino_ratio(returns)
            var_95 = np.percentile(returns, 5) * 100 if len(returns) > 0 else 0
        else:
            daily_vol = 0
            annual_vol = 0
            sharpe = 0
            sortino = 0
            var_95 = 0
            
        stats['volatility_stats'] = {
            'daily_volatility': daily_vol,
            'annual_volatility': annual_vol,
            'max_drawdown': self._calculate_max_drawdown(data['close']),
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'var_95': var_95
        }
        
        # 分布统计
        if len(returns) > 0:
            stats['distribution_stats'] = {
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'positive_days': (returns > 0).sum() / len(returns) * 100,
                'negative_days': (returns < 0).sum() / len(returns) * 100
            }
        else:
            stats['distribution_stats'] = {
                'skewness': 0,
                'kurtosis': 0,
                'positive_days': 0,
                'negative_days': 0
            }
        
        return stats
    
    def _calculate_technical_indicators(self, data):
        """计算技术指标"""
        indicators = {}
        
        # 移动平均线
        indicators['moving_averages'] = {
            'ma5': data['close'].rolling(window=5).mean().iloc[-1],
            'ma10': data['close'].rolling(window=10).mean().iloc[-1],
            'ma20': data['close'].rolling(window=20).mean().iloc[-1],
            'ma60': data['close'].rolling(window=60).mean().iloc[-1]
        }
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]
        
        # MACD
        ema12 = data['close'].ewm(span=12).mean()
        ema26 = data['close'].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        indicators['macd'] = {
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': (macd - signal).iloc[-1]
        }
        
        # 布林带
        bb_middle = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        indicators['bollinger_bands'] = {
            'upper': bb_middle.iloc[-1] + 2 * bb_std.iloc[-1],
            'middle': bb_middle.iloc[-1],
            'lower': bb_middle.iloc[-1] - 2 * bb_std.iloc[-1],
            'band_width': (bb_middle.iloc[-1] + 2 * bb_std.iloc[-1] - (bb_middle.iloc[-1] - 2 * bb_std.iloc[-1])) / bb_middle.iloc[-1]
        }
        
        return indicators
    
    def _analyze_trend(self, data):
        """分析趋势"""
        trend = {}
        
        # 短期趋势 (5日)
        short_trend = self._calculate_trend_strength(data['close'].tail(5))
        trend['short_term'] = short_trend
        
        # 中期趋势 (20日)
        medium_trend = self._calculate_trend_strength(data['close'].tail(20))
        trend['medium_term'] = medium_trend
        
        # 长期趋势 (60日)
        long_trend = self._calculate_trend_strength(data['close'].tail(60))
        trend['long_term'] = long_trend
        
        # 趋势一致性
        trends = [short_trend['direction'], medium_trend['direction'], long_trend['direction']]
        trend['consistency'] = '强' if len(set(trends)) == 1 else '弱'
        
        return trend
    
    def _calculate_trend_strength(self, prices):
        """计算趋势强度"""
        if len(prices) < 2:
            return {'direction': '未知', 'strength': 0}
        
        # 线性回归计算趋势
        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)
        
        direction = '上涨' if slope > 0 else '下跌' if slope < 0 else '震荡'
        strength = abs(slope) / prices.mean() * 100  # 百分比强度
        
        return {
            'direction': direction,
            'strength': strength,
            'slope': slope
        }
    
    def _assess_risk(self, data):
        """风险评估"""
        risk = {}
        
        # 波动率风险
        volatility = data['close'].pct_change().std() * 100
        if volatility < 2:
            risk['volatility_risk'] = '低'
        elif volatility < 5:
            risk['volatility_risk'] = '中'
        else:
            risk['volatility_risk'] = '高'
        
        # 最大回撤风险
        max_dd = self._calculate_max_drawdown(data['close'])
        if max_dd < 0.1:
            risk['drawdown_risk'] = '低'
        elif max_dd < 0.2:
            risk['drawdown_risk'] = '中'
        else:
            risk['drawdown_risk'] = '高'
        
        # 流动性风险 (基于成交量)
        avg_volume = data['vol'].mean()
        if avg_volume > 10000000:
            risk['liquidity_risk'] = '低'
        elif avg_volume > 1000000:
            risk['liquidity_risk'] = '中'
        else:
            risk['liquidity_risk'] = '高'
        
        # 总体风险评级
        risk_scores = {
            '低': 1, '中': 2, '高': 3
        }
        total_score = sum(risk_scores[risk[key]] for key in ['volatility_risk', 'drawdown_risk', 'liquidity_risk'])
        
        if total_score <= 3:
            risk['overall_risk'] = '低风险'
        elif total_score <= 6:
            risk['overall_risk'] = '中风险'
        else:
            risk['overall_risk'] = '高风险'
        
        return risk
    
    def _calculate_max_drawdown(self, prices):
        """计算最大回撤"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    def _calculate_sortino_ratio(self, returns):
        """计算索提诺比率"""
        if len(returns) == 0:
            return 0
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            return 0
        downside_std = negative_returns.std()
        if downside_std == 0:
            return 0
        return returns.mean() / downside_std * np.sqrt(252)
    
    def _analyze_money_flow(self, data):
        """分析资金流向"""
        # 计算资金流向指标
        money_flow = {}
        
        # 典型价格
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        # 资金流
        money_flow_raw = typical_price * data['vol']
        
        # 计算净资金流
        positive_flow = money_flow_raw[data['close'] > data['close'].shift(1)].sum()
        negative_flow = money_flow_raw[data['close'] < data['close'].shift(1)].sum()
        
        net_flow = positive_flow - negative_flow
        money_flow['positive_money_flow'] = positive_flow
        money_flow['negative_money_flow'] = negative_flow
        money_flow['net_money_flow'] = net_flow
        money_flow['net_money_flow_status'] = '净流入' if net_flow > 0 else '净流出'
        
        # 资金流比率
        if negative_flow != 0:
            money_flow['money_flow_ratio'] = positive_flow / abs(negative_flow)
        else:
            money_flow['money_flow_ratio'] = float('inf') if positive_flow > 0 else 0
        
        # 资金流趋势
        money_flow_series = typical_price * data['vol']
        money_flow_ma5 = money_flow_series.rolling(5).mean()
        money_flow_ma20 = money_flow_series.rolling(20).mean()
        
        money_flow['money_flow_trend'] = '上升' if money_flow_ma5.iloc[-1] > money_flow_ma20.iloc[-1] else '下降'
        
        return money_flow
    
    def _calculate_relative_strength(self, data):
        """计算相对强度"""
        rs = {}
        
        # 计算相对于自身均值的强度
        price = data['close']
        ma20 = price.rolling(20).mean()
        ma60 = price.rolling(60).mean()
        
        rs['vs_ma20'] = (price.iloc[-1] / ma20.iloc[-1] - 1) * 100
        rs['vs_ma60'] = (price.iloc[-1] / ma60.iloc[-1] - 1) * 100
        
        # 计算相对强度评级 (0-100)
        # 基于近期表现
        recent_return = (price.iloc[-1] / price.iloc[-20] - 1) * 100 if len(price) >= 20 else 0
        # 标准化到0-100
        rs_rating = min(max((recent_return + 20) / 40 * 100, 0), 100)  # 假设-20%到+20%映射到0-100
        rs['rs_rating'] = rs_rating
        
        # 强度分类
        if rs_rating >= 70:
            rs['strength_category'] = '强'
        elif rs_rating >= 30:
            rs['strength_category'] = '中'
        else:
            rs['strength_category'] = '弱'
        
        return rs
    
    def _recognize_price_patterns(self, data):
        """识别价格模式"""
        patterns = {}
        
        # 检查双顶/双底
        price = data['close']
        recent_prices = price.tail(60)
        
        # 寻找局部极值点
        try:
            # 检查scipy是否可用
            try:
                from scipy.signal import argrelextrema
                HAS_SCIPY = True
            except ImportError:
                HAS_SCIPY = False
            
            if HAS_SCIPY:
                if len(recent_prices) >= 10:
                    # 局部最大值
                    max_indices = argrelextrema(recent_prices.values, np.greater, order=5)[0]
                    # 局部最小值
                    min_indices = argrelextrema(recent_prices.values, np.less, order=5)[0]
                    
                    patterns['local_max_count'] = len(max_indices)
                    patterns['local_min_count'] = len(min_indices)
                    
                    # 检查是否形成头肩形态
                    if len(max_indices) >= 3:
                        patterns['potential_head_shoulders'] = '可能'
                    else:
                        patterns['potential_head_shoulders'] = '未识别'
                    
                    # 检查双顶/双底模式
                    if len(max_indices) >= 2:
                        # 检查两个峰值是否接近
                        peak_values = recent_prices.iloc[max_indices].values
                        if len(peak_values) >= 2:
                            peak_diff = abs(peak_values[-1] - peak_values[-2]) / peak_values[-2]
                            if peak_diff < 0.05:  # 5% 以内
                                patterns['double_top'] = '可能'
                            else:
                                patterns['double_top'] = '未识别'
                    
                    if len(min_indices) >= 2:
                        # 检查两个谷底是否接近
                        trough_values = recent_prices.iloc[min_indices].values
                        if len(trough_values) >= 2:
                            trough_diff = abs(trough_values[-1] - trough_values[-2]) / trough_values[-2]
                            if trough_diff < 0.05:  # 5% 以内
                                patterns['double_bottom'] = '可能'
                            else:
                                patterns['double_bottom'] = '未识别'
                else:
                    patterns['local_max_count'] = 0
                    patterns['local_min_count'] = 0
                    patterns['potential_head_shoulders'] = '数据不足'
                    patterns['double_top'] = '数据不足'
                    patterns['double_bottom'] = '数据不足'
            else:
                # scipy 不可用，使用简单方法
                patterns['local_max_count'] = '需要scipy库'
                patterns['local_min_count'] = '需要scipy库'
                patterns['potential_head_shoulders'] = '需要scipy库'
                patterns['double_top'] = '需要scipy库'
                patterns['double_bottom'] = '需要scipy库'
            
            # 检查趋势线突破
            # 简单实现：检查价格是否突破近期高/低点
            if len(recent_prices) > 0:
                recent_high = recent_prices.max()
                recent_low = recent_prices.min()
                current_price = price.iloc[-1]
                
                if recent_high > 0 and current_price >= recent_high * 0.98:
                    patterns['breakout_status'] = '接近突破高点'
                elif recent_low > 0 and current_price <= recent_low * 1.02:
                    patterns['breakout_status'] = '接近突破低点'
                else:
                    patterns['breakout_status'] = '区间震荡'
            else:
                patterns['breakout_status'] = '数据不足'
                
        except Exception as e:
            patterns['error'] = str(e)
            patterns['potential_head_shoulders'] = '计算错误'
            patterns['breakout_status'] = '未知'
            patterns['double_top'] = '计算错误'
            patterns['double_bottom'] = '计算错误'
        
        # 支撑阻力位
        if len(price) >= 20:
            patterns['support_level'] = price.tail(20).min()
            patterns['resistance_level'] = price.tail(20).max()
        else:
            patterns['support_level'] = price.min() if len(price) > 0 else 0
            patterns['resistance_level'] = price.max() if len(price) > 0 else 0
        
        return patterns
    
    def _analyze_market_sentiment(self, data):
        """分析市场情绪"""
        sentiment = {}
        
        # 基于价格和成交量
        price = data['close']
        volume = data['vol']
        
        # 价格动量
        price_change_5d = (price.iloc[-1] / price.iloc[-5] - 1) * 100 if len(price) >= 5 else 0
        price_change_20d = (price.iloc[-1] / price.iloc[-20] - 1) * 100 if len(price) >= 20 else 0
        
        sentiment['price_momentum_5d'] = price_change_5d
        sentiment['price_momentum_20d'] = price_change_20d
        
        # 成交量情绪
        volume_ratio = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else 1
        sentiment['volume_ratio'] = volume_ratio
        
        # 情绪分数
        sentiment_score = 0
        if price_change_5d > 0:
            sentiment_score += 1
        if price_change_20d > 0:
            sentiment_score += 1
        if volume_ratio > 1.2:
            sentiment_score += 1
        if volume_ratio < 0.8:
            sentiment_score -= 1
        
        sentiment['sentiment_score'] = sentiment_score
        
        # 情绪分类
        if sentiment_score >= 2:
            sentiment['sentiment_category'] = '乐观'
        elif sentiment_score <= -1:
            sentiment['sentiment_category'] = '悲观'
        else:
            sentiment['sentiment_category'] = '中性'
        
        return sentiment
    
    def _generate_advice(self, analysis_result):
        """生成投资建议"""
        advice = {}
        
        basic_stats = analysis_result['basic_stats']
        technical = analysis_result['technical_indicators']
        trend = analysis_result['trend_analysis']
        risk = analysis_result['risk_assessment']
        money_flow = analysis_result.get('money_flow', {})
        relative_strength = analysis_result.get('relative_strength', {})
        pattern = analysis_result.get('pattern_recognition', {})
        sentiment = analysis_result.get('market_sentiment', {})
        
        # 技术面建议
        current_price = basic_stats['price_stats']['current_price']
        ma20 = technical['moving_averages']['ma20']
        rsi = technical['rsi']
        macd_hist = technical['macd']['histogram']
        
        tech_signals = []
        if current_price > ma20:
            tech_signals.append('价格在MA20之上')
        if rsi < 70:
            tech_signals.append('RSI未超买')
        if rsi > 30:
            tech_signals.append('RSI未超卖')
        if macd_hist > 0:
            tech_signals.append('MACD柱状图为正')
        
        # 综合技术信号
        tech_score = sum([
            1 if current_price > ma20 else -1,
            1 if 30 < rsi < 70 else 0,
            1 if macd_hist > 0 else -1
        ])
        
        if tech_score >= 2:
            advice['technical_signal'] = '买入信号'
        elif tech_score <= -2:
            advice['technical_signal'] = '卖出信号'
        else:
            advice['technical_signal'] = '持有观望'
        
        # 趋势建议
        if trend['consistency'] == '强' and trend['short_term']['direction'] == '上涨':
            advice['trend_signal'] = '趋势向上，建议关注'
        elif trend['consistency'] == '强' and trend['short_term']['direction'] == '下跌':
            advice['trend_signal'] = '趋势向下，谨慎操作'
        else:
            advice['trend_signal'] = '趋势不明，建议观望'
        
        # 风险建议
        if risk['overall_risk'] == '低风险':
            advice['risk_signal'] = '风险较低，适合投资'
        elif risk['overall_risk'] == '中风险':
            advice['risk_signal'] = '风险适中，注意控制仓位'
        else:
            advice['risk_signal'] = '风险较高，谨慎投资'
        
        # 资金流向建议
        if money_flow.get('net_money_flow_status') == '净流入':
            advice['money_flow_signal'] = '资金净流入，积极信号'
        elif money_flow.get('net_money_flow_status') == '净流出':
            advice['money_flow_signal'] = '资金净流出，谨慎信号'
        else:
            advice['money_flow_signal'] = '资金流向中性'
        
        # 相对强度建议
        if relative_strength.get('rs_rating', 0) > 70:
            advice['relative_strength_signal'] = '相对强度强，表现优于市场'
        elif relative_strength.get('rs_rating', 0) < 30:
            advice['relative_strength_signal'] = '相对强度弱，表现劣于市场'
        else:
            advice['relative_strength_signal'] = '相对强度中等'
        
        # 综合建议
        positive_signals = 0
        negative_signals = 0
        
        if advice['technical_signal'] == '买入信号':
            positive_signals += 1
        elif advice['technical_signal'] == '卖出信号':
            negative_signals += 1
            
        if advice['trend_signal'] == '趋势向上，建议关注':
            positive_signals += 1
        elif advice['trend_signal'] == '趋势向下，谨慎操作':
            negative_signals += 1
            
        if advice['money_flow_signal'] == '资金净流入，积极信号':
            positive_signals += 1
        elif advice['money_flow_signal'] == '资金净流出，谨慎信号':
            negative_signals += 1
        
        if positive_signals >= 2 and negative_signals == 0:
            advice['overall_advice'] = '强烈推荐买入'
        elif negative_signals >= 2 and positive_signals == 0:
            advice['overall_advice'] = '建议卖出'
        elif positive_signals > negative_signals:
            advice['overall_advice'] = '谨慎买入'
        elif negative_signals > positive_signals:
            advice['overall_advice'] = '谨慎卖出'
        else:
            advice['overall_advice'] = '持有观望'
        
        return advice
    
    def print_analysis_report(self, analysis_result):
        """打印分析报告"""
        if analysis_result is None:
            print("[错误] 分析结果为空")
            return
        
        print(f"\n[报告] 股票分析报告 - {analysis_result['symbol']}")
        print("=" * 60)
        print(f"分析时间: {analysis_result['analysis_date']}")
        print(f"数据期间: {analysis_result['data_period']}")
        print(f"总交易日: {analysis_result['total_days']}")
        
        # 基础统计
        print("\n[基础统计] 基础统计:")
        stats = analysis_result['basic_stats']['price_stats']
        print(f"   当前价格: {stats['current_price']:.2f}")
        print(f"   日涨跌: {stats['price_change_1d']:.2f} ({stats['price_change_1d_pct']:.2f}%)")
        print(f"   5日涨跌: {stats['price_change_5d']:.2f} ({stats['price_change_5d_pct']:.2f}%)")
        print(f"   52周最高: {stats['high_52w']:.2f}")
        print(f"   52周最低: {stats['low_52w']:.2f}")
        
        # 技术指标
        print("\n[技术指标] 技术指标:")
        tech = analysis_result['technical_indicators']
        print(f"   MA5: {tech['moving_averages']['ma5']:.2f}")
        print(f"   MA20: {tech['moving_averages']['ma20']:.2f}")
        print(f"   RSI: {tech['rsi']:.2f}")
        print(f"   MACD: {tech['macd']['macd']:.4f}")
        
        # 趋势分析
        print("\n[趋势分析] 趋势分析:")
        trend = analysis_result['trend_analysis']
        print(f"   短期趋势: {trend['short_term']['direction']} (强度: {trend['short_term']['strength']:.2f}%)")
        print(f"   中期趋势: {trend['medium_term']['direction']} (强度: {trend['medium_term']['strength']:.2f}%)")
        print(f"   趋势一致性: {trend['consistency']}")
        
        # 风险评估
        print("\n[风险评估] 风险评估:")
        risk = analysis_result['risk_assessment']
        print(f"   波动率风险: {risk['volatility_risk']}")
        print(f"   回撤风险: {risk['drawdown_risk']}")
        print(f"   流动性风险: {risk['liquidity_risk']}")
        print(f"   总体风险: {risk['overall_risk']}")
        
        # 投资建议
        print("\n[投资建议] 投资建议:")
        advice = analysis_result['investment_advice']
        print(f"   技术信号: {advice['technical_signal']}")
        print(f"   趋势信号: {advice['trend_signal']}")
        print(f"   风险信号: {advice['risk_signal']}")
        print(f"   综合建议: {advice['overall_advice']}")
        
        print("=" * 60)


def main():
    """主函数 - 演示分析器功能"""
    import sys
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 如果有命令行参数，直接分析指定的股票
        symbol = sys.argv[1].strip().upper()
        print(f"A股股票分析器 - 直接分析模式")
        print("=" * 50)
        sys.stdout.flush()
        sys.stdout.flush()
        
        # 检查scipy是否可用
        try:
            import scipy
            print(f"[OK] scipy 版本: {scipy.__version__}")
        except ImportError:
            print("[警告] scipy 未安装，模式识别功能将受限")
        
        try:
            # 创建分析器
            analyzer = StockAnalyzer()
            
            # 验证股票代码格式
            if not (symbol.endswith('.SZ') or symbol.endswith('.SH') or symbol.endswith('.BJ')):
                print(f"[错误] 股票代码 {symbol} 格式不正确")
                print("股票代码应以 .SZ、.SH 或 .BJ 结尾")
                print("例如: 000001.SZ, 600000.SH, 430001.BJ")
                sys.exit(1)
            
            print(f"\n[分析] 正在分析 {symbol}...")
            result = analyzer.analyze_single_stock(symbol)
            if result:
                analyzer.print_analysis_report(result)
            else:
                print(f"[错误] 无法分析 {symbol}")
                print("可能原因:")
                print("1. 数据文件中没有该股票的数据")
                print("2. 股票代码格式不正确")
                print("3. 数据文件可能不完整")
                sys.exit(1)
            
            sys.exit(0)
            
        except Exception as e:
            print(f"[错误] 运行过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # 如果没有命令行参数，进入交互式模式
    print("A股股票分析器演示")
    print("=" * 50)
    sys.stdout.flush()
    sys.stdout.flush()
    sys.stdout.flush()
    sys.stdout.flush()
    sys.stdout.flush()
    
    # 检查scipy是否可用
    try:
        import scipy
        print(f"[OK] scipy 版本: {scipy.__version__}")
        HAS_SCIPY = True
    except ImportError:
        print("[警告] scipy 未安装，模式识别功能将受限")
        print("   如需完整功能，请运行: pip install scipy")
        HAS_SCIPY = False
    
    try:
        # 创建分析器
        analyzer = StockAnalyzer()
        sys.stdout.flush()
        sys.stdout.flush()
        
        # 检查是否有市场数据
        if not analyzer.market_data:
            print("[警告] 未找到任何市场数据文件")
            print("请确保以下文件存在于 e:/stockdata 目录中:")
            print("  - stocksz.csv (深圳股市)")
            print("  - stocksh.csv (上海股市)")
            print("  - stockother.csv (其他股市)")
            print("\n正在创建示例数据文件以供演示...")
            
            # 创建示例数据目录
            import os
            data_dir = "e:/stockdata"
            os.makedirs(data_dir, exist_ok=True)
            
            # 创建示例数据文件
            import pandas as pd
            from datetime import datetime, timedelta
            
            # 生成示例数据
            dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
            
            # 示例股票数据
            sample_data = []
            for i, date in enumerate(dates):
                sample_data.append({
                    'ts_code': '000001.SZ',
                    'trade_date': date.strftime('%Y%m%d'),
                    'open': 10.0 + i * 0.01,
                    'high': 10.5 + i * 0.01,
                    'low': 9.5 + i * 0.01,
                    'close': 10.0 + i * 0.02,
                    'vol': 1000000 + i * 10000,
                    'amount': 10000000 + i * 100000
                })
            
            df = pd.DataFrame(sample_data)
            df.to_csv(os.path.join(data_dir, 'stocksz.csv'), index=False)
            print("[OK] 已创建示例数据文件: stocksz.csv")
            
            # 重新加载数据
            analyzer._load_market_data()
        
        # 交互式分析
        while True:
            print("\n" + "="*60)
            print("请选择操作:")
            print("1. 分析示例股票 (000001.SZ 平安银行)")
            print("2. 输入股票代码进行分析")
            print("3. 显示市场统计信息")
            print("4. 退出")
            print("提示: 也可以直接运行 'py stock_analyzer.py 股票代码' 进行分析")
            
            try:
                # 确保提示立即显示
                import sys
                sys.stdout.flush()
                choice = input("\n请输入选项 (1-4): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[再见] 检测到退出信号，感谢使用 A股股票分析器，再见！")
                break
            
            if choice == '':
                print("[提示] 检测到空输入，请输入选项编号 (1-4)")
                print("[提示] 直接按回车将重新显示菜单")
                continue
            
            if choice == '1':
                # 示例股票分析
                symbol = '000001.SZ'
                name = '平安银行'
                print(f"\n[分析] 正在分析 {name} ({symbol})...")
                result = analyzer.analyze_single_stock(symbol)
                if result:
                    analyzer.print_analysis_report(result)
                else:
                    print(f"[错误] 无法分析 {symbol}，跳过...")
            
            elif choice == '2':
                # 用户输入股票代码
                try:
                    sys.stdout.flush()
                    symbol = input("请输入股票代码 (例如: 000001.SZ): ").strip().upper()
                except (EOFError, KeyboardInterrupt):
                    print("\n[提示] 已取消输入，返回主菜单")
                    continue
                
                if not symbol:
                    print("[错误] 股票代码不能为空")
                    print("[提示] 请输入有效的股票代码，如 000001.SZ, 600000.SH")
                    continue
                
                # 验证股票代码格式
                if not (symbol.endswith('.SZ') or symbol.endswith('.SH') or symbol.endswith('.BJ')):
                    print("[警告] 股票代码应以 .SZ、.SH 或 .BJ 结尾")
                    print("   例如: 000001.SZ (深圳), 600000.SH (上海), 430001.BJ (北京)")
                    print("   请重新输入正确的股票代码格式")
                    continue
                
                # 获取股票名称（如果有）
                try:
                    sys.stdout.flush()
                    name = input("请输入股票名称 (可选，按Enter跳过): ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[提示] 已取消输入，使用股票代码作为名称")
                    name = symbol
                
                if not name:
                    name = symbol
                
                print(f"\n[分析] 正在分析 {name} ({symbol})...")
                result = analyzer.analyze_single_stock(symbol)
                if result:
                    analyzer.print_analysis_report(result)
                else:
                    print(f"[错误] 无法分析 {symbol}，可能数据文件中没有该股票的数据")
                    print("   请确保数据文件包含该股票的信息")
                    print("   注意: 股票代码必须与数据文件中的格式完全一致")
            
            elif choice == '3':
                # 显示市场统计信息
                analyzer.show_data_statistics()
            
            elif choice == '4':
                print("[再见] 感谢使用 A股股票分析器，再见！")
                break
            
            else:
                print(f"[错误] 无效选项 '{choice}'，请输入 1-4 之间的数字")
                print("[提示] 有效选项为: 1, 2, 3, 4")
                
    except Exception as e:
        print(f"[错误] 运行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n[建议] 建议:")
        print("1. 确保已安装所需依赖: pip install pandas numpy")
        print("2. 如果需要模式识别功能: pip install scipy")
        print("3. 检查数据目录是否存在: e:/stockdata")


if __name__ == "__main__":
    
    # 检查基本依赖
    try:
        import pandas as pd
        import numpy as np
        print("[OK] 基本依赖检查通过")
    except ImportError as e:
        print(f"[错误] 缺少必要依赖: {e}")
        print("请运行: pip install pandas numpy")
        sys.exit(1)
    
    # 运行主函数
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[再见] 程序被用户中断，感谢使用 A股股票分析器！")
    except Exception as e:
        print(f"\n[错误] 程序运行出现未预期错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n[提示] 提示:")
    print("1. 要分析其他股票，请使用选项2输入股票代码")
    print("2. 确保数据文件位于 e:/stockdata 目录中")
    print("3. 如需完整功能，建议安装: pip install scipy")
    print("4. 按Ctrl+C可随时退出程序")
