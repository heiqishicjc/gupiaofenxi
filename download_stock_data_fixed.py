#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据批量下载工具 - 修复版

修复权限问题，直接使用Tushare获取数据，避免缓存文件创建
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.china_stock_fetcher_tushare_fixed import ChinaStockFetcherTushareFixed


class StockDataDownloaderFixed:
    """A股数据批量下载器 - 修复版"""
    
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
        '海康威视': '002415.SZ'
    }
    
    def __init__(self, output_dir="e:/stockdata"):
        """
        初始化数据下载器 - 修复版
        
        Args:
            output_dir: 数据输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建修复版数据获取器
        self.fetcher = ChinaStockFetcherTushareFixed()
        
        print(f"📁 数据输出目录: {output_dir}")
    
    def download_single_stock(self, symbol, stock_name, start_date="20250228", end_date="20250801"):
        """
        下载单只股票数据 - 修复版
        
        Args:
            symbol: 股票代码
            stock_name: 股票名称
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            bool: 是否下载成功
        """
        try:
            print(f"📥 正在下载 {stock_name} ({symbol})...")
            
            # 直接使用修复版获取数据（不使用缓存）
            data = self.fetcher.get_a_stock_data(symbol, start_date=start_date, end_date=end_date, use_cache=False)
            
            if data is None or data.empty:
                print(f"❌ 无法获取 {stock_name} 的数据")
                return False
            
            # 保存到CSV文件
            filename = f"{symbol}_{stock_name}_{start_date}_{end_date}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            # 添加日期列便于分析
            data['TradeDate'] = data.index.strftime('%Y-%m-%d')
            
            # 保存数据（不包含索引）
            data.to_csv(filepath, encoding='utf-8-sig', index=False)
            
            print(f"✅ {stock_name} 下载成功")
            print(f"   文件: {filename}")
            print(f"   记录数: {len(data)} 条")
            print(f"   时间范围: {data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"   最新收盘价: {data['Close'].iloc[-1]:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ {stock_name} 下载失败: {e}")
            return False
    
    def download_all_stocks(self, start_date="20250228", end_date="20250801"):
        """
        下载所有热门股票数据 - 修复版
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            dict: 下载结果统计
        """
        print(f"🚀 开始批量下载 {len(self.POPULAR_STOCKS)} 只热门A股数据")
        print(f"📅 时间范围: {start_date} 到 {end_date}")
        print(f"📁 保存目录: {self.output_dir}")
        print("=" * 60)
        
        results = {
            'total': len(self.POPULAR_STOCKS),
            'success': 0,
            'failed': 0,
            'failed_list': []
        }
        
        for stock_name, symbol in self.POPULAR_STOCKS.items():
            success = self.download_single_stock(symbol, stock_name, start_date, end_date)
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['failed_list'].append(stock_name)
            
            # 添加延迟避免请求过快
            time.sleep(2)
            print("-" * 40)
        
        return results
    
    def create_combined_file(self, start_date="20250228", end_date="20250801"):
        """
        创建合并的CSV文件 - 修复版
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        print("🔄 正在创建合并的CSV文件...")
        
        combined_data = []
        success_count = 0
        
        for stock_name, symbol in self.POPULAR_STOCKS.items():
            try:
                print(f"📥 获取 {stock_name} 数据...")
                
                # 获取数据
                data = self.fetcher.get_a_stock_data(symbol, start_date=start_date, end_date=end_date, use_cache=False)
                
                if data is not None and not data.empty:
                    # 添加股票标识信息
                    data['StockCode'] = symbol
                    data['StockName'] = stock_name
                    data['Market'] = 'SH' if symbol.endswith('.SH') else 'SZ'
                    data['TradeDate'] = data.index.strftime('%Y-%m-%d')
                    
                    combined_data.append(data)
                    success_count += 1
                    print(f"✅ {stock_name} 数据获取成功")
                else:
                    print(f"❌ {stock_name} 数据获取失败")
                
                # 添加延迟
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {stock_name} 数据获取失败: {e}")
        
        if combined_data:
            # 合并所有数据
            final_data = pd.concat(combined_data)
            
            # 按日期和股票代码排序
            final_data = final_data.sort_values(['TradeDate', 'StockCode'])
            
            # 保存合并文件
            filename = f"stockdata_combined_{start_date}_{end_date}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            final_data.to_csv(filepath, encoding='utf-8-sig', index=False)
            
            print(f"\n🎉 合并文件创建完成!")
            print("=" * 50)
            print(f"📊 合并统计:")
            print(f"   成功合并: {success_count} 只股票")
            print(f"   失败合并: {len(self.POPULAR_STOCKS) - success_count} 只股票")
            print(f"   总记录数: {len(final_data)} 条")
            print(f"   文件大小: {os.path.getsize(filepath) / 1024 / 1024:.2f} MB")
            print(f"💾 文件路径: {filepath}")
            
            # 显示数据预览
            print(f"\n📈 数据预览:")
            preview_cols = ['TradeDate', 'StockCode', 'StockName', 'Open', 'High', 'Low', 'Close', 'Volume']
            available_cols = [col for col in preview_cols if col in final_data.columns]
            print(final_data[available_cols].head(10))
            
            return final_data
        else:
            print("❌ 没有可合并的数据")
            return None


def main():
    """主函数"""
    print("🚀 A股数据批量下载工具 - 修复版")
    print("=" * 50)
    
    # 配置参数
    OUTPUT_DIR = "e:/stockdata"
    START_DATE = "20250228"  # 2025-02-28
    END_DATE = "20250801"    # 2025-08-01
    
    # 创建下载器
    downloader = StockDataDownloaderFixed(output_dir=OUTPUT_DIR)
    
    while True:
        print("\n📋 请选择下载模式:")
        print("1. 批量下载热门A股数据 (10只股票)")
        print("2. 创建合并的CSV文件")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            # 批量下载
            print(f"\n📥 开始下载热门股票数据 ({START_DATE} 到 {END_DATE})")
            results = downloader.download_all_stocks(START_DATE, END_DATE)
            
            print(f"\n📊 下载结果统计:")
            print(f"   总计: {results['total']} 只股票")
            print(f"   成功: {results['success']} 只")
            print(f"   失败: {results['failed']} 只")
            
            if results['failed_list']:
                print(f"   失败列表: {', '.join(results['failed_list'])}")
        
        elif choice == "2":
            # 创建合并文件
            print(f"\n🔄 开始创建合并CSV文件 ({START_DATE} 到 {END_DATE})")
            downloader.create_combined_file(START_DATE, END_DATE)
        
        elif choice == "3":
            print("\n👋 感谢使用A股数据下载工具!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()