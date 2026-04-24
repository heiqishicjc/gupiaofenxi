#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指定个股数据回测工具
策略：MA5上穿MA10买入，MA5下穿MA10卖出
数据来源：e:\\stockdatasz.csv 或 e:\\stockdatash.csv
结果输出：huicejieguo.md

用法：
    python newAstockbacktrade.py [股票代码]
    若不指定股票代码，则默认回测 002594.SZ（比亚迪）。
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# ========== 配置 ==========
DATA_DIR = r"e:"
SZ_FILE = os.path.join(DATA_DIR, "stockdatasz.csv")
SH_FILE = os.path.join(DATA_DIR, "stockdatash.csv")
OUTPUT_FILE = "huicejieguo.md"

# ========== 数据读取 ==========
def load_data():
    """尝试读取 sz 文件，若不存在则读取 sh 文件"""
    if os.path.exists(SZ_FILE):
        print(f"读取深市数据: {SZ_FILE}")
        df = pd.read_csv(SZ_FILE, encoding="utf-8-sig")
    elif os.path.exists(SH_FILE):
        print(f"读取沪市数据: {SH_FILE}")
        df = pd.read_csv(SH_FILE, encoding="utf-8-sig")
    else:
        print("错误：未找到 stockdatasz.csv 或 stockdatash.csv")
        sys.exit(1)
    return df

def preprocess_data(df):
    """数据预处理：统一列名、排序、计算均线"""
    # 统一列名（常见中英文）
    rename_map = {
        "股票代码": "symbol",
        "代码": "symbol",
        "ts_code": "symbol",
        "日期": "date",
        "trade_date": "date",
        "开盘": "open",
        "开盘价": "open",
        "open": "open",
        "收盘": "close",
        "收盘价": "close",
        "close": "close",
        "最高": "high",
        "最高价": "high",
        "high": "high",
        "最低": "low",
        "最低价": "low",
        "low": "low",
        "成交量": "volume",
        "成交额": "amount",
        "vol": "volume",
        "amount": "amount",
    }
    df.rename(columns=rename_map, inplace=True)

    # 确保必要列存在
    required = ["symbol", "date", "close"]
    for col in required:
        if col not in df.columns:
            print(f"错误：数据中缺少必要列 '{col}'")
            sys.exit(1)

    # 日期转换
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(subset=["date"], inplace=True)

    # 按股票代码和日期排序
    df.sort_values(["symbol", "date"], inplace=True)

    # 计算 MA5 和 MA10
    df["MA5"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )
    df["MA10"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(window=10, min_periods=1).mean()
    )

    return df

def generate_signals(df):
    """生成买入/卖出信号"""
    # 上穿：前一日 MA5 <= MA10 且 当日 MA5 > MA10
    df["prev_MA5"] = df.groupby("symbol")["MA5"].shift(1)
    df["prev_MA10"] = df.groupby("symbol")["MA10"].shift(1)

    df["buy_signal"] = (df["prev_MA5"] <= df["prev_MA10"]) & (df["MA5"] > df["MA10"])
    df["sell_signal"] = (df["prev_MA5"] >= df["prev_MA10"]) & (df["MA5"] < df["MA10"])

    return df

def backtest_single_stock(df_stock):
    """对单只股票进行回测，返回交易记录和绩效"""
    trades = []
    position = 0          # 持仓数量
    cash = 100000         # 初始资金
    buy_price = 0.0
    buy_date = None

    for idx, row in df_stock.iterrows():
        price = row["close"]
        date = row["date"]

        if row["buy_signal"] and position == 0:
            # 买入
            position = cash / price
            cash = 0.0
            buy_price = price
            buy_date = date
            trades.append({
                "date": date,
                "action": "买入",
                "price": price,
                "shares": position,
                "cash_after": cash,
            })
        elif row["sell_signal"] and position > 0:
            # 卖出
            cash = position * price
            position = 0.0
            trades.append({
                "date": date,
                "action": "卖出",
                "price": price,
                "shares": 0,
                "cash_after": cash,
            })

    # 最终平仓（若仍持仓）
    if position > 0:
        last_price = df_stock.iloc[-1]["close"]
        cash = position * last_price
        position = 0.0
        trades.append({
            "date": df_stock.iloc[-1]["date"],
            "action": "强制平仓",
            "price": last_price,
            "shares": 0,
            "cash_after": cash,
        })

    # 计算绩效
    total_return = cash - 100000
    return_rate = (cash / 100000 - 1) * 100

    # 最大回撤（基于每日净值）
    df_stock = df_stock.copy()
    df_stock["net_value"] = np.nan
    # 简化：用收盘价模拟净值（实际需考虑持仓）
    # 此处仅用收盘价序列计算最大回撤
    peak = df_stock["close"].cummax()
    drawdown = (df_stock["close"] - peak) / peak * 100
    max_drawdown = drawdown.min()

    # 交易次数
    trade_count = len([t for t in trades if t["action"] in ("买入", "卖出")])

    return {
        "trades": trades,
        "total_return": total_return,
        "return_rate": return_rate,
        "max_drawdown": max_drawdown,
        "trade_count": trade_count,
        "final_cash": cash,
    }

