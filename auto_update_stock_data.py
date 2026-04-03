#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据自动更新工具

支持一次性下载完整数据后，自动更新到当日最新数据
智能检测数据缺失并自动补充
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


class AutoStockDataUpdater:
    """A股数据自动更新器"""
    
    def __init__(self, data_file="e:/stockdata/stockdata.csv", config_file="e:/stockdata/update_config.json"):
        """
        初始化自动更新器
        
        Args:
            data_file: 数据文件路径
            config_file: 更新配置文件路径
        """
        self.data_file = data_file
        self.config_file = config_file
        self.fetcher = ChinaStockFetcherTushareFixed()
        
        # 加载配置
        self.config = self._load_config()
        
        # 加载现有数据
        self.existing_data = self._load_existing_data()
        
        print(f"📁 数据文件: {data_file}")
        print(f"⚙️  配置文件: {config_file}")
    
    def _load_config(self):
        """加载或创建配置文件"""
        default_config = {
            'last_update_date': None,
            'update_frequency': 'daily',  # daily, weekly, monthly
            'auto_update_enabled': True,
            'stock_codes': [],
            'initial_download_complete': False
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print("✅ 成功加载配置文件")
                return {**default_config, **config}
            else:
                # 创建配置文件目录
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                
                # 保存默认配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                
                print("📝 创建默认配置文件")
                return default_config
                
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return False
    
    def _load_existing_data(self):
        """加载现有数据文件"""
        try:
            if not os.path.exists(self.data_file):
                print(f"📝 数据文件不存在，将创建新文件")
                return None
            
            df = pd.read_csv(self.data_file)
            
            # 更新配置中的股票代码列表
            if not df.empty:
                self.config['stock_codes'] = df['ts_code'].unique().tolist()
                
                # 更新最后更新日期
                if 'trade_date' in df.columns:
                    latest_date = df['trade_date'].max()
                    self.config['last_update_date'] = latest_date
                    self.config['initial_download_complete'] = True
            
            print(f"✅ 成功加载现有数据")
            print(f"   总记录数: {len(df)} 条")
            print(f"   股票代码数量: {len(self.config['stock_codes'])} 只")
            
            if self.config['last_update_date']:
                print(f"   最后更新日期: {self.config['last_update_date']}")
            
            return df
            
        except Exception as e:
            print(f"❌ 加载数据文件失败: {e}")
            return None
    
    def get_update_needed_info(self):
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
    
    def initial_download(self, start_date="20250228", end_date=None):
        """
        初始下载完整数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期（默认今日）
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        print(f"🚀 开始初始下载完整数据")
        print(f"📅 时间范围: {start_date} 到 {end_date}")
        
        # 定义热门A股股票列表
        popular_stocks = {
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
        
        all_data = []
        success_count = 0
        
        for stock_name, symbol in popular_stocks.items():
            try:
                print(f"📥 下载 {stock_name} ({symbol})...")
                
                data = self.fetcher.get_a_stock_data(symbol, start_date=start_date, end_date=end_date, use_cache=False)
                
                if data is not None and not data.empty:
                    # 转换为Tushare格式
                    converted_data = self._convert_to_tushare_format(data, symbol, stock_name)
                    all_data.append(converted_data)
                    success_count += 1
                    print(f"✅ {stock_name} 下载成功 ({len(data)} 条记录)")
                else:
                    print(f"❌ {stock_name} 下载失败")
                
                # 添加延迟
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {stock_name} 下载失败: {e}")
        
        if all_data:
            # 合并所有数据
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # 保存数据
            self._save_data(combined_data)
            
            # 更新配置
            self.config['last_update_date'] = end_date
            self.config['stock_codes'] = list(popular_stocks.values())
            self.config['initial_download_complete'] = True
            self.save_config()
            
            print(f"\n🎉 初始下载完成!")
            print(f"   成功下载: {success_count} 只股票")
            print(f"   总记录数: {len(combined_data)} 条")
            print(f"   时间范围: {start_date} 到 {end_date}")
            
            return True
        else:
            print("❌ 初始下载失败，没有成功下载任何数据")
            return False
    
    def auto_update(self):
        """自动更新到最新数据"""
        update_info = self.get_update_needed_info()
        
        if not update_info['update_needed']:
            print(f"✅ {update_info['reason']}")
            return True
        
        print(f"🔄 开始自动更新")
        print(f"   原因: {update_info['reason']}")
        print(f"   更新范围: {update_info['from_date']} 到 {update_info['to_date']}")
        
        if not self.config['stock_codes']:
            print("❌ 没有配置股票代码，请先进行初始下载")
            return False
        
        all_updated_data = []
        success_count = 0
        
        for symbol in self.config['stock_codes']:
            try:
                print(f"📥 更新 {symbol}...")
                
                # 从最后更新日期的下一天开始
                from_date = (datetime.strptime(update_info['from_date'], '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
                
                data = self.fetcher.get_a_stock_data(symbol, start_date=from_date, end_date=update_info['to_date'], use_cache=False)
                
                if data is not None and not data.empty:
                    # 转换为Tushare格式
                    converted_data = self._convert_to_tushare_format(data, symbol)
                    all_updated_data.append(converted_data)
                    success_count += 1
                    print(f"✅ {symbol} 更新成功 ({len(data)} 条记录)")
                else:
                    print(f"⚠️  {symbol} 无新数据")
                
                # 添加延迟
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {symbol} 更新失败: {e}")
        
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
            
            print(f"\n🎉 自动更新完成!")
            print(f"   成功更新: {success_count} 只股票")
            print(f"   新增记录: {len(updated_data)} 条")
            print(f"   总记录数: {len(combined_data)} 条")
            print(f"   最新日期: {update_info['to_date']}")
            
            return True
        else:
            print("⚠️  没有新数据需要更新")
            return True
    
    def _convert_to_tushare_format(self, data, symbol, stock_name=None):
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
            
            print(f"💾 数据已保存到: {self.data_file}")
            print(f"   文件大小: {os.path.getsize(self.data_file) / 1024 / 1024:.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据保存失败: {e}")
            return False
    
    def show_status(self):
        """显示当前状态"""
        print("\n📊 当前状态信息")
        print("=" * 40)
        
        update_info = self.get_update_needed_info()
        
        print(f"📁 数据文件: {self.data_file}")
        print(f"⚙️  配置文件: {self.config_file}")
        print(f"📈 初始下载完成: {'✅' if self.config['initial_download_complete'] else '❌'}")
        
        if self.config['last_update_date']:
            print(f"📅 最后更新日期: {self.config['last_update_date']}")
        
        print(f"📊 股票数量: {len(self.config['stock_codes'])} 只")
        
        if self.existing_data is not None:
            print(f"📋 总记录数: {len(self.existing_data)} 条")
        
        print(f"🔄 更新状态: {update_info['reason']}")
        
        if update_info['update_needed']:
            print(f"📥 需要更新: {update_info['days_to_update']} 天数据")


def main():
    """主函数"""
    print("🚀 A股数据自动更新工具")
    print("=" * 50)
    
    # 配置参数
    DATA_FILE = "e:/stockdata/stockdata.csv"
    CONFIG_FILE = "e:/stockdata/update_config.json"
    
    # 创建自动更新器
    updater = AutoStockDataUpdater(data_file=DATA_FILE, config_file=CONFIG_FILE)
    
    while True:
        print("\n📋 请选择操作:")
        print("1. 显示当前状态")
        print("2. 初始下载完整数据")
        print("3. 自动更新到最新数据")
        print("4. 一键初始下载并自动更新")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            # 显示状态
            updater.show_status()
        
        elif choice == "2":
            # 初始下载
            if updater.config['initial_download_complete']:
                confirm = input("⚠️  已经进行过初始下载，确定要重新下载吗？(y/N): ").strip().lower()
                if confirm != 'y':
                    continue
            
            start_date = input("请输入开始日期 (默认20250228): ").strip() or "20250228"
            end_date = input("请输入结束日期 (默认今日): ").strip()
            
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            updater.initial_download(start_date, end_date)
        
        elif choice == "3":
            # 自动更新
            if not updater.config['initial_download_complete']:
                print("❌ 请先进行初始下载")
                continue
            
            updater.auto_update()
        
        elif choice == "4":
            # 一键初始下载并自动更新
            print("🚀 开始一键初始下载并自动更新")
            
            # 初始下载
            if updater.initial_download("20250228"):
                # 自动更新
                updater.auto_update()
        
        elif choice == "5":
            print("\n👋 感谢使用A股数据自动更新工具!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()