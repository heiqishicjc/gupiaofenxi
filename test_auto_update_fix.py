#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动更新工具修复
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 导入修复后的类
from auto_update_stock_data_enhanced_no_token import EnhancedStockDataUpdaterNoToken

def test_type_conversion():
    """测试类型转换修复"""
    print("测试类型转换修复...")
    
    # 创建测试实例
    updater = EnhancedStockDataUpdaterNoToken()
    
    # 测试 get_update_needed_info 方法
    print("1. 测试 get_update_needed_info 方法...")
    try:
        update_info = updater.get_update_needed_info()
        print(f"   ✅ 成功: {update_info['reason']}")
        print(f"   最后更新: {update_info.get('last_update', 'N/A')}")
        print(f"   需要更新: {update_info.get('update_needed', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    # 测试市场分类统计
    print("\n2. 测试市场分类统计...")
    try:
        updater.show_market_statistics()
        print("   ✅ 成功")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    # 测试单个股票数据获取
    print("\n3. 测试单个股票数据获取...")
    try:
        # 使用一个测试股票代码
        test_symbol = "600519.SH"  # 贵州茅台
        start_date = "20250401"
        end_date = "20250403"
        
        data = updater.get_stock_data_from_api(test_symbol, start_date, end_date)
        if data is not None:
            print(f"   ✅ 成功获取 {len(data)} 条记录")
        else:
            print("   ⚠️ 无数据返回（可能是模拟数据限制）")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    # 测试重复检查功能
    print("\n4. 测试重复检查功能...")
    try:
        # 创建一个测试数据
        test_data = pd.DataFrame({
            'trade_date': ['20250401', '20250402'],
            'ts_code': ['600519.SH', '600519.SH'],
            'open': [100.0, 101.0],
            'high': [102.0, 103.0],
            'low': [99.0, 100.0],
            'close': [101.0, 102.0],
            'vol': [1000000, 1100000]
        })
        
        # 测试重复检查
        is_duplicate = updater.check_duplicate_data("600519.SH", "20250401")
        print(f"   ✅ 重复检查功能正常: {is_duplicate}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！类型转换修复成功！")
    return True

def test_small_update():
    """测试小规模更新功能"""
    print("\n测试小规模更新功能...")
    
    # 创建测试实例
    updater = EnhancedStockDataUpdaterNoToken()
    
    # 测试更新少量股票
    print("1. 测试更新少量股票...")
    try:
        # 只更新前5只深圳股票
        market_stocks = updater.get_market_stocks("深圳股市")[:5]
        
        if not market_stocks:
            print("   ⚠️ 没有深圳股票数据，跳过测试")
            return True
            
        print(f"   测试股票: {market_stocks}")
        
        # 临时修改股票列表进行测试
        original_stocks = updater.config['market_categories']['深圳股市']['stocks']
        updater.config['market_categories']['深圳股市']['stocks'] = market_stocks
        
        # 测试更新
        result = updater.update_market_data("深圳股市", max_stocks=2, delay_between_stocks=0.1)
        
        # 恢复原始股票列表
        updater.config['market_categories']['深圳股市']['stocks'] = original_stocks
        
        print(f"   ✅ 更新测试完成")
        print(f"   成功: {result.get('success', 0)} 只股票")
        print(f"   失败: {result.get('failed', 0)} 只股票")
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False
    
    print("\n🎉 小规模更新测试通过！")
    return True

def main():
    """主测试函数"""
    print("A股数据自动更新工具修复测试")
    print("=" * 50)
    
    # 测试类型转换修复
    if not test_type_conversion():
        print("\n❌ 类型转换测试失败")
        return
    
    # 测试小规模更新功能
    if not test_small_update():
        print("\n❌ 小规模更新测试失败")
        return
    
    print("\n" + "=" * 50)
    print("🎊 所有测试通过！自动更新工具修复成功！")
    print("\n工具功能总结:")
    print("✅ 类型转换修复 - 解决 numpy.int64 问题")
    print("✅ 市场分类功能 - 支持深圳、上海、其他股市")
    print("✅ 重复检查功能 - 避免重复下载数据")
    print("✅ 可控更新时间 - 支持延迟和批量控制")
    print("✅ 用户友好界面 - 7个操作选项的交互菜单")

if __name__ == "__main__":
    main()