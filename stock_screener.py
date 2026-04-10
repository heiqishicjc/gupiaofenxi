#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票筛选器 v1.1.0 - 从5395只股票中筛选合格股票

功能特色：
1. 支持按市场筛选：深圳股市、上海股市、其他股市
2. 技术面筛选 (技术指标)
3. 基本面筛选 (价格、成交量等)
4. 趋势筛选 (短期、中期、长期趋势)
5. 风险筛选 (波动率、回撤等)
6. 自定义筛选条件

数据文件：
 - 深圳股市: E:/stockdata/stocksz.csv
 - 上海股市: E:/stockdata/stocksh.csv  
 - 其他股市: E:/stockdata/stockother.csv
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

from individual_analyzer import IndividualAnalyzer


class StockScreener:
    """A股股票筛选器 v1.1.0"""
    
    def __init__(self, data_dir="e:/stockdata"):
        """
        初始化股票筛选器
        
        Args:
            data_dir: 股票数据目录
        """
        self.data_dir = data_dir
        self.analyzer = IndividualAnalyzer(data_dir)
        self.selected_market = None  # 当前选中的市场
        self.market_stocks = {}  # 各市场的股票列表
        
        # 初始化各市场股票数据
        self._init_market_data()
        
        print("A股股票筛选器 v1.1.0 初始化完成")
        print(f"数据目录: {data_dir}")
        print("支持市场: 深圳股市、上海股市、其他股市")
    
    def _init_market_data(self):
        """初始化各市场股票数据"""
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
                    stocks = df['ts_code'].unique().tolist()
                    self.market_stocks[market_name] = stocks
                    print(f"成功加载 {market_name} 数据: {len(stocks)} 只股票")
                else:
                    print(f"警告: {market_name} 数据文件不存在: {file_path}")
                    self.market_stocks[market_name] = []
                    
            except Exception as e:
                print(f"加载 {market_name} 数据失败: {e}")
                self.market_stocks[market_name] = []
    
    def select_market(self, market_name):
        """
        选择要筛选的市场
        
        Args:
            market_name: 市场名称 ('深圳股市', '上海股市', '其他股市')
            
        Returns:
            bool: 选择是否成功
        """
        if market_name not in self.market_stocks:
            print(f"错误: 不支持的市场 '{market_name}'")
            return False
        
        if not self.market_stocks[market_name]:
            print(f"错误: {market_name} 没有可用的股票数据")
            return False
        
        self.selected_market = market_name
        print(f"已选择市场: {market_name}")
        print(f"股票数量: {len(self.market_stocks[market_name])} 只")
        return True
    
    def get_current_stocks(self):
        """获取当前选中的股票列表"""
        if self.selected_market is None:
            # 如果没有选择市场，返回所有股票
            all_stocks = []
            for stocks in self.market_stocks.values():
                all_stocks.extend(stocks)
            return all_stocks
        
        return self.market_stocks[self.selected_market]
    
    def show_market_statistics(self):
        """显示各市场统计信息"""
        print("\n各市场统计信息:")
        print("=" * 50)
        
        total_stocks = 0
        for market_name, stocks in self.market_stocks.items():
            stock_count = len(stocks)
            total_stocks += stock_count
            status = "当前选中" if market_name == self.selected_market else ""
            print(f"{market_name}: {stock_count} 只股票 {status}")
        
        print(f"\n总股票数量: {total_stocks} 只")
        
        if self.selected_market:
            print(f"当前筛选市场: {self.selected_market}")
        else:
            print("当前筛选范围: 全市场")
    
    def _get_all_stocks(self):
        """获取所有5395只股票代码"""
        try:
            # 从现有的stockdata.csv文件中获取所有股票代码
            df = pd.read_csv('e:/stockdata/stockdata.csv')
            all_stocks = df['ts_code'].unique().tolist()
            print(f"成功加载 {len(all_stocks)} 只股票代码")
            return all_stocks
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            # 返回示例股票列表作为备用
            return [
                '000001.SZ', '000002.SZ', '000858.SZ', '002415.SZ', '300750.SZ',
                '600519.SH', '601398.SH', '601318.SH', '600036.SH', '600030.SH'
            ]
    
    def screen_by_technical_indicators(self, stocks=None, max_results=50):
        """
        技术面筛选
        
        Args:
            stocks: 要筛选的股票列表 (None表示筛选当前选中的股票)
            max_results: 最大返回结果数
            
        Returns:
            list: 符合条件的股票列表
        """
        if stocks is None:
            stocks = self.get_current_stocks()
        
        print(f"\n开始技术面筛选 ({len(stocks)} 只股票)...")
        
        qualified_stocks = []
        
        for i, symbol in enumerate(stocks, 1):
            try:
                # 分析单只股票
                analysis_result = self.analyzer.analyze_single_stock(symbol)
                
                if analysis_result is None:
                    continue
                
                technical = analysis_result['technical_indicators']
                
                # 技术面筛选条件
                conditions = [
                    # RSI在30-70之间 (避免超买超卖)
                    (30 <= technical['rsi'] <= 70),
                    # 价格在MA20之上
                    (analysis_result['basic_stats']['price_stats']['current_price'] > 
                     technical['moving_averages']['ma20']),
                    # MACD金叉或接近金叉
                    (technical['macd']['macd'] > technical['macd']['signal'] - 0.01),
                    # 布林带宽度适中
                    (0.05 <= technical['bollinger_bands']['band_width'] <= 0.15)
                ]
                
                # 满足至少3个条件
                if sum(conditions) >= 3:
                    qualified_stocks.append({
                        'symbol': symbol,
                        'score': sum(conditions),
                        'current_price': analysis_result['basic_stats']['price_stats']['current_price'],
                        'rsi': technical['rsi'],
                        'ma20_ratio': (analysis_result['basic_stats']['price_stats']['current_price'] / 
                                     technical['moving_averages']['ma20'] - 1) * 100
                    })
                
                if i % 100 == 0:
                    print(f"  已处理 {i}/{len(stocks)} 只股票，当前合格: {len(qualified_stocks)} 只")
                
                # 继续处理所有股票，不限制数量
                    
            except Exception as e:
                # 跳过分析失败的股票
                continue
        
        # 按分数排序并返回前max_results只
        qualified_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ 技术面筛选完成: {len(qualified_stocks)} 只股票符合条件")
        return qualified_stocks[:max_results]
    
    def screen_by_trend(self, stocks=None, max_results=50):
        """
        趋势筛选
        
        Args:
            stocks: 要筛选的股票列表 (None表示筛选当前选中的股票)
            max_results: 最大返回结果数
            
        Returns:
            list: 符合条件的股票列表
        """
        if stocks is None:
            stocks = self.get_current_stocks()
        
        print(f"\n开始趋势筛选 ({len(stocks)} 只股票)...")
        
        qualified_stocks = []
        
        for i, symbol in enumerate(stocks, 1):
            try:
                analysis_result = self.analyzer.analyze_single_stock(symbol)
                
                if analysis_result is None:
                    continue
                
                trend = analysis_result['trend_analysis']
                
                # 趋势筛选条件
                conditions = [
                    # 短期趋势向上
                    (trend['short_term']['direction'] == '上涨'),
                    # 中期趋势向上
                    (trend['medium_term']['direction'] == '上涨'),
                    # 趋势一致性强
                    (trend['consistency'] == '强'),
                    # 短期趋势强度大于0.5%
                    (trend['short_term']['strength'] > 0.5)
                ]
                
                # 满足至少2个条件
                if sum(conditions) >= 2:
                    qualified_stocks.append({
                        'symbol': symbol,
                        'score': sum(conditions),
                        'short_trend': trend['short_term']['direction'],
                        'medium_trend': trend['medium_term']['direction'],
                        'trend_strength': trend['short_term']['strength'],
                        'consistency': trend['consistency']
                    })
                
                if i % 100 == 0:
                    print(f"  已处理 {i}/{len(stocks)} 只股票，当前合格: {len(qualified_stocks)} 只")
                
                if len(qualified_stocks) >= max_results * 2:
                    break
                    
            except Exception as e:
                continue
        
        qualified_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ 趋势筛选完成: {len(qualified_stocks)} 只股票符合条件")
        return qualified_stocks[:max_results]
    
    def screen_by_risk(self, stocks=None, max_results=50):
        """
        风险筛选 (筛选低风险股票)
        
        Args:
            stocks: 要筛选的股票列表 (None表示筛选当前选中的股票)
            max_results: 最大返回结果数
            
        Returns:
            list: 符合条件的股票列表
        """
        if stocks is None:
            stocks = self.get_current_stocks()
        
        print(f"\n开始风险筛选 ({len(stocks)} 只股票)...")
        
        qualified_stocks = []
        
        for i, symbol in enumerate(stocks, 1):
            try:
                analysis_result = self.analyzer.analyze_single_stock(symbol)
                
                if analysis_result is None:
                    continue
                
                risk = analysis_result['risk_assessment']
                basic_stats = analysis_result['basic_stats']
                
                # 风险筛选条件 (选择低风险股票)
                conditions = [
                    # 总体风险为低风险
                    (risk['overall_risk'] == '低风险'),
                    # 波动率风险为低
                    (risk['volatility_risk'] == '低'),
                    # 回撤风险为低
                    (risk['drawdown_risk'] == '低'),
                    # 日波动率小于3%
                    (basic_stats['volatility_stats']['daily_volatility'] < 3)
                ]
                
                # 满足至少3个条件
                if sum(conditions) >= 3:
                    qualified_stocks.append({
                        'symbol': symbol,
                        'score': sum(conditions),
                        'overall_risk': risk['overall_risk'],
                        'volatility': basic_stats['volatility_stats']['daily_volatility'],
                        'max_drawdown': basic_stats['volatility_stats']['max_drawdown'] * 100
                    })
                
                if i % 100 == 0:
                    print(f"  已处理 {i}/{len(stocks)} 只股票，当前合格: {len(qualified_stocks)} 只")
                
                if len(qualified_stocks) >= max_results * 2:
                    break
                    
            except Exception as e:
                continue
        
        qualified_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ 风险筛选完成: {len(qualified_stocks)} 只股票符合条件")
        return qualified_stocks[:max_results]
    
    def screen_by_custom_conditions(self, stocks=None, conditions_config=None, max_results=50):
        """
        自定义条件筛选
        
        Args:
            stocks: 要筛选的股票列表 (None表示筛选当前选中的股票)
            conditions_config: 自定义条件配置
            max_results: 最大返回结果数
            
        Returns:
            list: 符合条件的股票列表
        """
        if stocks is None:
            stocks = self.get_current_stocks()
        
        if conditions_config is None:
            # 默认自定义条件
            conditions_config = {
                'min_price': 5,           # 最低价格
                'max_price': 200,         # 最高价格
                'min_volume_ratio': 0.8,  # 成交量比率 (相对于平均)
                'max_rsi': 80,           # 最大RSI
                'min_rsi': 40            # 最小RSI
            }
        
        print(f"\n开始自定义条件筛选 ({len(stocks)} 只股票)...")
        
        qualified_stocks = []
        
        for i, symbol in enumerate(stocks, 1):
            try:
                analysis_result = self.analyzer.analyze_single_stock(symbol)
                
                if analysis_result is None:
                    continue
                
                basic_stats = analysis_result['basic_stats']
                technical = analysis_result['technical_indicators']
                
                current_price = basic_stats['price_stats']['current_price']
                avg_volume = basic_stats['price_stats']['avg_volume']
                recent_volume = analysis_result['basic_stats']['price_stats']['avg_volume']
                
                # 自定义筛选条件
                conditions = [
                    # 价格范围
                    (conditions_config['min_price'] <= current_price <= conditions_config['max_price']),
                    # 成交量活跃
                    (recent_volume >= avg_volume * conditions_config['min_volume_ratio']),
                    # RSI范围
                    (conditions_config['min_rsi'] <= technical['rsi'] <= conditions_config['max_rsi'])
                ]
                
                # 满足所有条件
                if all(conditions):
                    qualified_stocks.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'volume_ratio': recent_volume / avg_volume,
                        'rsi': technical['rsi']
                    })
                
                if i % 100 == 0:
                    print(f"  已处理 {i}/{len(stocks)} 只股票，当前合格: {len(qualified_stocks)} 只")
                
                if len(qualified_stocks) >= max_results * 2:
                    break
                    
            except Exception as e:
                continue
        
        print(f"✅ 自定义条件筛选完成: {len(qualified_stocks)} 只股票符合条件")
        return qualified_stocks[:max_results]
    
    def comprehensive_screening(self, screening_methods=None, max_results_per_method=20):
        """
        综合筛选 (多种筛选方法组合)
        
        Args:
            screening_methods: 筛选方法列表
            max_results_per_method: 每种方法的最大结果数
            
        Returns:
            dict: 各筛选方法的结果
        """
        if screening_methods is None:
            screening_methods = ['technical', 'trend', 'risk', 'custom']
        
        print(f"\n开始综合筛选 (方法: {', '.join(screening_methods)})")
        print("=" * 60)
        
        results = {}
        
        # 执行各种筛选方法
        if 'technical' in screening_methods:
            results['technical'] = self.screen_by_technical_indicators(max_results=max_results_per_method)
        
        if 'trend' in screening_methods:
            results['trend'] = self.screen_by_trend(max_results=max_results_per_method)
        
        if 'risk' in screening_methods:
            results['risk'] = self.screen_by_risk(max_results=max_results_per_method)
        
        if 'custom' in screening_methods:
            results['custom'] = self.screen_by_custom_conditions(max_results=max_results_per_method)
        
        # 计算综合评分
        all_stocks = {}
        for method, stocks in results.items():
            for stock in stocks:
                symbol = stock['symbol']
                if symbol not in all_stocks:
                    all_stocks[symbol] = {'symbol': symbol, 'methods': [], 'score': 0}
                
                all_stocks[symbol]['methods'].append(method)
                all_stocks[symbol]['score'] += 1
        
        # 按综合评分排序
        comprehensive_results = sorted(all_stocks.values(), key=lambda x: x['score'], reverse=True)
        
        print(f"\n综合筛选结果统计:")
        print("-" * 40)
        for method, stocks in results.items():
            print(f"{method.upper()}筛选: {len(stocks)} 只股票")
        
        print(f"综合合格: {len(comprehensive_results)} 只股票")
        
        return {
            'methods': results,
            'comprehensive': comprehensive_results[:max_results_per_method]
        }
    
    def print_screening_results(self, results, method_name):
        """打印筛选结果"""
        print(f"\n{method_name.upper()}筛选结果:")
        print("=" * 60)
        
        if not results:
            print("没有符合条件的股票")
            return
        
        for i, stock in enumerate(results, 1):
            print(f"{i:2d}. {stock['symbol']}", end="")
            
            # 根据不同的筛选方法显示不同的信息
            if 'current_price' in stock:
                print(f" | 价格: {stock['current_price']:.2f}", end="")
            
            if 'rsi' in stock:
                print(f" | RSI: {stock['rsi']:.1f}", end="")
            
            if 'score' in stock:
                print(f" | 评分: {stock['score']}/4", end="")
            
            if 'trend_strength' in stock:
                print(f" | 趋势强度: {stock['trend_strength']:.2f}%", end="")
            
            if 'volatility' in stock:
                print(f" | 波动率: {stock['volatility']:.2f}%", end="")
            
            print()
    
    def export_results(self, results, filename="screening_results.csv"):
        """导出筛选结果到CSV文件"""
        try:
            # 准备数据
            export_data = []
            
            for method, stocks in results['methods'].items():
                for stock in stocks:
                    export_data.append({
                        'symbol': stock['symbol'],
                        'screening_method': method,
                        'current_price': stock.get('current_price', 0),
                        'rsi': stock.get('rsi', 0),
                        'score': stock.get('score', 0)
                    })
            
            # 创建DataFrame并保存
            df = pd.DataFrame(export_data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            print(f"\n筛选结果已导出到: {filename}")
            print(f"   总记录数: {len(export_data)} 条")
            
            return True
            
        except Exception as e:
            print(f"导出失败: {e}")
            return False


def main():
    """主函数 - 演示筛选器功能"""
    print("A股股票筛选器 v1.1.0 演示")
    print("=" * 50)
    
    # 创建筛选器
    screener = StockScreener()
    
    # 市场选择菜单
    while True:
        print("\n请选择要筛选的市场:")
        print("1. 深圳股市")
        print("2. 上海股市") 
        print("3. 其他股市")
        print("4. 全市场")
        print("5. 查看市场统计")
        print("6. 开始筛选")
        print("7. 退出")
        
        choice = input("\n请输入选择 (1-7): ").strip()
        
        if choice == "1":
            screener.select_market("深圳股市")
        elif choice == "2":
            screener.select_market("上海股市")
        elif choice == "3":
            screener.select_market("其他股市")
        elif choice == "4":
            screener.selected_market = None
            print("已选择全市场筛选")
        elif choice == "5":
            screener.show_market_statistics()
        elif choice == "6":
            break
        elif choice == "7":
            print("\n感谢使用A股股票筛选器!")
            return
        else:
            print("错误: 无效选择，请重新输入")
    
    # 筛选菜单
    while True:
        print("\n请选择筛选方式:")
        print("1. 技术面筛选")
        print("2. 趋势筛选")
        print("3. 风险筛选")
        print("4. 自定义条件筛选")
        print("5. 综合筛选")
        print("6. 返回市场选择")
        print("7. 退出")
        
        choice = input("\n请输入选择 (1-7): ").strip()
        
        if choice == "1":
            # 技术面筛选
            print("\n请选择显示数量:")
            print("1. 显示20个股票")
            print("2. 显示50个股票")
            print("3. 显示所有符合条件的股票")
            
            display_choice = input("请输入选择 (1-3): ").strip()
            
            if display_choice == "1":
                max_results = 20
            elif display_choice == "2":
                max_results = 50
            elif display_choice == "3":
                max_results = 1000  # 显示所有股票
            else:
                print("使用默认显示20个股票")
                max_results = 20
            
            results = screener.screen_by_technical_indicators(max_results=max_results)
            screener.print_screening_results(results, "技术面")
        
        elif choice == "2":
            # 趋势筛选
            results = screener.screen_by_trend(max_results=20)
            screener.print_screening_results(results, "趋势")
        
        elif choice == "3":
            # 风险筛选
            results = screener.screen_by_risk(max_results=20)
            screener.print_screening_results(results, "风险")
        
        elif choice == "4":
            # 自定义条件筛选
            results = screener.screen_by_custom_conditions(max_results=20)
            screener.print_screening_results(results, "自定义条件")
        
        elif choice == "5":
            # 综合筛选
            results = screener.comprehensive_screening()
            
            # 打印各方法结果
            for method_name, method_results in results['methods'].items():
                screener.print_screening_results(method_results, method_name)
            
            # 打印综合结果
            print("\n综合推荐股票:")
            print("=" * 60)
            for i, stock in enumerate(results['comprehensive'], 1):
                print(f"{i:2d}. {stock['symbol']} | 符合方法: {', '.join(stock['methods'])} | 综合评分: {stock['score']}")
            
            # 导出结果
            export_choice = input("\n是否导出筛选结果到CSV文件？(y/N): ").strip().lower()
            if export_choice == 'y':
                screener.export_results(results)
        
        elif choice == "6":
            # 返回市场选择
            print("\n返回市场选择菜单...")
            break
        
        elif choice == "7":
            print("\n感谢使用A股股票筛选器!")
            return
        
        else:
            print("错误: 无效选择，请重新输入")
    
    # 递归调用主函数，实现菜单循环
    main()


if __name__ == "__main__":
    main()