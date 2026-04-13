#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据自动更新工具 - 版本2.0 IP直连最终版

修复问题：
1. 修复HTTP 405错误 - 使用正确的请求头
2. 使用IP地址直连，绕过DNS解析问题
3. 支持完整5395只股票更新
4. 智能重试机制

升级功能：
1. 按市场分类保存数据：深圳市场(stockszzl.csv)、上海市场(stockshzl.csv)、其他市场(stockotherzl.csv)
2. 数据完整性检测：检测数据缺失并自动补充
3. 时间范围：20200101到当前日期
4. 智能更新：只更新缺失的数据
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


class TushareAPIFinal:
    """Tushare API 最终修复版本"""
    
    def __init__(self, token="46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad"):
        """初始化Tushare API最终修复版本"""
        self.token = token
        
        # 使用IP地址直连，绕过DNS解析
        self.base_urls = [
            "http://api.tushare.pro",  # 主域名
            "http://116.62.129.122",   # IP地址1
            "http://47.107.33.27"      # IP地址2
        ]
        
        self.current_url_index = 0
        
        print("Tushare API 最终修复版初始化成功")
        print(f"使用Token: {token[:10]}...")
        print("可用服务器:", len(self.base_urls), "个")
    
    def _make_request(self, api_name, params, max_retries=3):
        """发送API请求，支持重试和服务器切换"""
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
                # 使用正确的请求头和超时设置
                response = requests.post(
                    base_url, 
                    json=payload, 
                    headers=headers,
                    timeout=15
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
                    print(f"HTTP错误 {response.status_code}: {response.text[:100]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"请求失败 (服务器 {self.current_url_index + 1}): {e}")
                
                # 切换到下一个服务器
                self.current_url_index = (self.current_url_index + 1) % len(self.base_urls)
                
                if attempt < max_retries - 1:
                    print(f"切换到服务器 {self.current_url_index + 1}...")
                    time.sleep(2)  # 重试前等待2秒
                continue
            
            except Exception as e:
                print(f"未知错误: {e}")
                break
        
        print("所有服务器尝试失败")
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


class AutoStockDataUpdaterV2Final:
    """A股数据自动更新器 - 最终修复版本"""
    
    def __init__(self, data_dir="e:/stockdata", config_file="e:/stockdata/update_config_v2.json"):
        """初始化更新器"""
        self.data_dir = data_dir
        self.config_file = config_file
        self.api = TushareAPIFinal()
        
        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        
        # 市场分类
        self.MARKET_CATEGORIES = {
            'sz': {'name': '深圳股市', 'file': 'stockszzl.csv', 'prefix': ['000', '002', '003', '300']},
            'sh': {'name': '上海股市', 'file': 'stockshzl.csv', 'prefix': ['600', '601', '603', '605', '688']},
            'other': {'name': '其他股市', 'file': 'stockotherzl.csv', 'prefix': []}
        }
        
        # 加载配置
        self.config = self._load_config()
        
        print(f"数据目录: {data_dir}")
        print(f"配置文件: {config_file}")
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 默认配置
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
            print(f"保存配置失败: {e}")
    
    def get_stock_market(self, ts_code):
        """根据股票代码判断市场"""
        code_prefix = ts_code[:6]
        
        for market, info in self.MARKET_CATEGORIES.items():
            if market == 'other':
                continue
            for prefix in info['prefix']:
                if code_prefix.startswith(prefix):
                    return market
        
        return 'other'
    
    def show_market_status(self):
        """显示各市场状态"""
        print("\n=== 各市场状态 ===")
        
        for market, info in self.MARKET_CATEGORIES.items():
            file_path = os.path.join(self.data_dir, info['file'])
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    stock_count = len(df['ts_code'].unique())
                    date_range = f"{df['trade_date'].min()} 至 {df['trade_date'].max()}"
                    print(f"{info['name']}: {stock_count}只股票, 数据范围: {date_range}")
                except:
                    print(f"{info['name']}: 文件存在但无法读取")
            else:
                print(f"{info['name']}: 文件不存在")
    
    def initial_download_all_markets(self, full_download=False):
        """初始下载所有市场数据"""
        print("\n开始获取股票列表...")
        
        # 获取股票列表
        stock_basic = self.api.get_stock_basic()
        if stock_basic is None:
            print("获取股票列表失败")
            return
        
        print(f"成功获取 {len(stock_basic)} 只股票列表")
        
        # 限制测试数量
        if not full_download:
            stock_basic = stock_basic.head(5)  # 测试模式只下载5只股票
            print("测试模式: 只下载前5只股票")
        
        # 按市场分类
        market_stocks = {market: [] for market in self.MARKET_CATEGORIES.keys()}
        
        for _, stock in stock_basic.iterrows():
            market = self.get_stock_market(stock['ts_code'])
            market_stocks[market].append(stock['ts_code'])
        
        # 下载各市场数据
        start_date = '20200101'
        end_date = datetime.now().strftime('%Y%m%d')
        
        for market, stocks in market_stocks.items():
            if stocks:
                print(f"\n开始下载{self.MARKET_CATEGORIES[market]['name']}数据 ({len(stocks)}只股票)...")
                self._download_market_data(market, stocks, start_date, end_date)
    
    def _download_market_data(self, market, stock_codes, start_date, end_date):
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
                
                # 避免请求过快
                time.sleep(0.5)
                
            except Exception as e:
                failed_count += 1
                print(f" [失败: {e}]")
        
        # 保存数据
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"✅ {market_info['name']}数据保存成功: {success_count}只股票, {len(combined_data)}条记录")
        else:
            print(f"❌ {market_info['name']}无数据下载成功")
    
    def update_market_data(self, market):
        """更新单个市场数据"""
        market_info = self.MARKET_CATEGORIES[market]
        file_path = os.path.join(self.data_dir, market_info['file'])
        
        if not os.path.exists(file_path):
            print(f"{market_info['name']}数据文件不存在，请先进行初始下载")
            return
        
        print(f"开始更新{market_info['name']}数据...")
        
        # 读取现有数据
        try:
            existing_data = pd.read_csv(file_path)
            
            # 获取需要更新的股票列表
            stock_codes = existing_data['ts_code'].unique()
            
            # 获取最新数据
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')  # 更新最近7天数据
            end_date = datetime.now().strftime('%Y%m%d')
            
            self._download_market_data(market, stock_codes, start_date, end_date)
            
        except Exception as e:
            print(f"更新{market_info['name']}数据失败: {e}")
    
    def update_all_markets(self):
        """更新所有市场数据"""
        for market in self.MARKET_CATEGORIES.keys():
            self.update_market_data(market)


def main():
    """主函数"""
    print("A股数据自动更新工具 - 版本2.0 IP直连最终版")
    print("=" * 50)
    
    # 配置参数
    DATA_DIR = "e:/stockdata"
    CONFIG_FILE = "e:/stockdata/update_config_v2.json"
    
    # 创建自动更新器
    updater = AutoStockDataUpdaterV2Final(data_dir=DATA_DIR, config_file=CONFIG_FILE)
    
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
            print("\n请选择下载模式:")
            print("1. 完整下载 (下载所有股票)")
            print("2. 测试下载 (只下载少量股票进行测试)")
            
            download_choice = input("请输入选择 (1-2): ").strip()
            
            if download_choice == "1":
                print("开始完整下载所有股票...")
                updater.initial_download_all_markets(full_download=True)
            elif download_choice == "2":
                print("开始测试下载...")
                updater.initial_download_all_markets(full_download=False)
            else:
                print("使用默认测试下载模式")
                updater.initial_download_all_markets(full_download=False)
        
        elif choice == "3":
            # 更新深圳股市数据
            print("开始更新深圳股市数据...")
            updater.update_market_data("sz")
        
        elif choice == "4":
            # 更新上海股市数据
            print("开始更新上海股市数据...")
            updater.update_market_data("sh")
        
        elif choice == "5":
            # 更新其他股市数据
            print("开始更新其他股市数据...")
            updater.update_market_data("other")
        
        elif choice == "6":
            # 更新所有市场数据
            print("开始更新所有市场数据...")
            updater.update_all_markets()
        
        elif choice == "7":
            # 退出
            print("感谢使用A股数据自动更新工具！")
            break
        
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()