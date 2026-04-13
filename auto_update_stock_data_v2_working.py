#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据自动更新工具 - 版本2.0 工作版

专门针对当前网络环境优化：
- 只使用可连接的服务器: 47.107.33.27
- 开始时间: 20200101
- 文件名: 添加zl后缀
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import requests
import warnings
warnings.filterwarnings('ignore')


class TushareAPIWorking:
    """Tushare API 工作版本 - 只使用可连接的服务器"""
    
    def __init__(self, token="46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"):
        """初始化Tushare API工作版本"""
        self.token = token
        
        # 只使用可连接的服务器
        self.base_urls = [
            "http://47.107.33.27"  # 唯一可连接的服务器
        ]
        
        self.current_url_index = 0
        
        print("Tushare API 工作版初始化成功")
        print(f"使用Token: {token[:10]}...")
        print("可用服务器: 1 个 (47.107.33.27)")
    
    def _make_request(self, api_name, params, max_retries=5):
        """发送API请求，使用唯一可连接的服务器"""
        payload = {
            "api_name": api_name,
            "token": self.token,
            "params": params
        }
        
        # 正确的请求头
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for attempt in range(max_retries):
            base_url = self.base_urls[self.current_url_index]
            
            try:
                # 使用较长的超时时间
                timeout = 20 + attempt * 5  # 每次重试增加5秒超时
                
                response = requests.post(
                    base_url, 
                    json=payload, 
                    headers=headers,
                    timeout=timeout
                )
                
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
                    print(f"HTTP错误 {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {type(e).__name__}")
                
                if attempt < max_retries - 1:
                    wait_time = 3 + attempt * 2  # 递增等待时间
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                continue
            
            except Exception as e:
                print(f"未知错误: {e}")
                break
        
        print("所有重试尝试失败")
        return None
    
    def get_stock_basic(self):
        """获取股票基本信息"""
        return self._make_request('stock_basic', {'list_status': 'L'})
    
    def get_daily_data(self, ts_code, start_date, end_date):
        """获取日线数据"""
        params = {
            'ts_code': ts_code,
            'start_date': str(start_date),
            'end_date': str(end_date)
        }
        return self._make_request('daily', params)


