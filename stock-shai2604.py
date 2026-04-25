import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_stock_data(symbol, start_date=None, end_date=None):
    """从三个CSV文件中加载指定股票代码的数据，支持日期范围过滤"""
    csv_files = [
        r"e:\stockdatasz.csv",
        r"e:\stockdatash.csv",
        r"e:\stockdataother.csv"
    ]
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            continue
        
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            # 打印CSV文件的列名，方便调试
            print(f"文件 {csv_file} 的列名: {list(df.columns)}")
            
            # 查找股票代码列（扩展列名列表）
            symbol_col = None
            for col in ['symbol', 'code', 'ts_code', '股票代码', 'stock_code', '代码']:
                if col in df.columns:
                    symbol_col = col
                    break
            
            if symbol_col is None:
                print(f"文件 {csv_file} 中未找到股票代码列")
                continue
            
            print(f"找到股票代码列: {symbol_col}")
            
            # 过滤出目标股票（支持部分匹配，如 002495 匹配 002495.SZ）
            stock_data = df[df[symbol_col].astype(str).str.contains(str(symbol), na=False)]
            
            if stock_data.empty:
                print(f"文件 {csv_file} 中未找到股票 {symbol}")
                continue
            
            print(f"找到 {len(stock_data)} 条股票 {symbol} 的数据")
            
            # 确保有日期列（扩展列名列表）
            date_col = None
            for col in ['date', 'trade_date', '日期', '交易日期', 'datetime']:
                if col in stock_data.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print(f"文件 {csv_file} 中未找到日期列")
                continue
            
            print(f"找到日期列: {date_col}")
            
            # 确保有收盘价列（扩展列名列表）
            close_col = None
            for col in ['close', 'Close', '收盘价', '收盘', 'close_price']:
                if col in stock_data.columns:
                    close_col = col
                    break
            
            if close_col is None:
                print(f"文件 {csv_file} 中未找到收盘价列")
                continue
            
            print(f"找到收盘价列: {close_col}")
            
            # 按日期排序
            stock_data = stock_data.sort_values(by=date_col)
            
            # 返回需要的列
            result = stock_data[[date_col, close_col]].copy()
            result.columns = ['date', 'close']
            result['close'] = pd.to_numeric(result['close'], errors='coerce')
            result = result.dropna(subset=['close'])
            
            # 将日期列转换为整数（如果CSV中是YYYYMMDD格式的整数）
            # 同时支持字符串格式的日期
            try:
                result['date'] = pd.to_numeric(result['date'], errors='coerce').astype('Int64')
            except:
                # 如果转换失败，保持原样
                pass
            
            # 将输入的日期也转换为整数进行比较
            if start_date is not None:
                try:
                    start_int = int(start_date)
                    result = result[result['date'] >= start_int]
                except ValueError:
                    # 如果输入不是纯数字，使用字符串比较
                    result['date'] = result['date'].astype(str)
                    result = result[result['date'] >= str(start_date)]
            if end_date is not None:
                try:
                    end_int = int(end_date)
                    result = result[result['date'] <= end_int]
                except ValueError:
                    result['date'] = result['date'].astype(str)
                    result = result[result['date'] <= str(end_date)]
            
            if result.empty:
                print(f"日期范围过滤后无数据")
                continue
            
            print(f"最终加载 {len(result)} 条数据")
            return result
            
        except Exception as e:
            print(f"读取 {csv_file} 时出错: {e}")
            continue
    
    return None

def calculate_ma(data, window):
    """计算移动平均线"""
    return data['close'].rolling(window=window).mean()

def backtest_ma_cross(data, ma1_window, ma2_window):
    """对指定MA参数组合进行回测"""
    if len(data) < max(ma1_window, ma2_window) + 2:
        return None
    
    # 计算MA
    ma1 = calculate_ma(data, ma1_window)
    ma2 = calculate_ma(data, ma2_window)
    
    # 生成信号
    # 1: 买入（MA1上穿MA2）
    # -1: 卖出（MA1下穿MA2）
    # 0: 无操作
    signals = pd.Series(0, index=data.index)
    
    for i in range(1, len(data)):
        if pd.isna(ma1.iloc[i]) or pd.isna(ma2.iloc[i]):
            continue
        if pd.isna(ma1.iloc[i-1]) or pd.isna(ma2.iloc[i-1]):
            continue
        
        # 上穿
        if ma1.iloc[i-1] <= ma2.iloc[i-1] and ma1.iloc[i] > ma2.iloc[i]:
            signals.iloc[i] = 1
        # 下穿
        elif ma1.iloc[i-1] >= ma2.iloc[i-1] and ma1.iloc[i] < ma2.iloc[i]:
            signals.iloc[i] = -1
    
    # 执行回测
    position = 0  # 0: 空仓, 1: 持仓
    entry_price = 0
    total_return = 1.0  # 初始资金为1
    trades = 0
    
    for i in range(len(data)):
        if signals.iloc[i] == 1 and position == 0:
            # 买入
            position = 1
            entry_price = data['close'].iloc[i]
            trades += 1
        elif signals.iloc[i] == -1 and position == 1:
            # 卖出
            position = 0
            exit_price = data['close'].iloc[i]
            if entry_price > 0:
                total_return *= (exit_price / entry_price)
            entry_price = 0
    
    # 如果最后还持仓，按最后价格平仓
    if position == 1 and entry_price > 0:
        total_return *= (data['close'].iloc[-1] / entry_price)
    
    # 计算收益率
    if trades > 0:
        return_rate = (total_return - 1) * 100
    else:
        return_rate = 0
    
    return {
        'ma1': ma1_window,
        'ma2': ma2_window,
        'trades': trades,
        'return_rate': return_rate
    }

