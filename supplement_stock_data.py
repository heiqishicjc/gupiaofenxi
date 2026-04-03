#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据补充工具

为现有的stockdata.csv文件补充指定时间范围的数据
基于第一列股票代码进行数据补充
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.china_stock_fetcher_tushare_fixed import ChinaStockFetcherTushareFixed


class StockDataSupplement:
    """A股数据补充工具"""
    
    def __init__(self, data_file="e:/stockdata/stockdata.csv"):
        """
        初始化数据补充器
        
        Args:
            data_file: 现有数据文件路径
        """
        self.data_file = data_file
        self.fetcher = ChinaStockFetcherTushareFixed()
        
        # 加载现有数据
        self.existing_data = self._load_existing_data()
        
        print(f"📁 数据文件: {data_file}")
    
    def _load_existing_data(self):
        """加载现有数据文件"""
        try:
            if not os.path.exists(self.data_file):
                print(f"❌ 数据文件不存在: {self.data_file}")
                return None
            
            df = pd.read_csv(self.data_file)
            print(f"✅ 成功加载现有数据")
            print(f"   总记录数: {len(df)} 条")
            print(f"   股票代码数量: {df['ts_code'].nunique()} 只")
            print(f"   股票代码列表: {df['ts_code'].unique().tolist()}")
            print(f"   时间范围: {df['trade_date'].min()} 到 {df['trade_date'].max()}")
            
            return df
            
        except Exception as e:
            print(f"❌ 加载数据文件失败: {e}")
            return None
    
    def get_existing_stock_codes(self):
        """获取现有数据中的股票代码列表"""
        if self.existing_data is None:
            return []
        
        return self.existing_data['ts_code'].unique().tolist()
    
    def get_stock_data_gaps(self, symbol, start_date="20250228", end_date="20250801"):
        """
        分析股票数据缺失情况
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            dict: 缺失数据信息
        """
        if self.existing_data is None:
            return {'symbol': symbol, 'missing_dates': [], 'status': 'no_existing_data'}
        
        # 获取该股票的现有数据
        stock_data = self.existing_data[self.existing_data['ts_code'] == symbol]
        
        if stock_data.empty:
            return {'symbol': symbol, 'missing_dates': [], 'status': 'no_data_for_symbol'}
        
        # 获取现有数据的日期范围
        existing_dates = set(stock_data['trade_date'].astype(str).tolist())
        
        # 生成目标日期范围
        target_start = datetime.strptime(start_date, '%Y%m%d')
        target_end = datetime.strptime(end_date, '%Y%m%d')
        
        target_dates = set()
        current_date = target_start
        while current_date <= target_end:
            # 只包括工作日（周一至周五）
            if current_date.weekday() < 5:
                target_dates.add(current_date.strftime('%Y%m%d'))
            current_date += timedelta(days=1)
        
        # 找出缺失的日期
        missing_dates = sorted(list(target_dates - existing_dates))
        
        return {
            'symbol': symbol,
            'existing_dates_count': len(existing_dates),
            'target_dates_count': len(target_dates),
            'missing_dates_count': len(missing_dates),
            'missing_dates': missing_dates,
            'status': 'has_gaps' if missing_dates else 'complete'
        }
    
    def supplement_stock_data(self, symbol, start_date="20250228", end_date="20250801"):
        """
        为指定股票补充数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            tuple: (是否成功, 补充的数据量, 错误信息)
        """
        try:
            print(f"\n📥 正在为 {symbol} 补充数据...")
            
            # 获取缺失数据信息
            gap_info = self.get_stock_data_gaps(symbol, start_date, end_date)
            
            if gap_info['status'] == 'complete':
                print(f"✅ {symbol} 数据已完整，无需补充")
                return True, 0, "数据已完整"
            
            if gap_info['status'] == 'no_data_for_symbol':
                print(f"⚠️ {symbol} 在现有文件中没有数据，将下载完整数据")
                # 下载完整数据
                data = self.fetcher.get_a_stock_data(symbol, start_date=start_date, end_date=end_date, use_cache=False)
            else:
                # 只下载缺失的数据
                missing_start = gap_info['missing_dates'][0]
                missing_end = gap_info['missing_dates'][-1]
                print(f"   需要补充 {len(gap_info['missing_dates'])} 天的数据")
                print(f"   时间范围: {missing_start} 到 {missing_end}")
                
                data = self.fetcher.get_a_stock_data(symbol, start_date=missing_start, end_date=missing_end, use_cache=False)
            
            if data is None or data.empty:
                print(f"❌ 无法获取 {symbol} 的数据")
                return False, 0, "数据获取失败"
            
            # 转换数据格式以匹配现有文件
            supplemented_data = self._convert_to_tushare_format(data, symbol)
            
            print(f"✅ {symbol} 数据补充成功")
            print(f"   补充记录数: {len(supplemented_data)} 条")
            
            return True, len(supplemented_data), supplemented_data
            
        except Exception as e:
            print(f"❌ {symbol} 数据补充失败: {e}")
            return False, 0, str(e)
    
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
        
        # 添加其他必要字段（使用默认值）
        df['pre_close'] = df['close'].shift(1)  # 前收盘价
        df['change'] = df['close'] - df['pre_close']  # 涨跌额
        df['pct_chg'] = (df['change'] / df['pre_close'] * 100).round(4)  # 涨跌幅
        df['amount'] = df['close'] * df['vol']  # 成交额
        
        # 添加下载时间
        df['download_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 处理第一行的NaN值
        df = df.fillna(0)
        
        return df
    
    def save_supplemented_data(self, supplemented_data_list):
        """
        保存补充后的数据
        
        Args:
            supplemented_data_list: 补充的数据列表
            
        Returns:
            bool: 是否保存成功
        """
        try:
            if not supplemented_data_list:
                print("❌ 没有需要保存的数据")
                return False
            
            # 合并所有补充的数据
            all_supplemented = pd.concat(supplemented_data_list, ignore_index=True)
            
            # 合并现有数据和补充数据
            combined_data = pd.concat([self.existing_data, all_supplemented], ignore_index=True)
            
            # 按股票代码和交易日期排序
            combined_data = combined_data.sort_values(['ts_code', 'trade_date'])
            
            # 去重（保留最后出现的记录）
            combined_data = combined_data.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
            
            # 保存到文件
            combined_data.to_csv(self.data_file, index=False, encoding='utf-8-sig')
            
            print(f"\n🎉 数据保存完成!")
            print("=" * 50)
            print(f"📊 保存统计:")
            print(f"   原有记录数: {len(self.existing_data)} 条")
            print(f"   补充记录数: {len(all_supplemented)} 条")
            print(f"   合并后记录数: {len(combined_data)} 条")
            print(f"   文件大小: {os.path.getsize(self.data_file) / 1024 / 1024:.2f} MB")
            print(f"💾 文件路径: {self.data_file}")
            
            # 显示数据预览
            print(f"\n📈 数据预览:")
            print(combined_data[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']].tail(10))
            
            return True
            
        except Exception as e:
            print(f"❌ 数据保存失败: {e}")
            return False


def get_stock_range_selection(stock_codes):
    """
    获取股票代码范围选择
    
    Args:
        stock_codes: 股票代码列表
        
    Returns:
        list: 选中的股票代码列表
    """
    total_stocks = len(stock_codes)
    
    print("\n股票代码统计:")
    print(f"   总股票数量: {total_stocks} 只")
    print(f"   股票代码范围: 1-{total_stocks}")
    
    while True:
        print("\n请选择股票代码范围:")
        print("1. 选择范围 (如: 1-2000)")
        print("2. 选择单个股票 (如: 600519.SH)")
        print("3. 返回主菜单")
        
        range_choice = input("\n请输入选择 (1-3): ").strip()
        
        if range_choice == "1":
            # 选择范围
            while True:
                range_input = input("请输入股票代码范围 (格式: 开始-结束, 如 1-2000): ").strip()
                
                if '-' in range_input:
                    try:
                        start_str, end_str = range_input.split('-')
                        start_idx = int(start_str.strip()) - 1  # 转换为0-based索引
                        end_idx = int(end_str.strip()) - 1
                        
                        # 验证范围有效性
                        if start_idx < 0 or end_idx >= total_stocks or start_idx > end_idx:
                            print(f"错误: 范围无效，请输入 1-{total_stocks} 之间的有效范围")
                            continue
                        
                        selected_codes = stock_codes[start_idx:end_idx+1]
                        
                        print(f"成功: 已选择范围: {start_idx+1}-{end_idx+1}")
                        print(f"   选中股票数量: {len(selected_codes)} 只")
                        print(f"   示例股票: {selected_codes[:3]}..." if len(selected_codes) > 3 else f"   选中股票: {selected_codes}")
                        
                        confirm = input("确认选择？(y/N): ").strip().lower()
                        if confirm == 'y':
                            return selected_codes
                        else:
                            break
                            
                    except ValueError:
                        print("错误: 输入格式错误，请使用 '开始-结束' 格式")
                else:
                    print("错误: 请输入有效的范围格式")
        
        elif range_choice == "2":
            # 选择单个股票
            while True:
                symbol = input("请输入股票代码: ").strip()
                
                if symbol in stock_codes:
                    print(f"成功: 已选择股票: {symbol}")
                    return [symbol]
                else:
                    print(f"错误: 股票代码 {symbol} 不在现有文件中")
                    print(f"   现有股票代码示例: {stock_codes[:3]}...")
                    
                    retry = input("是否重新输入？(y/N): ").strip().lower()
                    if retry != 'y':
                        break
        
        elif range_choice == "3":
            return None
        
        else:
            print("错误: 无效选择，请重新输入")


def main():
    """主函数"""
    print("A股数据补充工具")
    print("=" * 50)
    
    # 配置参数
    DATA_FILE = "e:/stockdata/stockdata.csv"
    START_DATE = "20250228"  # 2025-02-28
    END_DATE = "20250801"    # 2025-08-01
    
    # 创建数据补充器
    supplementer = StockDataSupplement(data_file=DATA_FILE)
    
    if supplementer.existing_data is None:
        print("错误: 无法加载现有数据文件，请检查文件路径")
        return
    
    # 获取现有股票代码
    stock_codes = supplementer.get_existing_stock_codes()
    
    if not stock_codes:
        print("错误: 现有文件中没有股票数据")
        return
    
    print(f"\n现有股票代码数量: {len(stock_codes)} 只")
    
    while True:
        print("\n请选择操作:")
        print("1. 分析数据缺失情况")
        print("2. 补充所有股票数据")
        print("3. 补充指定股票数据")
        print("4. 补充股票代码范围数据")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            # 分析数据缺失情况
            print(f"\n分析数据缺失情况 ({START_DATE} 到 {END_DATE})")
            print("-" * 40)
            
            for symbol in stock_codes:
                gap_info = supplementer.get_stock_data_gaps(symbol, START_DATE, END_DATE)
                
                status_icons = {
                    'complete': '[完成]',
                    'has_gaps': '[缺失]',
                    'no_data_for_symbol': '[无数据]'
                }
                
                icon = status_icons.get(gap_info['status'], '[未知]')
                
                print(f"{icon} {symbol}:")
                print(f"   现有数据: {gap_info['existing_dates_count']} 天")
                print(f"   目标数据: {gap_info['target_dates_count']} 天")
                print(f"   缺失数据: {gap_info['missing_dates_count']} 天")
                
                if gap_info['missing_dates']:
                    print(f"   缺失日期: {gap_info['missing_dates'][:3]}..." if len(gap_info['missing_dates']) > 3 else f"   缺失日期: {gap_info['missing_dates']}")
                
                print()
        
        elif choice == "2":
            # 补充所有股票数据
            print(f"\n开始补充所有股票数据 ({START_DATE} 到 {END_DATE})")
            
            supplemented_data_list = []
            total_supplemented = 0
            
            for symbol in stock_codes:
                success, count, data = supplementer.supplement_stock_data(symbol, START_DATE, END_DATE)
                
                if success and count > 0:
                    supplemented_data_list.append(data)
                    total_supplemented += count
                
                # 添加延迟避免请求过快
                time.sleep(2)
            
            if supplemented_data_list:
                # 保存补充的数据
                supplementer.save_supplemented_data(supplemented_data_list)
            else:
                print("成功: 所有股票数据已完整，无需补充")
        
        elif choice == "3":
            # 补充指定股票数据
            print(f"\n补充指定股票数据")
            
            symbol = input("请输入股票代码: ").strip()
            
            if symbol in stock_codes:
                success, count, data = supplementer.supplement_stock_data(symbol, START_DATE, END_DATE)
                
                if success and count > 0:
                    supplementer.save_supplemented_data([data])
            else:
                print(f"错误: 股票代码 {symbol} 不在现有文件中")
        
        elif choice == "4":
            # 补充股票代码范围数据
            print(f"\n补充股票代码范围数据 ({START_DATE} 到 {END_DATE})")
            
            # 获取股票代码范围选择
            selected_codes = get_stock_range_selection(stock_codes)
            
            if selected_codes is None:
                print("错误: 未选择任何股票")
                continue
            
            print(f"\n开始补充选中的 {len(selected_codes)} 只股票数据")
            
            supplemented_data_list = []
            total_supplemented = 0
            success_count = 0
            
            for i, symbol in enumerate(selected_codes, 1):
                print(f"\n[{i}/{len(selected_codes)}] 正在补充 {symbol}...")
                
                success, count, data = supplementer.supplement_stock_data(symbol, START_DATE, END_DATE)
                
                if success:
                    if count > 0:
                        supplemented_data_list.append(data)
                        total_supplemented += count
                        success_count += 1
                        print(f"成功: {symbol} 补充成功 ({count} 条记录)")
                    else:
                        print(f"成功: {symbol} 数据已完整，无需补充")
                else:
                    print(f"错误: {symbol} 补充失败")
                
                # 添加延迟避免请求过快
                time.sleep(2)
            
            if supplemented_data_list:
                # 保存补充的数据
                supplementer.save_supplemented_data(supplemented_data_list)
                
                print(f"\n范围补充结果统计:")
                print(f"   选中股票: {len(selected_codes)} 只")
                print(f"   成功补充: {success_count} 只")
                print(f"   失败补充: {len(selected_codes) - success_count} 只")
                print(f"   新增记录: {total_supplemented} 条")
            else:
                print("成功: 选中股票数据已完整，无需补充")
        
        elif choice == "5":
            print("\n感谢使用A股数据补充工具!")
            break
        
        else:
            print("错误: 无效选择，请重新输入")


if __name__ == "__main__":
    main()