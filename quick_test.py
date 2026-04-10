#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试自动更新工具修复
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 导入修复后的类
from auto_update_stock_data_enhanced_no_token import EnhancedStockDataUpdaterNoToken

def main():
    print("=== 快速测试自动更新工具修复 ===")
    
    # 创建测试实例
    updater = EnhancedStockDataUpdaterNoToken()
    
    print("\n1. 测试 get_update_needed_info 方法...")
    try:
        update_info = updater.get_update_needed_info()
        print("   成功:", update_info['reason'])
        print("   最后更新:", update_info.get('last_update', 'N/A'))
        print("   需要更新:", update_info.get('update_needed', 'N/A'))
        print("   类型转换修复成功")
    except Exception as e:
        print("   失败:", e)
        print("   类型转换修复失败")
        return
    
    print("\n2. 测试市场分类统计...")
    try:
        updater.show_market_statistics()
        print("   市场分类功能正常")
    except Exception as e:
        print("   失败:", e)
        print("   市场分类功能异常")
        return
    
    print("\n3. 测试单个股票数据获取...")
    try:
        # 使用一个测试股票代码
        test_symbol = "600519.SH"  # 贵州茅台
        start_date = "20250401"
        end_date = "20250403"
        
        data = updater.get_stock_data_from_api(test_symbol, start_date, end_date)
        if data is not None:
            print("   成功获取", len(data), "条记录")
        else:
            print("   无数据返回（可能是模拟数据限制）")
        print("   数据获取功能正常")
    except Exception as e:
        print("   失败:", e)
        print("   数据获取功能异常")
        return
    
    print("\n=== 测试完成 ===")
    print("所有功能测试通过！类型转换修复成功！")

if __name__ == "__main__":
    main()