def run_backtest(df, symbol=None):
    """对指定股票或所有股票执行回测"""
    results = {}
    if symbol:
        # 只回测指定股票
        symbols = [symbol]
        print(f"回测指定股票: {symbol}")
    else:
        symbols = df["symbol"].unique()
        print(f"共发现 {len(symbols)} 只股票，开始回测...")

    for sym in symbols:
        df_stock = df[df["symbol"] == sym].copy()
        if len(df_stock) < 15:  # 至少需要15个交易日
            if symbol:
                print(f"警告：股票 {sym} 数据不足15个交易日，跳过")
            continue
        result = backtest_single_stock(df_stock)
        results[sym] = result

    return results

def generate_markdown(results):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 个股回测报告（MA5上穿MA10买入 / MA5下穿MA10卖出）")
    lines.append("")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 汇总统计
    total_stocks = len(results)
    win_stocks = sum(1 for r in results.values() if r["return_rate"] > 0)
    avg_return = np.mean([r["return_rate"] for r in results.values()]) if results else 0
    avg_trades = np.mean([r["trade_count"] for r in results.values()]) if results else 0

    lines.append("## 总体统计")
    lines.append("")
    lines.append(f"- 回测股票数量：{total_stocks}")
    if total_stocks > 0:
        lines.append(f"- 盈利股票数量：{win_stocks}（{win_stocks/total_stocks*100:.1f}%）")
    else:
        lines.append("- 盈利股票数量：0")
    lines.append(f"- 平均收益率：{avg_return:.2f}%")
    lines.append(f"- 平均交易次数：{avg_trades:.1f}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 按收益率排序
    sorted_symbols = sorted(results.keys(), key=lambda s: results[s]["return_rate"], reverse=True)

    for sym in sorted_symbols:
        r = results[sym]
        lines.append(f"## {sym}")
        lines.append("")
        lines.append(f"- 最终资金：{r['final_cash']:.2f}")
        lines.append(f"- 总收益：{r['total_return']:.2f}（{r['return_rate']:.2f}%）")
        lines.append(f"- 最大回撤：{r['max_drawdown']:.2f}%")
        lines.append(f"- 交易次数：{r['trade_count']}")
        lines.append("")
        lines.append("### 交易明细")
        lines.append("")
        lines.append("| 日期 | 操作 | 价格 | 持仓 | 现金余额 |")
        lines.append("|------|------|------|------|----------|")
        for t in r["trades"]:
            date_str = t["date"].strftime("%Y-%m-%d") if hasattr(t["date"], "strftime") else str(t["date"])
            lines.append(f"| {date_str} | {t['action']} | {t['price']:.2f} | {t['shares']:.2f} | {t['cash_after']:.2f} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def main():
    print("=" * 60)
    print("个股回测工具（MA5/MA10 金叉死叉策略）")
    print("=" * 60)

    # 解析命令行参数，默认回测 002594.SZ（比亚迪）
    symbol = "002594.SZ"
    if len(sys.argv) > 1:
        symbol = sys.argv[1].strip()
        print(f"指定股票代码: {symbol}")
    else:
        print(f"未指定股票代码，默认回测: {symbol}")

    # 1. 加载数据
    df = load_data()
    print(f"原始数据行数：{len(df)}")

    # 2. 预处理
    df = preprocess_data(df)
    print(f"预处理后行数：{len(df)}")

    # 3. 生成信号
    df = generate_signals(df)

    # 4. 回测
    results = run_backtest(df, symbol)

    # 5. 生成报告
    md_content = generate_markdown(results)

    # 6. 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n报告已保存至：{OUTPUT_FILE}")
    print("完成！")

if __name__ == "__main__":
    main()
