#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股回测系统 - 基于 stockdata.csv 数据样品
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class StockBacktester:
    """个股回测系统"""
    
    def __init__(self, data_file='stockdata.csv', initial_capital=100000.0):
        """
        初始化回测系统
        
        参数:
        data_file: 数据文件路径 (默认: 'stockdata.csv')
        initial_capital: 初始资金 (默认: 100000.0)
        """
        self.data_file = data_file
        self.initial_capital = initial_capital
        self.data = None
        self.signals = None
        self.positions = None
        self.portfolio = None
        
        # 尝试读取数据
        self.load_data()
        
    def load_data(self):
        """加载股票数据"""
        try:
            # 尝试读取CSV文件
            self.data = pd.read_csv(self.data_file)
            
            # 确保日期列是datetime类型
            if 'date' in self.data.columns:
                self.data['date'] = pd.to_datetime(self.data['date'])
                self.data.set_index('date', inplace=True)
            elif 'Date' in self.data.columns:
                self.data['Date'] = pd.to_datetime(self.data['Date'])
                self.data.set_index('Date', inplace=True)
            elif 'datetime' in self.data.columns:
                self.data['datetime'] = pd.to_datetime(self.data['datetime'])
                self.data.set_index('datetime', inplace=True)
            
            # 确保有价格数据列
            # 尝试常见的列名
            price_columns = ['close', 'Close', 'CLOSE', 'price', 'Price']
            for col in price_columns:
                if col in self.data.columns:
                    self.data['price'] = self.data[col]
                    break
            
            # 如果没有找到价格列，使用第一列数值数据
            if 'price' not in self.data.columns:
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    self.data['price'] = self.data[numeric_cols[0]]
                else:
                    raise ValueError("无法找到价格数据列")
            
            print(f"数据加载成功！共 {len(self.data)} 条记录")
            print(f"数据时间范围: {self.data.index[0]} 到 {self.data.index[-1]}")
            
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{self.data_file}'")
            print("请确保 stockdata.csv 文件存在，或提供正确的文件路径")
            # 创建示例数据用于演示
            self.create_sample_data()
        except Exception as e:
            print(f"加载数据时出错: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """创建示例数据（当没有真实数据时使用）"""
        print("创建示例数据用于演示...")
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # 生成随机价格数据
        price = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        
        self.data = pd.DataFrame({
            'open': price * (1 + np.random.randn(len(dates)) * 0.01),
            'high': price * (1 + np.abs(np.random.randn(len(dates)) * 0.02)),
            'low': price * (1 - np.abs(np.random.randn(len(dates)) * 0.02)),
            'close': price,
            'volume': np.random.randint(1000, 10000, len(dates))
        }, index=dates)
        
        self.data['price'] = self.data['close']
        print(f"示例数据创建完成！共 {len(self.data)} 条记录")
    
    def calculate_indicators(self):
        """计算技术指标"""
        if self.data is None:
            print("错误: 没有数据可用")
            return
        
        # 计算移动平均线
        self.data['sma_20'] = self.data['price'].rolling(window=20).mean()
        self.data['sma_50'] = self.data['price'].rolling(window=50).mean()
        
        # 计算RSI
        delta = self.data['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        
        # 计算MACD
        exp1 = self.data['price'].ewm(span=12, adjust=False).mean()
        exp2 = self.data['price'].ewm(span=26, adjust=False).mean()
        self.data['macd'] = exp1 - exp2
        self.data['macd_signal'] = self.data['macd'].ewm(span=9, adjust=False).mean()
        
        # 计算布林带
        self.data['bb_middle'] = self.data['price'].rolling(window=20).mean()
        bb_std = self.data['price'].rolling(window=20).std()
        self.data['bb_upper'] = self.data['bb_middle'] + (bb_std * 2)
        self.data['bb_lower'] = self.data['bb_middle'] - (bb_std * 2)
        
        print("技术指标计算完成！")
    
    def generate_signals(self, strategy='dual_sma'):
        """
        生成交易信号
        
        参数:
        strategy: 交易策略 (默认: 'dual_sma')
            - 'dual_sma': 双移动平均线策略
            - 'mean_reversion': 均值回归策略
            - 'rsi': RSI超买超卖策略
        """
        if self.data is None:
            print("错误: 没有数据可用")
            return
        
        # 确保已计算指标
        if 'sma_20' not in self.data.columns:
            self.calculate_indicators()
        
        # 创建信号DataFrame
        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['price'] = self.data['price']
        
        # 初始化信号列
        self.signals['signal'] = 0
        
        if strategy == 'dual_sma':
            # 双移动平均线策略：短期均线上穿长期均线时买入，下穿时卖出
            # 使用loc避免链式赋值警告
            self.signals.loc[self.data['sma_20'] > self.data['sma_50'], 'signal'] = 1
            self.signals.loc[self.data['sma_20'] <= self.data['sma_50'], 'signal'] = 0
            
        elif strategy == 'mean_reversion':
            # 均值回归策略：价格低于布林带下轨时买入，高于上轨时卖出
            self.signals.loc[self.data['price'] < self.data['bb_lower'], 'signal'] = 1
            self.signals.loc[self.data['price'] > self.data['bb_upper'], 'signal'] = 0
            
        elif strategy == 'rsi':
            # RSI策略：RSI低于30时买入，高于70时卖出
            self.signals.loc[self.data['rsi'] < 30, 'signal'] = 1
            self.signals.loc[self.data['rsi'] > 70, 'signal'] = 0
            
        elif strategy == 'macd_crossover':
            # MACD金叉死叉策略：MACD上穿信号线时买入，下穿时卖出
            # 确保MACD指标已计算
            if 'macd' not in self.data.columns:
                self.calculate_indicators()
            # 金叉：MACD > MACD信号线
            self.signals.loc[self.data['macd'] > self.data['macd_signal'], 'signal'] = 1
            # 死叉：MACD <= MACD信号线
            self.signals.loc[self.data['macd'] <= self.data['macd_signal'], 'signal'] = 0
            
        else:
            print(f"未知策略: {strategy}，使用默认双移动平均线策略")
            self.signals.loc[self.data['sma_20'] > self.data['sma_50'], 'signal'] = 1
            self.signals.loc[self.data['sma_20'] <= self.data['sma_50'], 'signal'] = 0
        
        # 计算持仓变化（信号从0变为1时买入，从1变为0时卖出）
        self.signals['positions'] = self.signals['signal'].diff()
        
        print(f"交易信号生成完成！策略: {strategy}")
        print(f"买入信号数量: {len(self.signals[self.signals['positions'] == 1])}")
        print(f"卖出信号数量: {len(self.signals[self.signals['positions'] == -1])}")
    
    def backtest(self, commission=0.001):
        """
        执行回测
        
        参数:
        commission: 交易佣金比例 (默认: 0.001 = 0.1%)
        """
        if self.signals is None:
            print("错误: 没有交易信号可用")
            return
        
        # 初始化回测数据
        self.portfolio = pd.DataFrame(index=self.signals.index)
        self.portfolio['price'] = self.signals['price']
        self.portfolio['signal'] = self.signals['signal']
        self.portfolio['positions'] = self.signals['positions']
        
        # 初始化持仓和现金
        self.portfolio['holdings'] = 0  # 持仓数量
        self.portfolio['cash'] = self.initial_capital  # 现金
        self.portfolio['total'] = self.initial_capital  # 总资产
        
        holdings = 0
        cash = self.initial_capital
        
        # 使用列表收集数据，避免在循环中直接修改DataFrame
        holdings_list = []
        cash_list = []
        total_list = []
        
        for i in range(len(self.portfolio)):
            price = self.portfolio['price'].iloc[i]
            position_change = self.portfolio['positions'].iloc[i]
            
            # 买入信号
            if position_change == 1 and cash > price:
                # 计算可买入数量（全部买入）
                shares_to_buy = cash // price
                if shares_to_buy > 0:
                    cost = shares_to_buy * price * (1 + commission)
                    if cost <= cash:
                        holdings += shares_to_buy
                        cash -= cost
            
            # 卖出信号
            elif position_change == -1 and holdings > 0:
                # 卖出全部持仓
                revenue = holdings * price * (1 - commission)
                holdings = 0
                cash += revenue
            
            # 收集每日数据
            holdings_list.append(holdings)
            cash_list.append(cash)
            total_list.append(cash + holdings * price)
        
        # 批量更新DataFrame列
        self.portfolio['holdings'] = holdings_list
        self.portfolio['cash'] = cash_list
        self.portfolio['total'] = total_list
        
        # 计算绩效指标
        self.calculate_performance()
        
        print("回测完成！")
    
    def calculate_performance(self):
        """计算回测绩效指标"""
        if self.portfolio is None:
            print("错误: 没有回测数据可用")
            return
        
        # 计算收益率
        self.portfolio['returns'] = self.portfolio['total'].pct_change()
        
        # 总收益率
        total_return = (self.portfolio['total'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # 年化收益率
        days = (self.portfolio.index[-1] - self.portfolio.index[0]).days
        years = days / 365.25
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 最大回撤
        cumulative = (1 + self.portfolio['returns']).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 夏普比率（假设无风险利率为0）
        excess_returns = self.portfolio['returns'].dropna()
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0
        
        # 计算胜率和盈亏比
        trade_returns = []
        in_trade = False
        entry_price = 0
        entry_index = 0
        
        for i in range(1, len(self.portfolio)):
            position_change = self.portfolio['positions'].iloc[i]
            current_price = self.portfolio['price'].iloc[i]
            
            if position_change == 1 and not in_trade:  # 买入
                in_trade = True
                entry_price = current_price
                entry_index = i
            elif position_change == -1 and in_trade:  # 卖出
                in_trade = False
                trade_return = (current_price - entry_price) / entry_price
                trade_returns.append(trade_return)
        
        # 如果有未平仓的交易，使用最后价格计算
        if in_trade and entry_index < len(self.portfolio) - 1:
            final_price = self.portfolio['price'].iloc[-1]
            trade_return = (final_price - entry_price) / entry_price
            trade_returns.append(trade_return)
        
        # 计算胜率、盈亏比等
        if trade_returns:
            winning_trades = [r for r in trade_returns if r > 0]
            losing_trades = [r for r in trade_returns if r <= 0]
            
            win_rate = len(winning_trades) / len(trade_returns) if trade_returns else 0
            
            avg_win = np.mean(winning_trades) if winning_trades else 0
            avg_loss = np.mean(losing_trades) if losing_trades else 0
            if avg_loss != 0:
                profit_factor = abs(avg_win / avg_loss)
                profit_factor_str = f"{profit_factor:.2f}"
            else:
                profit_factor = float('inf')
                profit_factor_str = "无限大"
        else:
            win_rate = 0
            profit_factor = 0
            profit_factor_str = "0.00"
            winning_trades = []
            losing_trades = []
        
        # 保存绩效指标
        self.performance = {
            '初始资金': self.initial_capital,
            '最终资产': self.portfolio['total'].iloc[-1],
            '总收益率': total_return,
            '年化收益率': annual_return,
            '最大回撤': max_drawdown,
            '夏普比率': sharpe_ratio,
            '胜率': win_rate,
            '盈亏比': profit_factor_str,
            '交易天数': days,
            '交易次数': len(self.portfolio[self.portfolio['positions'] != 0]),
            '盈利交易数': len(winning_trades),
            '亏损交易数': len(losing_trades)
        }
        
        print("\n" + "="*50)
        print("回测绩效报告")
        print("="*50)
        for key, value in self.performance.items():
            if isinstance(value, float):
                if '率' in key or '比率' in key or '胜率' in key:
                    print(f"{key}: {value:.2%}")
                elif '资金' in key or '资产' in key:
                    print(f"{key}: ￥{value:,.2f}")
                else:
                    print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        print("="*50)
    
    def save_results(self, filename='backtest_results.csv'):
        """保存回测结果到CSV文件"""
        if self.portfolio is None:
            print("错误: 没有回测数据可用")
            return
        
        try:
            # 保存投资组合数据
            self.portfolio.to_csv(filename)
            print(f"投资组合数据已保存到 '{filename}'")
            
            # 保存绩效指标
            perf_filename = 'performance_summary.csv'
            perf_df = pd.DataFrame([self.performance])
            perf_df.to_csv(perf_filename, index=False)
            print(f"绩效指标已保存到 '{perf_filename}'")
            
        except Exception as e:
            print(f"保存结果时出错: {e}")
    
    def plot_results(self):
        """绘制回测结果图表"""
        if self.portfolio is None:
            print("错误: 没有回测数据可用")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # 1. 价格和交易信号
        ax1 = axes[0]
        ax1.plot(self.portfolio.index, self.portfolio['price'], label='价格', linewidth=1)
        
        # 标记买入点
        buy_signals = self.portfolio[self.portfolio['positions'] == 1]
        if len(buy_signals) > 0:
            ax1.scatter(buy_signals.index, buy_signals['price'], 
                       color='green', marker='^', s=100, label='买入', alpha=0.7)
        
        # 标记卖出点
        sell_signals = self.portfolio[self.portfolio['positions'] == -1]
        if len(sell_signals) > 0:
            ax1.scatter(sell_signals.index, sell_signals['price'], 
                       color='red', marker='v', s=100, label='卖出', alpha=0.7)
        
        ax1.set_title('股票价格与交易信号')
        ax1.set_ylabel('价格')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 资产变化
        ax2 = axes[1]
        ax2.plot(self.portfolio.index, self.portfolio['total'], 
                label='总资产', color='blue', linewidth=2)
        ax2.axhline(y=self.initial_capital, color='red', linestyle='--', 
                   label=f'初始资金 (￥{self.initial_capital:,.0f})')
        ax2.set_title('资产变化曲线')
        ax2.set_ylabel('资产价值')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 持仓和现金
        ax3 = axes[2]
        ax3.plot(self.portfolio.index, self.portfolio['holdings'], 
                label='持仓数量', color='green', linewidth=1)
        ax3_twin = ax3.twinx()
        ax3_twin.plot(self.portfolio.index, self.portfolio['cash'], 
                     label='现金', color='orange', linewidth=1)
        ax3.set_title('持仓与现金')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('持仓数量')
        ax3_twin.set_ylabel('现金')
        
        # 合并图例
        lines1, labels1 = ax3.get_legend_handles_labels()
        lines2, labels2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('backtest_results.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("图表已保存为 'backtest_results.png'")

def main():
    """主函数"""
    print("个股回测系统 v1.1")
    print("="*50)
    
    # 创建回测实例
    backtester = StockBacktester(data_file='stockdata.csv', initial_capital=100000)
    
    # 计算技术指标
    backtester.calculate_indicators()
    
    # 选择策略并生成信号
    strategies = ['dual_sma', 'mean_reversion', 'rsi', 'macd_crossover']
    strategy_names = {
        'dual_sma': '双移动平均线策略',
        'mean_reversion': '均值回归策略',
        'rsi': 'RSI超买超卖策略',
        'macd_crossover': 'MACD金叉死叉策略'
    }
    
    print("\n可选策略:")
    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy_names[strategy]} ({strategy})")
    
    try:
        choice = int(input("\n请选择策略 (输入编号 1-4，默认1): ") or 1)
        if choice < 1 or choice > 4:
            choice = 1
    except:
        choice = 1
    
    selected_strategy = strategies[choice-1]
    
    # 生成交易信号
    backtester.generate_signals(strategy=selected_strategy)
    
    # 执行回测
    backtester.backtest(commission=0.001)
    
    # 保存结果
    backtester.save_results()
    
    # 显示结果
    backtester.plot_results()
    
    print("\n回测完成！详细结果已保存。")
    print("生成的文件:")
    print("  - backtest_results.csv: 投资组合每日数据")
    print("  - performance_summary.csv: 绩效指标汇总")
    print("  - backtest_results.png: 回测图表")

if __name__ == "__main__":
    main()
