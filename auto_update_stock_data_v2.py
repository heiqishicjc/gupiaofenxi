#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据自动更新工具 - 版本2.0

升级功能：
1. 按市场分类保存数据：深圳市场(stocksz.csv)、上海市场(stocksh.csv)、其他市场(stockother.csv)
2. 数据完整性检测：检测数据缺失并自动补充
3. 时间范围：20240101到当前日期
4. 智能更新：只更新缺失的数据
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


class AutoStockDataUpdaterV2:
    """A股数据自动更新器 - 版本2.0"""
    
    # 市场分类定义
    MARKET_CATEGORIES = {
        '深圳股市': {
            'suffix': '.SZ',
            'filename': 'stocksz.csv'
        },
        '上海股市': {
            'suffix': '.SH', 
            'filename': 'stocksh.csv'
        },
        '其他股市': {
            'suffix': ['.BJ', '.NQ', '.OC'],
            'filename': 'stockother.csv'
        }
    }
    
    def __init__(self, data_dir="e:/stockdata", config_file="e:/stockdata/update_config_v2.json"):
        """
        初始化自动更新器 - 版本2.0
        
        Args:
            data_dir: 数据目录路径
            config_file: 更新配置文件路径
        """
        self.data_dir = data_dir
        self.config_file = config_file
        
        # 使用您已有的有效 token
        valid_token = "46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"
        self.fetcher = ChinaStockFetcherTushareFixed(token=valid_token)
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
        # 加载各市场数据
        self.market_data = self._load_market_data()
        
        print("A股数据自动更新工具 - 版本2.0")
        print("=" * 50)
        print("数据目录:", data_dir)
        print("配置文件:", config_file)
    
    def _load_config(self):
        """加载或创建配置文件"""
        default_config = {
            'last_update_date': None,
            'start_date': '20240101',  # 固定起始日期
            'market_status': {},
            'stock_codes': [],
            'initial_download_complete': False
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print("成功加载配置文件")
                return {**default_config, **config}
            else:
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
    
    def _load_market_data(self):
        """加载各市场数据文件"""
        market_data = {}
        
        for market_name, market_info in self.MARKET_CATEGORIES.items():
            file_path = os.path.join(self.data_dir, market_info['filename'])
            
            try:
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    market_data[market_name] = df
                    
                    # 更新市场状态
                    if not df.empty:
                        self._update_market_status(market_name, df)
                    
                    print(f"成功加载 {market_name} 数据: {len(df)} 条记录")
                else:
                    market_data[market_name] = None
                    print(f"{market_name} 数据文件不存在，将创建新文件")
                    
            except Exception as e:
                print(f"加载 {market_name} 数据失败:", e)
                market_data[market_name] = None
        
        return market_data
    
    def _update_market_status(self, market_name, df):
        """更新市场状态信息"""
        if market_name not in self.config['market_status']:
            self.config['market_status'][market_name] = {}
        
        # 更新股票代码列表
        if 'ts_code' in df.columns:
            market_stocks = df['ts_code'].unique().tolist()
            self.config['market_status'][market_name]['stock_codes'] = market_stocks
            
            # 更新总股票代码列表
            if market_stocks:
                self.config['stock_codes'] = list(set(self.config['stock_codes'] + market_stocks))
        
        # 更新日期范围
        if 'trade_date' in df.columns and not df.empty:
            dates = df['trade_date'].unique()
            if len(dates) > 0:
                min_date = min(dates)
                max_date = max(dates)
                self.config['market_status'][market_name]['date_range'] = {
                    'min_date': min_date,
                    'max_date': max_date,
                    'total_days': len(dates)
                }
                
                # 更新最后更新日期
                if self.config['last_update_date'] is None or max_date > self.config['last_update_date']:
                    self.config['last_update_date'] = max_date
    
    def check_data_completeness(self, market_name):
        """
        检查数据完整性
        
        Args:
            market_name: 市场名称
            
        Returns:
            dict: 完整性检查结果
        """
        if market_name not in self.config['market_status']:
            return {
                'complete': False,
                'reason': '市场数据不存在',
                'missing_dates': [],
                'total_missing': 0
            }
        
        market_status = self.config['market_status'][market_name]
        
        if 'date_range' not in market_status:
            return {
                'complete': False,
                'reason': '日期范围信息缺失',
                'missing_dates': [],
                'total_missing': 0
            }
        
        date_range = market_status['date_range']
        current_max_date = date_range['max_date']
        
        # 检查是否需要更新到当前日期
        today = datetime.now().strftime('%Y%m%d')
        
        if current_max_date == today:
            return {
                'complete': True,
                'reason': '数据已是最新',
                'missing_dates': [],
                'total_missing': 0
            }
        
        # 计算缺失的日期
        missing_dates = self._calculate_missing_dates(current_max_date, today)
        
        return {
            'complete': len(missing_dates) == 0,
            'reason': f'有 {len(missing_dates)} 天数据需要更新' if missing_dates else '数据完整',
            'missing_dates': missing_dates,
            'total_missing': len(missing_dates)
        }
    
    def _calculate_missing_dates(self, start_date, end_date):
        """计算两个日期之间的缺失工作日"""
        try:
            # 确保日期是字符串类型
            start_date_str = str(start_date)
            end_date_str = str(end_date)
            
            start = datetime.strptime(start_date_str, '%Y%m%d')
            end = datetime.strptime(end_date_str, '%Y%m%d')
            
            # 从下一天开始计算
            current = start + timedelta(days=1)
            missing_dates = []
            
            while current <= end:
                if current.weekday() < 5:  # 周一到周五
                    missing_dates.append(current.strftime('%Y%m%d'))
                current += timedelta(days=1)
            
            return missing_dates
            
        except Exception as e:
            print(f"计算缺失日期失败:", e)
            return []
    
    def get_market_stocks(self, market_name):
        """获取指定市场的股票代码列表"""
        if market_name not in self.config['market_status']:
            return []
        
        return self.config['market_status'][market_name].get('stock_codes', [])
    
    def update_market_data(self, market_name, check_completeness=True):
        """
        更新指定市场的数据
        
        Args:
            market_name: 市场名称
            check_completeness: 是否检查数据完整性
            
        Returns:
            dict: 更新结果统计
        """
        print(f"\n开始更新 {market_name} 数据")
        print("-" * 40)
        
        # 检查数据完整性
        if check_completeness:
            completeness_info = self.check_data_completeness(market_name)
            print(f"数据完整性检查: {completeness_info['reason']}")
            
            if completeness_info['complete']:
                print(f"{market_name} 数据已完整，无需更新")
                return {'success': 0, 'failed': 0, 'updated': 0, 'reason': '数据已完整'}
        
        market_stocks = self.get_market_stocks(market_name)
        
        if not market_stocks:
            print(f"错误: {market_name} 没有股票数据")
            return {'success': 0, 'failed': 0, 'updated': 0, 'reason': '无股票数据'}
        
        # 获取需要更新的日期范围
        market_status = self.config['market_status'][market_name]
        date_range = market_status['date_range']
        
        start_date = date_range['max_date']  # 从最后更新日期开始
        end_date = datetime.now().strftime('%Y%m%d')
        
        print(f"股票数量: {len(market_stocks)} 只")
        print(f"更新范围: {start_date} 到 {end_date}")
        
        all_updated_data = []
        success_count = 0
        failed_count = 0
        total_updated = 0
        
        for i, symbol in enumerate(market_stocks, 1):
            try:
                print(f"[{i}/{len(market_stocks)}] 更新 {symbol}...")
                
                # 从最后更新日期的下一天开始
                from_date_str = str(start_date)
                from_date = (datetime.strptime(from_date_str, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
                
                data = self.fetcher.get_a_stock_data(symbol, start_date=from_date, end_date=end_date, use_cache=False)
                
                if data is not None and not data.empty:
                    # 转换为Tushare格式
                    converted_data = self._convert_to_tushare_format(data, symbol)
                    
                    # 检查并过滤重复数据
                    filtered_data = self._filter_duplicate_data(converted_data, symbol, market_name)
                    
                    if len(filtered_data) > 0:
                        all_updated_data.append(filtered_data)
                        success_count += 1
                        total_updated += len(filtered_data)
                        print(f"成功: 新增 {len(filtered_data)} 条记录")
                    else:
                        print("跳过: 无新数据")
                else:
                    print("跳过: 无新数据")
                    failed_count += 1
                
                # 添加延迟
                time.sleep(2)
                
            except Exception as e:
                print(f"失败: {e}")
                failed_count += 1
        
        if all_updated_data:
            # 合并更新数据
            updated_data = pd.concat(all_updated_data, ignore_index=True)
            
            # 合并现有数据和更新数据
            current_data = self.market_data[market_name]
            if current_data is not None:
                combined_data = pd.concat([current_data, updated_data], ignore_index=True)
            else:
                combined_data = updated_data
            
            # 去重并排序
            combined_data = combined_data.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            combined_data = combined_data.sort_values(['ts_code', 'trade_date'])
            
            # 保存数据
            file_path = os.path.join(self.data_dir, self.MARKET_CATEGORIES[market_name]['filename'])
            self._save_data(combined_data, file_path, market_name)
            
            # 更新配置
            self.config['last_update_date'] = end_date
            self.config['market_status'][market_name]['date_range']['max_date'] = end_date
            self.save_config()
            
            print(f"\n{market_name} 更新完成!")
            print(f"成功更新: {success_count} 只股票")
            print(f"失败更新: {failed_count} 只股票")
            print(f"新增记录: {total_updated} 条")
            print(f"最新日期: {end_date}")
            
            return {
                'success': success_count,
                'failed': failed_count,
                'updated': total_updated,
                'reason': '更新完成'
            }
        else:
            print(f"\n{market_name} 无新数据需要更新")
            return {'success': 0, 'failed': failed_count, 'updated': 0, 'reason': '无新数据'}
    
    def _filter_duplicate_data(self, data, symbol, market_name):
        """过滤重复数据"""
        current_data = self.market_data[market_name]
        
        if current_data is None:
            return data
        
        filtered_data = []
        
        for _, row in data.iterrows():
            trade_date = row['trade_date']
            
            # 检查是否已存在相同数据
            existing = current_data[
                (current_data['ts_code'] == symbol) & 
                (current_data['trade_date'] == trade_date)
            ]
            
            if len(existing) == 0:
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
    
    def _save_data(self, data, file_path, market_name):
        """保存数据到文件"""
        try:
            # 保存数据
            data.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            # 更新市场数据引用
            self.market_data[market_name] = data
            
            print("数据已保存到:", file_path)
            print("文件大小:", os.path.getsize(file_path) / 1024 / 1024, "MB")
            
            return True
            
        except Exception as e:
            print("数据保存失败:", e)
            return False
    
    def show_market_status(self):
        """显示各市场状态信息"""
        print("\n各市场数据状态:")
        print("=" * 60)
        
        for market_name in self.MARKET_CATEGORIES.keys():
            file_path = os.path.join(self.data_dir, self.MARKET_CATEGORIES[market_name]['filename'])
            
            if market_name in self.config['market_status']:
                market_status = self.config['market_status'][market_name]
                
                if 'date_range' in market_status:
                    date_range = market_status['date_range']
                    stock_count = len(market_status.get('stock_codes', []))
                    
                    print(f"{market_name}:")
                    print(f"   股票数量: {stock_count} 只")
                    print(f"   日期范围: {date_range['min_date']} 到 {date_range['max_date']}")
                    print(f"   总交易日: {date_range['total_days']} 天")
                    
                    # 检查完整性
                    completeness_info = self.check_data_completeness(market_name)
                    print(f"   完整性: {completeness_info['reason']}")
                else:
                    print(f"{market_name}: 数据文件存在但状态信息不完整")
            else:
                if os.path.exists(file_path):
                    print(f"{market_name}: 数据文件存在但未加载状态")
                else:
                    print(f"{market_name}: 数据文件不存在")
            
            print()
    
    def initial_download_all_markets(self):
        """初始下载所有市场数据"""
        print("开始初始下载所有市场数据")
        print("时间范围: 20240101 到", datetime.now().strftime('%Y%m%d'))
        
        total_results = {'success': 0, 'failed': 0, 'updated': 0}
        
        for market_name in self.MARKET_CATEGORIES.keys():
            print(f"\n{'='*50}")
            
            # 检查是否已有数据
            file_path = os.path.join(self.data_dir, self.MARKET_CATEGORIES[market_name]['filename'])
            
            if os.path.exists(file_path):
                confirm = input(f"{market_name} 数据文件已存在，确定要重新下载吗？(y/N): ").strip().lower()
                if confirm != 'y':
                    print(f"跳过 {market_name}")
                    continue
            
            # 执行初始下载
            result = self._initial_download_market(market_name)
            
            # 累加结果
            for key in total_results:
                total_results[key] += result.get(key, 0)
        
        print(f"\n所有市场初始下载完成!")
        print(f"成功下载: {total_results['success']} 只股票")
        print(f"失败下载: {total_results['failed']} 只股票")
        print(f"总记录数: {total_results['updated']} 条")
    
    def _initial_download_market(self, market_name):
        """初始下载指定市场数据"""
        print(f"开始下载 {market_name} 数据")
        
        # 获取该市场的所有股票代码（这里需要从API获取或使用预定义列表）
        # 为了简化，我们使用一个示例股票列表
        sample_stocks = self._get_sample_stocks_for_market(market_name)
        
        if not sample_stocks:
            print(f"错误: 无法获取 {market_name} 的股票列表")
            return {'success': 0, 'failed': 0, 'updated': 0}
        
        start_date = '20240101'
        end_date = datetime.now().strftime('%Y%m%d')
        
        print(f"股票数量: {len(sample_stocks)} 只")
        print(f"时间范围: {start_date} 到 {end_date}")
        
        all_data = []
        success_count = 0
        failed_count = 0
        total_records = 0
        
        for i, symbol in enumerate(sample_stocks, 1):
            try:
                print(f"[{i}/{len(sample_stocks)}] 下载 {symbol}...")
                
                data = self.fetcher.get_a_stock_data(symbol, start_date=start_date, end_date=end_date, use_cache=False)
                
                if data is not None and not data.empty:
                    # 转换为Tushare格式
                    converted_data = self._convert_to_tushare_format(data, symbol)
                    all_data.append(converted_data)
                    success_count += 1
                    total_records += len(data)
                    print(f"成功: 下载 {len(data)} 条记录")
                else:
                    print("失败: 无数据返回")
                    failed_count += 1
                
                # 添加延迟
                time.sleep(2)
                
            except Exception as e:
                print(f"失败: {e}")
                failed_count += 1
        
        if all_data:
            # 合并所有数据
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # 去重并排序
            combined_data = combined_data.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            combined_data = combined_data.sort_values(['ts_code', 'trade_date'])
            
            # 保存数据
            file_path = os.path.join(self.data_dir, self.MARKET_CATEGORIES[market_name]['filename'])
            self._save_data(combined_data, file_path, market_name)
            
            # 更新配置
            self.config['market_status'][market_name] = {
                'stock_codes': sample_stocks,
                'date_range': {
                    'min_date': start_date,
                    'max_date': end_date,
                    'total_days': len(combined_data['trade_date'].unique())
                }
            }
            
            self.config['last_update_date'] = end_date
            self.config['stock_codes'] = list(set(self.config['stock_codes'] + sample_stocks))
            self.save_config()
            
            print(f"\n{market_name} 初始下载完成!")
            print(f"成功下载: {success_count} 只股票")
            print(f"失败下载: {failed_count} 只股票")
            print(f"总记录数: {total_records} 条")
            
            return {
                'success': success_count,
                'failed': failed_count,
                'updated': total_records
            }
        else:
            print(f"\n{market_name} 下载失败")
            return {'success': 0, 'failed': failed_count, 'updated': 0}
    
    def _get_sample_stocks_for_market(self, market_name):
        """获取示例股票列表（简化实现）"""
        # 这里应该从API获取完整的股票列表
        # 为了演示，我们返回一些示例股票
        
        if market_name == '深圳股市':
            return ['000001.SZ', '000002.SZ', '000858.SZ', '002415.SZ', '300750.SZ']
        elif market_name == '上海股市':
            return ['600519.SH', '601398.SH', '601318.SH', '600036.SH', '600030.SH']
        elif market_name == '其他股市':
            return ['830946.BJ', '839680.BJ', '430090.OC']
        
        return []


def main():
    """主函数"""
    print("A股数据自动更新工具 - 版本2.0")
    print("=" * 50)
    
    # 配置参数
    DATA_DIR = "e:/stockdata"
    CONFIG_FILE = "e:/stockdata/update_config_v2.json"
    
    # 创建自动更新器
    updater = AutoStockDataUpdaterV2(data_dir=DATA_DIR, config_file=CONFIG_FILE)
    
    while True:
        print("\n请选择操作:")
        print("1. 显示各市场状态")
        print("2. 初始下载所有市场数据")
        print("3. 更新深圳股市数据")
        print("4. 更新上海股市数据")
        print("5. 更新其他股市数据")
        print("6. 更新所有市场数据")
        print("7. 退出")
        
        choice = input("\n请输入选择 (1-7): ").strip()
        
        if choice == "1":
            # 显示各市场状态
            updater.show_market_status()
        
        elif choice == "2":
            # 初始下载所有市场数据
            updater.initial_download_all_markets()
        
        elif choice in ["3", "4", "5"]:
            # 更新单个市场数据
            market_mapping = {
                "3": "深圳股市",
                "4": "上海股市", 
                "5": "其他股市"
            }
            
            market_name = market_mapping[choice]
            updater.update_market_data(market_name)
        
        elif choice == "6":
            # 更新所有市场数据
            print("开始更新所有市场数据")
            
            total_results = {'success': 0, 'failed': 0, 'updated': 0}
            
            for market_name in updater.MARKET_CATEGORIES.keys():
                print(f"\n{'='*50}")
                result = updater.update_market_data(market_name)
                
                # 累加结果
                for key in total_results:
                    total_results[key] += result.get(key, 0)
            
            print(f"\n所有市场更新完成!")
            print(f"成功更新: {total_results['success']} 只股票")
            print(f"失败更新: {total_results['failed']} 只股票")
            print(f"新增记录: {total_results['updated']} 条")
        
        elif choice == "7":
            print("\n感谢使用A股数据自动更新工具!")
            break
        
        else:
            print("错误: 无效选择，请重新输入")


if __name__ == "__main__":
    main()