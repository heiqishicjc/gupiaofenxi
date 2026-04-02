#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据批量下载工具

将A股数据下载到指定CSV文件中，支持自定义时间范围
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.china_stock_fetcher import ChinaStockFetcher


class StockDataDownloader:
    """A股数据批量下载器"""
    
    # 热门A股股票列表
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
        '海康威视': '002415.SZ',
        '中国中免': '601888.SH',
        '药明康德': '603259.SH',
        '恒瑞医药': '600276.SH',
        '美的集团': '000333.SZ',
        '格力电器': '000651.SZ',
        '伊利股份': '600887.SH',
        '海天味业': '603288.SH',
        '中国建筑': '601668.SH',
        '中国石油': '601857.SH',
        '中国石化': '600028.SH'
    }
    
    # 主要指数
    INDEXES = {
        '上证指数': '000001.SH',
        '深证成指': '399001.SZ',
        '创业板指': '399006.SZ',
        '沪深300': '000300.SH',
        '上证50': '000016.SH',
        '中证500': '000905.SH'
    }
    
    def __init__(self, output_dir="e:/stockdata"):
        """
        初始化数据下载器
        
        Args:
            output_dir: 数据输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建数据获取器
        self.fetcher = ChinaStockFetcher(prefer_tushare=True)
        
        print(f"📁 数据输出目录: {output_dir}")
    
    def download_single_stock(self, symbol, stock_name, start_date="20250228", end_date="20250801"):
        """
        下载单只股票数据
        
        Args:
            symbol: 股票代码
            stock_name: 股票名称
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            bool: 是否下载成功
        """
        try:
            print(f"📥 正在下载 {stock_name} ({symbol}) 数据...")
            
            # 使用Tushare格式下载数据
            data = self.fetcher.get_a_stock_data(symbol, start_date=start_date, end_date=end_date, use_cache=False)
            
            if data is None or data.empty:
                print(f"❌ 无法获取 {stock_name} 的数据")
                return False
            
            # 保存到CSV文件
            filename = f"{symbol}_{stock_name}_{start_date}_{end_date}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            data.to_csv(filepath, encoding='utf-8-sig')
            
            print(f"✅ {stock_name} 数据下载完成")
            print(f"   文件: {filename}")
            print(f"   数据量: {len(data)} 条记录")
            print(f"   时间范围: {data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}")
            
            return True
            
        except Exception as e:
            print(f"❌ {stock_name} 下载失败: {e}")
            return False
    
    def download_multiple_stocks(self, stock_list, start_date="20250228", end_date="20250801"):
        """
        批量下载多只股票数据
        
        Args:
            stock_list: 股票字典 {名称: 代码}
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            dict: 下载结果统计
        """
        print(f"🚀 开始批量下载 {len(stock_list)} 只股票数据")
        print(f"📅 时间范围: {start_date} 到 {end_date}")
        print(f"📁 保存目录: {self.output_dir}")
        print("=" * 60)
        
        results = {
            'total': len(stock_list),
            'success': 0,
            'failed': 0,
            'failed_list': []
        }
        
        for stock_name, symbol in stock_list.items():
            success = self.download_single_stock(symbol, stock_name, start_date, end_date)
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['failed_list'].append(stock_name)
            
            # 添加延迟避免请求过快
            time.sleep(1)
            print("-" * 40)
        
        return results
    
    def download_all_popular_stocks(self, start_date="20250228", end_date="20250801"):
        """下载所有热门股票数据"""
        return self.download_multiple_stocks(self.POPULAR_STOCKS, start_date, end_date)
    
    def download_indexes(self, start_date="20250228", end_date="20250801"):
        """下载指数数据"""
        return self.download_multiple_stocks(self.INDEXES, start_date, end_date)
    
    def create_combined_csv(self, start_date="20250228", end_date="20250801"):
        """
        创建合并的CSV文件，包含所有股票数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        print("🔄 正在创建合并的CSV文件...")
        
        combined_data = []
        
        for stock_name, symbol in self.POPULAR_STOCKS.items():
            try:
                # 下载数据
                data = self.fetcher.get_a_stock_data(symbol, start_date=start_date, end_date=end_date, use_cache=False)
                
                if data is not None and not data.empty:
                    # 添加股票标识列
                    data['StockCode'] = symbol
                    data['StockName'] = stock_name
                    
                    combined_data.append(data)
                    print(f"✅ 已添加 {stock_name} 数据")
                
            except Exception as e:
                print(f"❌ {stock_name} 数据添加失败: {e}")
            
            # 添加延迟
            time.sleep(0.5)
        
        if combined_data:
            # 合并所有数据
            final_data = pd.concat(combined_data)
            
            # 保存合并文件
            filename = f"stockdata_combined_{start_date}_{end_date}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            final_data.to_csv(filepath, encoding='utf-8-sig')
            
            print(f"\n🎉 合并文件创建完成!")
            print(f"📊 包含股票数量: {len(self.POPULAR_STOCKS)}")
            print(f"📈 总记录数: {len(final_data)}")
            print(f"💾 文件路径: {filepath}")
            
            return final_data
        else:
            print("❌ 没有可合并的数据")
            return None