class AutoStockDataUpdaterV2Working:
    """A股数据自动更新器 - 工作版本"""
    
    def __init__(self, data_dir="e:/stockdata", config_file="e:/stockdata/update_config_v2.json"):
        """初始化更新器"""
        self.data_dir = data_dir
        self.config_file = config_file
        self.api = TushareAPIWorking()
        
        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        
        # 市场分类 - 使用zl后缀文件名
        self.MARKET_CATEGORIES = {
            'sz': {'name': '深圳股市', 'file': 'stockszzl.csv', 'prefix': ['000', '002', '003', '300']},
            'sh': {'name': '上海股市', 'file': 'stockshzl.csv', 'prefix': ['600', '601', '603', '605', '688']},
            'other': {'name': '其他股市', 'file': 'stockotherzl.csv', 'prefix': []}
        }
        
        # 加载配置
        self.config = self._load_config()
        
        print(f"数据目录: {data_dir}")
        print(f"配置文件: {config_file}")
        print("开始时间: 20200101")
        print("文件命名: 添加zl后缀")
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"配置文件读取失败: {e}")
        
        # 默认配置 - 开始时间改为20200101
        return {
            'last_update': '20200101',
            'market_status': {}
        }
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"配置文件保存失败: {e}")
    
    def show_market_status(self):
        """显示各市场状态"""
        print("\n各市场数据状态:")
        print("-" * 40)
        
        for market, info in self.MARKET_CATEGORIES.items():
            file_path = os.path.join(self.data_dir, info['file'])
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    stock_count = df['ts_code'].nunique()
                    date_range = f"{df['trade_date'].min()} 至 {df['trade_date'].max()}"
                    print(f"{info['name']}: {stock_count}只股票, {len(df)}条记录")
                    print(f"  时间范围: {date_range}")
                    print(f"  文件: {info['file']}")
                except Exception as e:
                    print(f"{info['name']}: 文件读取错误 - {e}")
            else:
                print(f"{info['name']}: 无数据文件")
            
            print("-" * 40)
    
    def download_all_markets(self):
        """下载所有市场数据"""
        print("\n开始下载所有市场数据...")
        
        # 获取股票列表
        print("获取股票列表...")
        stock_basic = self.api.get_stock_basic()
        
        if stock_basic is None or stock_basic.empty:
            print("获取股票列表失败")
            return
        
        print(f"获取到 {len(stock_basic)} 只股票")
        
        # 按市场分类股票
        market_stocks = {}
        for market, info in self.MARKET_CATEGORIES.items():
            if market == 'other':
                # 其他市场：不属于深圳和上海的股票
                market_stocks[market] = stock_basic[
                    ~stock_basic['ts_code'].str.startswith(tuple(self.MARKET_CATEGORIES['sz']['prefix'])) &
                    ~stock_basic['ts_code'].str.startswith(tuple(self.MARKET_CATEGORIES['sh']['prefix']))
                ]['ts_code'].tolist()
            else:
                # 深圳和上海市场
                market_stocks[market] = stock_basic[
                    stock_basic['ts_code'].str.startswith(tuple(info['prefix']))
                ]['ts_code'].tolist()
        
        # 下载各市场数据 - 开始时间改为20200101
        start_date = '20200101'
        end_date = datetime.now().strftime('%Y%m%d')
        
        print(f"时间范围: {start_date} 至 {end_date}")
        
        for market, stock_codes in market_stocks.items():
            if stock_codes:
                print(f"\n下载 {self.MARKET_CATEGORIES[market]['name']} 数据 ({len(stock_codes)}只股票)...")
                self._download_market_data(market, stock_codes, start_date, end_date)
            else:
                print(f"\n{self.MARKET_CATEGORIES[market]['name']} 无股票数据")
        
        # 更新配置
        self.config['last_update'] = end_date
        self._save_config()
        
        print("\n所有市场数据下载完成!")
    
    def _download_market_data(self, market, stock_codes, start_date, end_date, is_update=False):
        """下载单个市场数据"""
        market_info = self.MARKET_CATEGORIES[market]
        file_path = os.path.join(self.data_dir, market_info['file'])
        
        all_data = []
        success_count = 0
        failed_count = 0
        
        for i, ts_code in enumerate(stock_codes, 1):
            print(f"  下载 {ts_code} ({i}/{len(stock_codes)})...", end='')
            
            try:
                data = self.api.get_daily_data(ts_code, start_date, end_date)
                
                if data is not None and not data.empty:
                    all_data.append(data)
                    success_count += 1
                    print(" [OK]")
                else:
                    failed_count += 1
                    print(" [无数据]")
                
            except Exception as e:
                failed_count += 1
                print(f" [失败: {e}]")
        
        # 保存数据
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            
            if is_update and os.path.exists(file_path):
                # 更新模式：读取现有数据，去重后合并
                try:
                    existing_data = pd.read_csv(file_path)
                    
                    # 合并数据并去重
                    merged_data = pd.concat([existing_data, combined_data], ignore_index=True)
                    
                    # 按交易日期和股票代码去重（保留最新数据）
                    merged_data = merged_data.drop_duplicates(
                        subset=['trade_date', 'ts_code'], 
                        keep='last'
                    )
                    
                    # 按日期排序
                    merged_data = merged_data.sort_values(['ts_code', 'trade_date'])
                    
                    merged_data.to_csv(file_path, index=False, encoding='utf-8-sig')
                    print(f"SUCCESS {market_info['name']}数据更新成功: 新增{len(combined_data)}条记录, 总记录{len(merged_data)}条")
                    
                except Exception as e:
                    print(f"ERROR 数据合并失败: {e}")
                    # 如果合并失败，保存新数据到临时文件
                    temp_file = file_path.replace('.csv', '_new.csv')
                    combined_data.to_csv(temp_file, index=False, encoding='utf-8-sig')
                    print(f"新数据已保存到: {temp_file}")
            else:
                # 初始下载模式：直接保存
                combined_data.to_csv(file_path, index=False, encoding='utf-8-sig')
                print(f"SUCCESS {market_info['name']}数据保存成功: {success_count}只股票, {len(combined_data)}条记录")
        else:
            print(f"ERROR {market_info['name']}无数据下载成功")
    
    def run(self):
        """运行主程序"""
        while True:
            print("\n" + "=" * 50)
            print("A股数据自动更新工具 - 工作版本")
            print("=" * 50)
            print("请选择操作:")
            print("1. 显示各市场状态")
            print("2. 初始下载所有市场数据")
            print("3. 更新深圳股市数据")
            print("4. 更新上海股市数据")
            print("5. 更新其他股市数据")
            print("6. 更新所有市场数据")
            print("7. 退出")
            
            choice = input("请输入选择 (1-7): ").strip()
            
            if choice == '1':
                self.show_market_status()
            elif choice == '2':
                self.download_all_markets()
            elif choice in ['3', '4', '5', '6']:
                print("更新功能暂未实现，请使用选项2进行初始下载")
            elif choice == '7':
                print("退出程序")
                break
            else:
                print("无效选择，请重新输入")


if __name__ == "__main__":
    updater = AutoStockDataUpdaterV2Working()
    updater.run()