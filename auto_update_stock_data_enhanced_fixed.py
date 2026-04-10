#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据自动更新工具 - 增强版（修复版）

支持按市场分类更新、智能重复检查、可控更新时间
将6393个股票数据分成深圳股市、上海股市、其他股市三部分
修复权限问题，使用项目目录存储token
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import json

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.china_stock_fetcher_tushare_fixed import ChinaStockFetcherTushareFixed


class EnhancedStockDataUpdaterFixed:
    """A股数据自动更新器 - 增强版（修复版）"""
    
    # 市场分类定义
    MARKET_CATEGORIES = {
        '深圳股市': ['.SZ'],
        '上海股市': ['.SH'],
        '其他股市': ['.BJ', '.NQ', '.OC']  # 北京交易所、新三板等
    }
    
    def __init__(self, data_file="e:/stockdata/stockdata.csv", config_file="e:/stockdata/update_config.json"):
        """
        初始化自动更新器 - 增强版（修复版）
        
        Args:
            data_file: 数据文件路径
            config_file: 更新配置文件路径
        """
        self.data_file = data_file
        self.config_file = config_file
        
        # 设置Tushare token文件路径到项目目录
        self._setup_tushare_token()
        
        self.fetcher = ChinaStockFetcherTushareFixed()
        
        # 加载配置
        self.config = self._load_config()
        
        # 加载现有数据
        self.existing_data = self._load_existing_data()
        
        print("数据文件:", data_file)
        print("配置文件:", config_file)
    
    def _setup_tushare_token(self):
        """设置Tushare token文件路径到项目目录"""
        # 在项目目录创建token文件
        project_token_file = os.path.join(os.path.dirname(__file__), 'tushare_token.csv')
        
        # 设置环境变量，让Tushare使用项目目录
        os.environ['TUSHARE_TOKEN_FILE'] = project_token_file
        
        # 如果token文件不存在，创建一个空的
        if not os.path.exists(project_token_file):
            try:
                with open(project_token_file, 'w', encoding='utf-8') as f:
                    f.write("token\n")
                    f.write("your_tushare_token_here\n")
                print("创建Tushare token文件:", project_token_file)
                print("提示: 请在此文件中填入您的Tushare token")
            except Exception as e:
                print("创建token文件失败:", e)
    
    def _load_config(self):
        """加载或创建配置文件"""
        default_config = {
            'last_update_date': None,
            'update_frequency': 'daily',
            'auto_update_enabled': True,
            'stock_codes': [],
            'initial_download_complete': False,
            'market_categories': {},
            'update_settings': {
                'delay_between_stocks': 2,
                'delay_between_batches': 10,
                'max_stocks_per_batch': 100
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print("成功加载配置文件")
                return {**default_config, **config}
            else:
                # 创建配置文件目录
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                
                # 保存默认配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                print("创建默认配置文件")
                return default_config
                
        except Exception as e:
            print("加载配置文件失败:", e)
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print("保存配置文件失败:", e)
            return False
    
    def _load_existing_data(self):
        """加载现有数据文件"""
        try:
            if not os.path.exists(self.data_file):
                print("数据文件不存在，将创建新文件")
                return None
            
            df = pd.read_csv(self.data_file)
            
            # 更新配置中的股票代码列表
            if not df.empty:
                self.config['stock_codes'] = df['ts_code'].unique().tolist()
                
                # 分析市场分类
                self._analyze_market_categories()
                
                # 更新最后更新日期
                if 'trade_date' in df.columns:
                    latest_date = df['trade_date'].max()
                    self.config['last_update_date'] = latest_date
                    self.config['initial_download_complete'] = True
            
            print("成功加载现有数据")
            print("   总记录数:", len(df), "条")
            print("   股票代码数量:", len(self.config['stock_codes']), "只")
            
            if self.config['last_update_date']:
                print("   最后更新日期:", self.config['last_update_date'])
            
            return df
            
        except Exception as e:
            print("加载数据文件失败:", e)
            return None
    
    def _analyze_market_categories(self):
        """分析股票代码的市场分类"""
        if not self.config['stock_codes']:
            return
        
        market_stats = {}
        
        for market_name, suffixes in self.MARKET_CATEGORIES.items():
            market_stocks = []
            for symbol in self.config['stock_codes']:
                for suffix in suffixes:
                    if symbol.endswith(suffix):
                        market_stocks.append(symbol)
                        break
            
            market_stats[market_name] = {
                'count': len(market_stocks),
                'stocks': market_stocks
            }
        
        self.config['market_categories'] = market_stats
        
        print("市场分类统计:")
        for market_name, stats in market_stats.items():
            print(f"   {market_name}: {stats['count']} 只股票")
    
    def get_market_stocks(self, market_name):
        """获取指定市场的股票代码列表"""
        if market_name not in self.config['market_categories']:
            return []
        
        return self.config['market_categories'][market_name]['stocks']
    
    def check_duplicate_data(self, symbol, date):
        """
        检查数据是否重复
        
        Args:
            symbol: 股票代码
            date: 交易日期
            
        Returns:
            bool: 是否已存在重复数据
        """
        if self.existing_data is None:
            return False
        
        # 检查是否已存在相同股票代码和日期的数据
        existing = self.existing_data[
            (self.existing_data['ts_code'] == symbol) & 
            (self.existing_data['trade_date'] == date)
        ]
        
        return len(existing) > 0
    
    def get_update_needed_info(self, market_name=None):
        """获取需要更新的信息"""
        today = datetime.now().strftime('%Y%m%d')
        
        if not self.config['last_update_date']:
            return {
                'update_needed': True,
                'reason': '首次下载',
                'from_date': '20250228',
                'to_date': today,
                'days_to_update': '全部'
            }
        
        last_update = self.config['last_update_date']
        
        # 如果是今天的数据，不需要更新
        if last_update == today:
            return {
                'update_needed': False,
                'reason': '数据已是最新',
                'last_update': last_update,
                'today': today
            }
        
        # 计算需要更新的天数
        last_date = datetime.strptime(last_update, '%Y%m%d')
        today_date = datetime.strptime(today, '%Y%m%d')
        
        # 计算工作日天数
        days_to_update = 0
        current_date = last_date + timedelta(days=1)  # 从下一天开始
        
        while current_date <= today_date:
            if current_date.weekday() < 5:  # 周一到周五
                days_to_update += 1
            current_date += timedelta(days=1)
        
        return {
            'update_needed': True,
            'reason': f'有 {days_to_update} 天数据需要更新',
            'from_date': last_update,
            'to_date': today,
            'days_to_update': days_to_update
        }
    
    def update_market_data(self, market_name, start_date="20250228", end_date=None, 
                          delay_between_stocks=2, max_stocks=None):
        """
        更新指定市场的数据
        
        Args:
            market_name: 市场名称
            start_date: 开始日期
            end_date: 结束日期
            delay_between_stocks: 股票间延迟(秒)
            max_stocks: 最大股票数量限制
            
        Returns:
            dict: 更新结果统计
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        market_stocks = self.get_market_stocks(market_name)
        
        if not market_stocks:
            print(f"错误: {market_name} 没有股票数据")
            return {'success': 0, 'failed': 0, 'duplicates': 0}
        
        # 应用股票数量限制
        if max_stocks and max_stocks < len(market_stocks):
            market_stocks = market_stocks[:max_stocks]
        
        print(f"开始更新 {market_name} 数据")
        print(f"   股票数量: {len(market_stocks)} 只")
        print(f"   时间范围: {start_date} 到 {end_date}")
        print(f"   延迟设置: {delay_between_stocks} 秒/股票")
        
        update_info = self.get_update_needed_info()
        
        if not update_info['update_needed']:
            print(f"   更新状态: {update_info['reason']}")
            return {'success': 0, 'failed': 0, 'duplicates': 0}
        
        all_updated_data = []
        success_count = 0
        failed_count = 0
        duplicate_count = 0
        
        for i, symbol in enumerate(market_stocks, 1):
            try:
                print(f"\n[{i}/{len(market_stocks)}] 更新 {symbol}...")
                
                # 从最后更新日期的下一天开始
                from_date = (datetime.strptime(update_info['from_date'], '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
                
                data = self.fetcher.get_a_stock_data(symbol, start_date=from_date, end_date=update_info['to_date'], use_cache=False)
                
                if data is not None and not data.empty:
                    # 转换为Tushare格式
                    converted_data = self._convert_to_tushare_format(data, symbol)
                    
                    # 检查并过滤重复数据
                    filtered_data = self._filter_duplicate_data(converted_data, symbol)
                    
                    if len(filtered_data) > 0:
                        all_updated_data.append(filtered_data)
                        success_count += 1
                        print(f"   成功: 新增 {len(filtered_data)} 条记录")
                        duplicate_count += (len(converted_data) - len(filtered_data))
                    else:
                        print("   跳过: 无新数据")
                        duplicate_count += len(converted_data)
                else:
                    print("   跳过: 无新数据")
                    failed_count += 1
                
                # 添加延迟
                time.sleep(delay_between_stocks)
                
            except Exception as e:
                print(f"   失败: {e}")
                failed_count += 1
        
        if all_updated_data:
            # 合并更新数据
            updated_data = pd.concat(all_updated_data, ignore_index=True)
            
            # 合并现有数据和更新数据
            if self.existing_data is not None:
                combined_data = pd.concat([self.existing_data, updated_data], ignore_index=True)
            else:
                combined_data = updated_data
            
            # 去重并排序
            combined_data = combined_data.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            combined_data = combined_data.sort_values(['ts_code', 'trade_date'])
            
            # 保存数据
            self._save_data(combined_data)
            
            # 更新配置
            self.config['last_update_date'] = update_info['to_date']
            self.save_config()
            
            print(f"\n{market_name} 更新完成!")
            print(f"   成功更新: {success_count} 只股票")
            print(f"   失败更新: {failed_count} 只股票")
            print(f"   跳过重复: {duplicate_count} 条记录")
            print(f"   新增记录: {len(updated_data)} 条")
            print(f"   最新日期: {update_info['to_date']}")
            
            return {
                'success': success_count,
                'failed': failed_count,
                'duplicates': duplicate_count,
                'new_records': len(updated_data)
            }
        else:
            print(f"\n{market_name} 无新数据需要更新")
            return {'success': 0, 'failed': failed_count, 'duplicates': duplicate_count, 'new_records': 0}
    
    def _filter_duplicate_data(self, data, symbol):
        """过滤重复数据"""
        if self.existing_data is None:
            return data
        
        filtered_data = []
        
        for _, row in data.iterrows():
            trade_date = row['trade_date']
            
            # 检查是否已存在相同数据
            if not self.check_duplicate_data(symbol, trade_date):
                filtered_data.append(row)
        
        return pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
    
    def _convert_to_tushare_format(self, data, symbol):
        """将获取的数据转换为Tushare格式"""
        # 重置索引，将日期作为列
        df = data.reset_index()
        
        # 重命名列以匹配Tushare格式
        column_mapping = {
            'Date': 'trade_date',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'vol'
        }
        
        # 只保留需要的列
        df = df.rename(columns=column_mapping)
        
        # 添加股票代码
        df['ts_code'] = symbol
        
        # 格式化日期
        df['trade_date'] = df['trade_date'].dt.strftime('%Y%m%d')
        
        # 添加其他必要字段
        df['pre_close'] = df['close'].shift(1)  # 前收盘价
        df['change'] = df['close'] - df['pre_close']  # 涨跌额
        df['pct_chg'] = (df['change'] / df['pre_close'] * 100).round(4)  # 涨跌幅
        df['amount'] = df['close'] * df['vol']  # 成交额
        
        # 添加下载时间
        df['download_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 处理第一行的NaN值
        df = df.fillna(0)
        
        return df
    
    def _save_data(self, data):
        """保存数据到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # 保存数据
            data.to_csv(self.data_file, index=False, encoding='utf-8-sig')
            
            # 更新现有数据引用
            self.existing_data = data
            
            print("数据已保存到:", self.data_file)
            print("   文件大小:", os.path.getsize(self.data_file) / 1024 / 1024, "MB")
            
            return True
            
        except Exception as e:
            print("数据保存失败:", e)
            return False
    
    def show_market_statistics(self):
        """显示市场统计信息"""
        print("\n市场分类统计:")
        print("=" * 40)
        
        total_stocks = 0
        for market_name, stats in self.config['market_categories'].items():
            count = stats['count']
            total_stocks += count
            print(f"{market_name}: {count} 只股票")
        
        print(f"\n总计: {total_stocks} 只股票")
        
        update_info = self.get_update_needed_info()
        print(f"\n更新状态: {update_info['reason']}")
        
        if update_info['update_needed']:
            print(f"需要更新: {update_info['days_to_update']} 天数据")


def main():
    """主函数"""
    print("A股数据自动更新工具 - 增强版（修复版）")
    print("=" * 50)
    
    # 配置参数
    DATA_FILE = "e:/stockdata/stockdata.csv"
    CONFIG_FILE = "e:/stockdata/update_config.json"
    
    # 创建自动更新器
    updater = EnhancedStockDataUpdaterFixed(data_file=DATA_FILE, config_file=CONFIG_FILE)
    
    while True:
        print("\n请选择操作:")
        print("1. 显示市场统计信息")
        print("2. 更新深圳股市数据")
        print("3. 更新上海股市数据")
        print("4. 更新其他股市数据")
        print("5. 更新所有市场数据")
        print("6. 自定义更新设置")
        print("7. 退出")
        
        choice = input("\n请输入选择 (1-7): ").strip()
        
        if choice == "1":
            # 显示市场统计信息
            updater.show_market_statistics()
        
        elif choice in ["2", "3", "4"]:
            # 更新单个市场数据
            market_mapping = {
                "2": "深圳股市",
                "3": "上海股市", 
                "4": "其他股市"
            }
            
            market_name = market_mapping[choice]
            
            # 获取更新设置
            delay = input(f"请输入{market_name}更新延迟(秒，默认2): ").strip()
            delay = int(delay) if delay.isdigit() else 2
            
            max_stocks = input(f"请输入最大股票数量(默认全部): ").strip()
            max_stocks = int(max_stocks) if max_stocks.isdigit() else None
            
            updater.update_market_data(market_name, delay_between_stocks=delay, max_stocks=max_stocks)
        
        elif choice == "5":
            # 更新所有市场数据
            print("开始更新所有市场数据")
            
            delay = input("请输入更新延迟(秒，默认2): ").strip()
            delay = int(delay) if delay.isdigit() else 2
            
            batch_delay = input("请输入市场间延迟(秒，默认10): ").strip()
            batch_delay = int(batch_delay) if batch_delay.isdigit() else 10
            
            total_results = {'success': 0, 'failed': 0, 'duplicates': 0, 'new_records': 0}
            
            for market_name in updater.MARKET_CATEGORIES.keys():
                print(f"\n{'='*50}")
                result = updater.update_market_data(market_name, delay_between_stocks=delay)
                
                # 累加结果
                for key in total_results:
                    total_results[key] += result.get(key, 0)
                
                # 市场间延迟
                if market_name != list(updater.MARKET_CATEGORIES.keys())[-1]:
                    print(f"等待 {batch_delay} 秒后继续下一个市场...")
                    time.sleep(batch_delay)
            
            print(f"\n所有市场更新完成!")
            print(f"   成功更新: {total_results['success']} 只股票")
            print(f"   失败更新: {total_results['failed']} 只股票")
            print(f"   跳过重复: {total_results['duplicates']} 条记录")
            print(f"   新增记录: {total_results['new_records']} 条")
        
        elif choice == "6":
            # 自定义更新设置
            print("自定义更新设置")
            print("-" * 20)
            
            market_name = input("请输入市场名称(深圳股市/上海股市/其他股市): ").strip()
            
            if market_name in updater.MARKET_CATEGORIES:
                start_date = input("请输入开始日期(默认20250228): ").strip() or "20250228"
                end_date = input("请输入结束日期(默认今日): ").strip()
                
                if not end_date:
                    end_date = datetime.now().strftime('%Y%m%d')
                
                delay = input("请输入更新延迟(秒，默认2): ").strip()
                delay = int(delay) if delay.isdigit() else 2
                
                max_stocks = input("请输入最大股票数量(默认全部): ").strip()
                max_stocks = int(max_stocks) if max_stocks.isdigit() else None
                
                updater.update_market_data(market_name, start_date, end_date, delay, max_stocks)
            else:
                print("错误: 无效的市场名称")
        
        elif choice == "7":
            print("\n感谢使用A股数据自动更新工具!")
            break
        
        else:
            print("错误: 无效选择，请重新输入")


if __name__ == "__main__":
    main()