def main():
    """主函数"""
    print("🚀 A股数据批量下载工具")
    print("=" * 50)
    
    # 配置参数
    OUTPUT_DIR = "e:/stockdata"
    START_DATE = "20250228"
    END_DATE = "20250801"
    
    # 创建下载器
    downloader = StockDataDownloader(output_dir=OUTPUT_DIR)
    
    while True:
        print("\n📋 请选择下载模式:")
        print("1. 下载所有热门股票数据")
        print("2. 下载指数数据")
        print("3. 创建合并的CSV文件")
        print("4. 下载单只股票数据")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            # 下载所有热门股票
            print(f"\n📥 开始下载热门股票数据 ({START_DATE} 到 {END_DATE})")
            results = downloader.download_all_popular_stocks(START_DATE, END_DATE)
            
            print(f"\n📊 下载结果统计:")
            print(f"   总计: {results['total']} 只股票")
            print(f"   成功: {results['success']} 只")
            print(f"   失败: {results['failed']} 只")
            
            if results['failed_list']:
                print(f"   失败列表: {', '.join(results['failed_list'])}")
        
        elif choice == "2":
            # 下载指数数据
            print(f"\n📈 开始下载指数数据 ({START_DATE} 到 {END_DATE})")
            results = downloader.download_indexes(START_DATE, END_DATE)
            
            print(f"\n📊 指数下载结果:")
            print(f"   成功: {results['success']} 个指数")
            print(f"   失败: {results['failed']} 个指数")
        
        elif choice == "3":
            # 创建合并文件
            print(f"\n🔄 开始创建合并CSV文件 ({START_DATE} 到 {END_DATE})")
            downloader.create_combined_csv(START_DATE, END_DATE)
        
        elif choice == "4":
            # 下载单只股票
            print("\n📋 热门股票列表:")
            for i, (name, code) in enumerate(downloader.POPULAR_STOCKS.items(), 1):
                print(f"   {i}. {name} ({code})")
            
            stock_choice = input("\n请输入股票编号或股票代码: ").strip()
            
            if stock_choice.isdigit() and 1 <= int(stock_choice) <= len(downloader.POPULAR_STOCKS):
                stock_list = list(downloader.POPULAR_STOCKS.items())
                stock_name, symbol = stock_list[int(stock_choice) - 1]
            else:
                # 直接输入股票代码
                symbol = stock_choice
                stock_name = "自定义股票"
                
                # 验证代码格式
                if not (symbol.endswith('.SH') or symbol.endswith('.SZ')):
                    print("❌ 请输入正确的股票代码格式 (如: 600519.SH)")
                    continue
            
            downloader.download_single_stock(symbol, stock_name, START_DATE, END_DATE)
        
        elif choice == "5":
            print("\n👋 感谢使用A股数据下载工具!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()