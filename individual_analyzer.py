#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股个股分析器 - 升级版核心分析模块

功能：
1. 支持交互式股票代码输入
2. 多维度技术分析
3. 基本面指标计算
4. 市场情绪分析
5. 风险评估
6. 投资建议生成
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from indicators.technical_indicators import TechnicalIndicators
from visualization.chart_plotter import ChartPlotter


class IndividualAnalyzer:
    """A股个股分析器"""
    
    def __init__(self, data_dir="e:/stockdata"):
        """
        初始化个股分析器
        
        Args:
            data_dir: 股票数据目录
        """
        self.data_dir = data_dir
        self.market_data = {}
        
        # 加载市场数据
        self._load_market_data()
        
        print("A股个股分析器初始化完成")
        print(f"数据目录: {data_dir}")
        
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
                    print(f"成功加载 {market_name} 数据: {len(df)} 条记录")
                else:
                    print(f"警告: {market_name} 数据文件不存在")
                    
            except Exception as e:
                print(f"加载 {market_name} 数据失败: {e}")
    
    def show_data_statistics(self):
        """显示数据统计信息"""
        print("\n数据统计信息:")
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
    
    def interactive_analysis(self):
        """交互式个股分析"""
        print("\n交互式个股分析")
        print("=" * 50)
        
        while True:
            print("\n请选择操作:")
            print("1. 输入股票代码进行分析")
            print("2. 查看示例股票分析")
            print("3. 返回主菜单")
            
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                self._analyze_custom_stock()
            
            elif choice == "2":
                self._analyze_sample_stocks()
            
            elif choice == "3":
                print("返回主菜单")
                break
            
            else:
                print("错误: 无效选择，请重新输入")
    
    def _analyze_custom_stock(self):
        """分析用户自定义股票"""
        while True:
            print("\n请输入股票代码 (格式: 000001.SZ 或 600519.SH)")
            print("输入 'back' 返回上一级")
            
            symbol = input("股票代码: ").strip().upper()
            
            if symbol.lower() == 'back':
                return
            
            # 验证股票代码格式
            if not self._validate_stock_symbol(symbol):
                print("❌ 股票代码格式错误，请重新输入")
                continue
            
            # 检查股票是否存在
            if not self._check_stock_exists(symbol):
                print(f"❌ 股票 {symbol} 不存在于数据库中")
                continue
            
            # 执行分析
            print(f"\n开始分析股票: {symbol}")
            result = self.analyze_single_stock(symbol)
            
            if result:
                self.print_analysis_report(result)
                
                # 询问是否继续分析
                continue_analysis = input("\n是否继续分析其他股票？(y/N): ").strip().lower()
                if continue_analysis != 'y':
                    break
            else:
                print(f"❌ 分析股票 {symbol} 失败")
    
    def _validate_stock_symbol(self, symbol):
        """验证股票代码格式"""
        valid_suffixes = ['.SZ', '.SH', '.BJ', '.NQ', '.OC']
        
        if len(symbol) < 7:
            return False
        
        # 检查后缀
        suffix = symbol[-3:]
        if suffix not in valid_suffixes:
            return False
        
        # 检查代码部分 (6位数字)
        code_part = symbol[:-3]
        if not code_part.isdigit() or len(code_part) != 6:
            return False
        
        return True
    
    def _check_stock_exists(self, symbol):
        """检查股票是否存在于数据库中"""
        market_name = self._detect_market(symbol)
        
        if market_name not in self.market_data:
            return False
        
        market_data = self.market_data[market_name]
        return symbol in market_data['ts_code'].values
    
    def _analyze_sample_stocks(self):
        """分析示例股票"""
        sample_stocks = [
            ('000001.SZ', '平安银行'),
            ('600519.SH', '贵州茅台'),
            ('000858.SZ', '五粮液'),
            ('002415.SZ', '海康威视'),
            ('300750.SZ', '宁德时代')
        ]
        
        print("\n示例股票列表:")
        print("-" * 40)
        for i, (symbol, name) in enumerate(sample_stocks, 1):
            print(f"{i}. {symbol} - {name}")
        
        while True:
            print("\n请选择要分析的股票:")
            print("输入编号 (1-5) 或输入 'all' 分析所有示例股票")
            print("输入 'back' 返回上一级")
            
            choice = input("选择: ").strip().lower()
            
            if choice == 'back':
                return
            
            elif choice == 'all':
                # 分析所有示例股票
                for symbol, name in sample_stocks:
                    print(f"\n{'='*60}")
                    print(f"分析: {name} ({symbol})")
                    print("="*60)
                    
                    result = self.analyze_single_stock(symbol)
                    if result:
                        self.print_analysis_report(result)
                break
            
            elif choice.isdigit() and 1 <= int(choice) <= len(sample_stocks):
                # 分析单个示例股票
                symbol, name = sample_stocks[int(choice) - 1]
                print(f"\n分析: {name} ({symbol})")
                
                result = self.analyze_single_stock(symbol)
                if result:
                    self.print_analysis_report(result)
                
                # 询问是否继续
                continue_analysis = input("\n是否继续分析其他示例股票？(y/N): ").strip().lower()
                if continue_analysis != 'y':
                    break
            
            else:
                print("❌ 无效选择，请重新输入")
    
    def analyze_single_stock(self, symbol, market_name=None):
        """
        分析单只股票
        
        Args:
            symbol: 股票代码 (如: 000001.SZ)
            market_name: 市场名称 (自动检测)
            
        Returns:
            dict: 分析结果
        """
        print(f"\n🔍 开始分析股票: {symbol}")
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
        
        print(f"✅ 成功获取数据: {len(stock_data)} 个交易日")
        
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
        print("1. 执行基础统计分析...")
        analysis_result['basic_stats'] = self._calculate_basic_stats(data)
        
        # 2. 技术指标分析
        print("2. 计算技术指标...")
        analysis_result['technical_indicators'] = self._calculate_technical_indicators(data)
        
        # 3. 趋势分析
        print("3. 分析趋势...")
        analysis_result['trend_analysis'] = self._analyze_trend(data)
        
        # 4. 风险评估
        print("4. 评估风险...")
        analysis_result['risk_assessment'] = self._assess_risk(data)
        
        # 5. 投资建议
        print("5. 生成投资建议...")
        analysis_result['investment_advice'] = self._generate_advice(analysis_result)
        
        return analysis_result
    
    def _calculate_basic_stats(self, data):
        """计算基础统计指标"""
        stats = {}
        
        # 价格统计
        stats['price_stats'] = {
            'current_price': data['close'].iloc[-1],
            'price_change_1d': data['close'].iloc[-1] - data['close'].iloc[-2],
            'price_change_1d_pct': ((data['close'].iloc[-1] - data['close'].iloc[-2]) / data['close'].iloc[-2]) * 100,
            'price_change_5d': data['close'].iloc[-1] - data['close'].iloc[-6],
            'price_change_5d_pct': ((data['close'].iloc[-1] - data['close'].iloc[-6]) / data['close'].iloc[-6]) * 100,
            'price_change_1m': data['close'].iloc[-1] - data['close'].iloc[-22] if len(data) > 22 else None,
            'high_52w': data['high'].max(),
            'low_52w': data['low'].min(),
            'avg_volume': data['vol'].mean(),
            'avg_amount': data['amount'].mean()
        }
        
        # 波动率统计
        returns = data['close'].pct_change().dropna()
        stats['volatility_stats'] = {
            'daily_volatility': returns.std() * 100,  # 百分比
            'annual_volatility': returns.std() * np.sqrt(252) * 100,
            'max_drawdown': self._calculate_max_drawdown(data['close']),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
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
    
    def _generate_advice(self, analysis_result):
        """生成投资建议"""
        advice = {}
        
        basic_stats = analysis_result['basic_stats']
        technical = analysis_result['technical_indicators']
        trend = analysis_result['trend_analysis']
        risk = analysis_result['risk_assessment']
        
        # 技术面建议
        current_price = basic_stats['price_stats']['current_price']
        ma20 = technical['moving_averages']['ma20']
        rsi = technical['rsi']
        
        if current_price > ma20 and rsi < 70:
            advice['technical_signal'] = '买入信号'
        elif current_price < ma20 and rsi > 30:
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
        
        # 综合建议
        if (advice['technical_signal'] == '买入信号' and 
            advice['trend_signal'] == '趋势向上，建议关注' and
            advice['risk_signal'] == '风险较低，适合投资'):
            advice['overall_advice'] = '强烈推荐买入'
        elif (advice['technical_signal'] == '卖出信号' and 
              advice['trend_signal'] == '趋势向下，谨慎操作'):
            advice['overall_advice'] = '建议卖出'
        else:
            advice['overall_advice'] = '持有观望'
        
        return advice
    
    def print_analysis_report(self, analysis_result):
        """打印分析报告"""
        if analysis_result is None:
            print("❌ 分析结果为空")
            return
        
        print(f"\n📈 股票分析报告 - {analysis_result['symbol']}")
        print("=" * 60)
        print(f"分析时间: {analysis_result['analysis_date']}")
        print(f"数据期间: {analysis_result['data_period']}")
        print(f"总交易日: {analysis_result['total_days']}")
        
        # 基础统计
        print("\n📊 基础统计:")
        stats = analysis_result['basic_stats']['price_stats']
        print(f"   当前价格: {stats['current_price']:.2f}")
        print(f"   日涨跌: {stats['price_change_1d']:.2f} ({stats['price_change_1d_pct']:.2f}%)")
        print(f"   5日涨跌: {stats['price_change_5d']:.2f} ({stats['price_change_5d_pct']:.2f}%)")
        print(f"   52周最高: {stats['high_52w']:.2f}")
        print(f"   52周最低: {stats['low_52w']:.2f}")
        
        # 技术指标
        print("\n📈 技术指标:")
        tech = analysis_result['technical_indicators']
        print(f"   MA5: {tech['moving_averages']['ma5']:.2f}")
        print(f"   MA20: {tech['moving_averages']['ma20']:.2f}")
        print(f"   RSI: {tech['rsi']:.2f}")
        print(f"   MACD: {tech['macd']['macd']:.4f}")
        
        # 趋势分析
        print("\n📅 趋势分析:")
        trend = analysis_result['trend_analysis']
        print(f"   短期趋势: {trend['short_term']['direction']} (强度: {trend['short_term']['strength']:.2f}%)")
        print(f"   中期趋势: {trend['medium_term']['direction']} (强度: {trend['medium_term']['strength']:.2f}%)")
        print(f"   趋势一致性: {trend['consistency']}")
        
        # 风险评估
        print("\n⚠️  风险评估:")
        risk = analysis_result['risk_assessment']
        print(f"   波动率风险: {risk['volatility_risk']}")
        print(f"   回撤风险: {risk['drawdown_risk']}")
        print(f"   流动性风险: {risk['liquidity_risk']}")
        print(f"   总体风险: {risk['overall_risk']}")
        
        # 投资建议
        print("\n💡 投资建议:")
        advice = analysis_result['investment_advice']
        print(f"   技术信号: {advice['technical_signal']}")
        print(f"   趋势信号: {advice['trend_signal']}")
        print(f"   风险信号: {advice['risk_signal']}")
        print(f"   综合建议: {advice['overall_advice']}")
        
        print("=" * 60)


def main():
    """主函数 - 演示分析器功能"""
    print("A股个股分析器演示")
    print("=" * 50)
    
    # 创建分析器
    analyzer = IndividualAnalyzer()
    
    # 启动交互式分析
    analyzer.interactive_analysis()


if __name__ == "__main__":
    main()