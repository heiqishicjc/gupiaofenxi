#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版股票数据下载工具
"""

import requests
import pandas as pd
import os
from datetime import datetime

class SimpleStockDownloader:
    def __init__(self):
        self.token = "46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"
        self.base_url = "http://api.tushare.pro"
        self.data_dir = "e:/stockdata"
        
        # 创建数据目录
        os.makedirs(self.data_dir, exist_ok=True)
        
        print("简化版股票数据下载工具")
        print("=" * 50)
    
    def _make_request(self, api_name, params):
        """发送API请求"""
        payload = {
            "api_name": api_name,
            "token": self.token,
            "params": params
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result['code'] == 0:
                    # 转换为DataFrame
                    data = result['data']
                    df = pd.DataFrame(data['items'], columns=data['fields'])
                    return df
                else:
                    print(f"API错误: {result['msg']}")
                    return None
            else:
                print(f"HTTP错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def download_stock_list(self):
        """下载股票列表"""
        print("正在下载股票列表...")
        
        df = self._make_request('stock_basic', {'list_status': 'L'})
        
        if df is not None:
            print(f"成功获取 {len(df)} 只股票列表")
            
            # 保存股票列表
            file_path = os.path.join(self.data_dir, "stock_list.csv")
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"股票列表已保存到: {file_path}")
            
            return df
        else:
            print("获取股票列表失败")
            return None
    
    def download_sample_data(self, count=10):
        """下载样本数据"""
        print(f"正在下载 {count} 只股票的样本数据...")
        
        # 获取股票列表
        stock_list = self.download_stock_list()
        
        if stock_list is None:
            return
        
        # 选择前count只股票
        sample_stocks = stock_list.head(count)
        
        all_data = []
        success_count = 0
        
        for i, (_, stock) in enumerate(sample_stocks.iterrows(), 1):
            print(f"  下载 {stock['ts_code']} ({i}/{count})...", end="")
            
            # 下载日线数据（最近30天）
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - pd.Timedelta(days=30)).strftime('%Y%m%d')
            
            params = {
                'ts_code': stock['ts_code'],
                'start_date': start_date,
                'end_date': end_date
            }
            
            data = self._make_request('daily', params)
            
            if data is not None and not data.empty:
                all_data.append(data)
                success_count += 1
                print(" [OK]")
            else:
                print(" [无数据]")
        
        # 保存数据
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            file_path = os.path.join(self.data_dir, "sample_stock_data.csv")
            combined_data.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            print(f"\n✅ 样本数据下载完成！")
            print(f"成功下载: {success_count}/{count} 只股票")
            print(f"总记录数: {len(combined_data)} 条")
            print(f"数据文件: {file_path}")
        else:
            print("\n❌ 无数据下载成功")

def main():
    downloader = SimpleStockDownloader()
    
    while True:
        print("\n请选择操作:")
        print("1. 下载股票列表")
        print("2. 下载样本数据（10只股票）")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            downloader.download_stock_list()
        
        elif choice == "2":
            downloader.download_sample_data()
        
        elif choice == "3":
            print("感谢使用！")
            break
        
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()