def find_best_parameters(data):
    """寻找最优MA参数组合"""
    ma1_options = [3, 5, 7]
    ma2_options = [10, 14, 20]
    
    results = []
    
    for ma1 in ma1_options:
        for ma2 in ma2_options:
            if ma1 >= ma2:
                continue  # 短周期必须小于长周期
            
            result = backtest_ma_cross(data, ma1, ma2)
            if result is not None:
                results.append(result)
    
    if not results:
        return None
    
    # 按收益率排序
    results.sort(key=lambda x: x['return_rate'], reverse=True)
    
    return results

def save_results_to_md(symbol, all_results, best_result, output_file, start_date=None, end_date=None):
    """将结果保存为Markdown文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 股票 {symbol} MA交叉策略回测结果\n\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 显示时间段信息
        if start_date and end_date:
            f.write(f"**回测时间段**: {start_date} 至 {end_date}\n\n")
        elif start_date:
            f.write(f"**回测起始日期**: {start_date}\n\n")
        elif end_date:
            f.write(f"**回测结束日期**: {end_date}\n\n")
        else:
            f.write("**回测时间段**: 全部可用数据\n\n")
        
        f.write("## 参数说明\n\n")
        f.write("- MA1（短周期）: 3, 5, 7\n")
        f.write("- MA2（长周期）: 10, 14, 20\n")
        f.write("- 买入条件：MA1 上穿 MA2\n")
        f.write("- 卖出条件：MA1 下穿 MA2\n\n")
        
        f.write("## 所有参数组合回测结果\n\n")
        f.write("| MA1 | MA2 | 交易次数 | 收益率(%) |\n")
        f.write("|-----|-----|----------|----------|\n")
        
        for result in all_results:
            f.write(f"| {result['ma1']} | {result['ma2']} | {result['trades']} | {result['return_rate']:.2f} |\n")
        
        f.write("\n## 最优参数\n\n")
        f.write(f"- **MA1**: {best_result['ma1']}\n")
        f.write(f"- **MA2**: {best_result['ma2']}\n")
        f.write(f"- **交易次数**: {best_result['trades']}\n")
        f.write(f"- **收益率**: {best_result['return_rate']:.2f}%\n\n")
        
        f.write("---\n")
        f.write("*由 stock-shai2604.py 自动生成*\n")

def main():
    print("=" * 60)
    print("股票MA交叉策略回测工具（支持指定时间段）")
    print("=" * 60)
    
    # 输入股票代码
    symbol = input("请输入股票代码（例如 000001 或 600000）: ").strip()
    
    if not symbol:
        print("股票代码不能为空！")
        return
    
    # 输入时间段
    start_date = input("请输入起始日期（格式YYYYMMDD，直接回车表示不限）: ").strip()
    end_date = input("请输入结束日期（格式YYYYMMDD，直接回车表示不限）: ").strip()
    
    # 如果输入为空则设为None
    if not start_date:
        start_date = None
    if not end_date:
        end_date = None
    
    print(f"\n正在加载股票 {symbol} 的数据...")
    
    # 检查CSV文件是否存在
    csv_files = [
        r"e:\stockdatasz.csv",
        r"e:\stockdatash.csv",
        r"e:\stockdataother.csv"
    ]
    
    found_any_file = False
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            found_any_file = True
            print(f"找到文件: {csv_file}")
        else:
            print(f"文件不存在: {csv_file}")
    
    if not found_any_file:
        print("错误：未找到任何CSV数据文件，请检查文件路径。")
        return
    
    # 加载数据（支持日期范围过滤）
    try:
        data = load_stock_data(symbol, start_date, end_date)
    except Exception as e:
        print(f"加载数据时发生异常: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if data is None or data.empty:
        print(f"未找到股票 {symbol} 的数据，请检查CSV文件是否存在且包含该股票。")
        print("提示：请确认CSV文件中包含股票代码列（如 symbol、code、ts_code、股票代码、stock_code、代码）")
        print("提示：请确认CSV文件中包含日期列（如 date、trade_date、日期、交易日期、datetime）")
        print("提示：请确认CSV文件中包含收盘价列（如 close、Close、收盘价、收盘、close_price）")
        return
    
    print(f"成功加载 {len(data)} 条数据记录")
    print(f"数据范围：{data['date'].iloc[0]} 至 {data['date'].iloc[-1]}")
    
    print("\n正在回测所有MA参数组合...")
    
    # 寻找最优参数
    try:
        all_results = find_best_parameters(data)
    except Exception as e:
        print(f"回测时发生异常: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if all_results is None or len(all_results) == 0:
        print("回测失败，数据不足或无法生成有效信号。")
        return
    
    best_result = all_results[0]
    
    print(f"\n{'='*60}")
    print("回测结果")
    print(f"{'='*60}")
    print(f"{'MA1':<6} {'MA2':<6} {'交易次数':<10} {'收益率(%)':<10}")
    print("-" * 40)
    
    for result in all_results:
        print(f"{result['ma1']:<6} {result['ma2']:<6} {result['trades']:<10} {result['return_rate']:<10.2f}")
    
    print(f"\n{'='*60}")
    print("最优参数")
    print(f"{'='*60}")
    print(f"MA1: {best_result['ma1']}")
    print(f"MA2: {best_result['ma2']}")
    print(f"交易次数: {best_result['trades']}")
    print(f"收益率: {best_result['return_rate']:.2f}%")
    
    # 保存结果
    output_file = r"E:\shai202604.md"
    try:
        save_results_to_md(symbol, all_results, best_result, output_file, start_date, end_date)
        print(f"\n结果已保存到: {output_file}")
    except Exception as e:
        print(f"保存结果时发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
