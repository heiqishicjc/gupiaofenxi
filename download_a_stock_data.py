#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据下载工具 - 简化版

将A股数据下载到指定CSV文件中
时间范围: 2025-02-28 到 2025-08-01
保存路径: e:/stockdata/stockdata.csv
"""

import sys
import os
import pandas as pd
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.china_stock_fetcher import ChinaStockFetcher


def download_stock_data():
    """
    下载A股数据到指定文件
    
    时间范围: 2025-02-28 到 2025-08-01
    保存路径: e:/stockdata/stockdata.csv
    """
    print("🚀 A股数据下载工具")
    print("=" * 50)
    
    # 配置参数
    OUTPUT_FILE = "e:/stockdata/stockdata.csv"
    START_DATE = "20250228"  # 2025-02-28
    END_DATE = "20250801"    # 2025-08-01
    
    # 热门A股股票列表
    STOCKS_TO_DOWNLOAD = {
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
    
    # 创建输出目录
    output_dir = os.path.dirname(OUTPUT_FILE)
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    print(f"💾 输出文件: {os.path.basename(OUTPUT_FILE)}")
    print(f"📅 时间范围: {START_DATE} 到 {END_DATE}")
    print(f"📊 下载股票: {len(STOCKS_TO_DOWNLOAD)} 只")
    print("=" * 50)
    
    # 创建数据获取器
    fetcher = ChinaStockFetcher(prefer_tushare=True)
    
    all_stock_data = []
    success_count = 0
    
    for stock_name, symbol in STOCKS_TO_DOWNLOAD.items():
        print(f"\n📥 正在下载 {stock_name} ({symbol})...")
        
        try:
            # 使用Tushare获取数据
            data = fetcher.get_a_stock_data(symbol, start_date=START_DATE, end_date=END_DATE, use_cache=False)
            
            if data is None or data.empty:
                print(f"❌ {stock_name} 数据获取失败")
                continue
            
            # 添加股票标识信息
            data['StockCode'] = symbol
            data['StockName'] = stock_name
            data['Market'] = 'SH' if symbol.endswith('.SH') else 'SZ'
            
            # 添加日期列（便于分析）
            data['TradeDate'] = data.index.strftime('%Y-%m-%d')
            
            all_stock_data.append(data)
            success_count += 1
            
            print(f"✅ {stock_name} 下载成功")
            print(f"   记录数: {len(data)} 条")
            print(f"   时间范围: {data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"   最新收盘价: {data['Close'].iloc[-1]:.2f}")
            
        except Exception as e:
            print(f"❌ {stock_name} 下载失败: {e}")
    
    if all_stock_data:
        print(f"\n🔄 正在合并数据并保存到文件...")
        
        # 合并所有股票数据
        combined_data = pd.concat(all_stock_data)
        
        # 按日期和股票代码排序
        combined_data = combined_data.sort_values(['TradeDate', 'StockCode'])
        
        # 保存到CSV文件
        combined_data.to_csv(OUTPUT_FILE, encoding='utf-8-sig', index=False)
        
        print(f"\n🎉 数据下载完成!")
        print("=" * 50)
        print(f"📊 下载统计:")
        print(f"   成功下载: {success_count} 只股票")
        print(f"   失败下载: {len(STOCKS_TO_DOWNLOAD) - success_count} 只股票")
        print(f"   总记录数: {len(combined_data)} 条")
        print(f"   文件大小: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.2f} MB")
        print(f"💾 文件路径: {OUTPUT_FILE}")
        
        # 显示数据预览
        print(f"\n📈 数据预览:")
        print(combined_data[['TradeDate', 'StockCode', 'StockName', 'Open', 'High', 'Low', 'Close', 'Volume']].head(10))
        
        return True
    else:
        print("❌ 没有成功下载任何数据")
        return False


def download_specific_stock(symbol, stock_name):
    """
    下载指定股票数据
    
    Args:
        symbol: 股票代码
        stock_name: 股票名称
    """
    OUTPUT_FILE = f"e:/stockdata/{symbol}_{stock_name}.csv"
    START_DATE = "20250228"
    END_DATE = "20250801"
    
    # 创建输出目录
    output_dir = os.path.dirname(OUTPUT_FILE)
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建数据获取器
    fetcher = ChinaStockFetcher(prefer_tushare=True)
    
    print(f"📥 正在下载 {stock_name} ({symbol})...")
    
    try:
        data = fetcher.get_a_stock_data(symbol, start_date=START_DATE, end_date=END_DATE, use_cache=False)
        
        if data is None or data.empty:
            print(f"❌ {stock_name} 数据获取失败")
            return False
        
        # 添加日期列
        data['TradeDate'] = data.index.strftime('%Y-%m-%d')
        
        # 保存到CSV文件
        data.to_csv(OUTPUT_FILE, encoding='utf-8-sig', index=False)
        
        print(f"✅ {stock_name} 下载成功")
        print(f"   文件: {OUTPUT_FILE}")
        print(f"   记录数: {len(data)} 条")
        print(f"   时间范围: {data.index[0].strftime('%Y-%m-%d')} 到 {data.index[-1].strftime('%Y-%m-%d')}")
        
        return True
        
    except Exception as e:
        print(f"❌ {stock_name} 下载失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 A股数据下载工具")
    print("=" * 50)
    
    while True:
        print("\n📋 请选择下载模式:")
        print("1. 批量下载热门A股数据 (10只股票)")
        print("2. 下载单只股票数据")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            # 批量下载
            download_stock_data()
            break
        
        elif choice == "2":
            # 单只股票下载
            print("\n📋 请输入股票信息:")
            symbol = input("股票代码 (如: 600519.SH): ").strip()
            stock_name = input("股票名称 (如: 贵州茅台): ").strip()
            
            if symbol and stock_name:
                download_specific_stock(symbol, stock_name)
            else:
                print("❌ 请输入完整的股票信息")
            break
        
        elif choice == "3":
            print("\n👋 感谢使用A股数据下载工具!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()