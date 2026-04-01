# A股股票分析工具 (A-Share Stock Analysis Tool)

一个专门针对中国A股市场的Python数据分析工具，提供A股数据获取、技术指标计算和可视化功能。

## 功能特性

### 🎯 A股特色功能
- **A股数据获取**: 支持上海、深圳交易所股票及主要指数
- **A股特有指标**: 乖离率(BIAS)、心理线(PSY)、威廉指标(W%R)等
- **热门A股分析**: 内置贵州茅台、宁德时代等热门股票
- **指数分析**: 上证指数、深证成指、创业板指等主要指数

### 📊 通用功能
- 技术指标计算（移动平均线、RSI、MACD、布林带等）
- 数据可视化（价格图表、K线图、指标图表）
- 数据预处理和清洗
- 多股票对比分析

## 项目结构

```
gupiaofenxi/
├── src/                    # 源代码目录
│   ├── data/              # 数据获取模块
│   │   ├── data_fetcher.py        # 通用数据获取
│   │   └── china_stock_fetcher.py # A股专用数据获取
│   ├── indicators/        # 技术指标模块
│   ├── visualization/    # 可视化模块
│   └── utils/            # 工具函数
├── tests/                 # 测试文件
├── data/                  # 数据存储目录
├── docs/                  # 文档
├── requirements.txt       # Python依赖
├── main.py               # 主程序入口
└── test_a_stock.py       # A股功能测试
```

## 快速开始

### 1. 环境设置
```bash
# 创建虚拟环境
py -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements_minimal.txt
```

### 2. 运行分析工具
```bash
python main.py
```

### 3. 测试功能
```bash
python test_a_stock.py
```

## A股代码格式

### 股票代码
- **上海证券交易所**: `600036.SS` (招商银行)
- **深圳证券交易所**: `000001.SZ` (平安银行)  
- **创业板**: `300750.SZ` (宁德时代)
- **科创板**: `688001.SS` (华兴源创)

### 主要指数
- `000001.SS` - 上证指数
- `399001.SZ` - 深证成指
- `399006.SZ` - 创业板指
- `000300.SS` - 沪深300
- `000016.SS` - 上证50

## 使用示例

### 分析单只A股
```python
from src.data.china_stock_fetcher import ChinaStockFetcher

fetcher = ChinaStockFetcher()

# 获取贵州茅台数据
data = fetcher.get_a_stock_data('600519.SS', period='1y')

# 计算A股特有指标
data = fetcher.calculate_a_stock_metrics(data)

print(f"最新收盘价: {data['Close'].iloc[-1]:.2f}")
print(f"乖离率: {data['BIAS20'].iloc[-1]:.2f}%")
```

### 分析指数
```python
# 获取上证指数数据
index_data = fetcher.get_index_data('上证指数', period='6mo')
```

### 查看热门股票
```python
fetcher = ChinaStockFetcher()

print("热门A股:")
for name, symbol in fetcher.POPULAR_STOCKS.items():
    print(f"{name}: {symbol}")
```

## 技术栈

- **Python 3.8+**: 核心编程语言
- **pandas**: 数据处理和分析
- **numpy**: 数值计算
- **matplotlib**: 数据可视化
- **yfinance**: 股票数据获取（支持A股）

## 支持的A股指标

### 通用技术指标
- 移动平均线 (MA5, MA10, MA20, MA60)
- 相对强弱指数 (RSI)
- 移动平均收敛散度 (MACD)
- 布林带 (Bollinger Bands)
- 随机指标 (Stochastic)

### A股特有指标
- **乖离率 (BIAS)**: 股价与移动平均线的偏离程度
- **心理线 (PSY)**: 投资者心理预期指标
- **威廉指标 (W%R)**: 超买超卖指标
- **振幅**: 当日价格波动幅度

## 数据源

本项目使用 **yfinance** 库获取A股数据，该库通过Yahoo Finance API提供全球股票数据，包括中国A股市场。

## 注意事项

1. **数据延迟**: 免费数据源可能存在15分钟延迟
2. **网络连接**: 需要稳定的网络连接获取实时数据
3. **数据缓存**: 项目会自动缓存数据以减少API调用
4. **使用限制**: 请遵守数据提供商的使用条款

## 开发计划

- [ ] 添加更多A股数据源（腾讯财经、新浪财经等）
- [ ] 实现A股财务数据分析
- [ ] 添加A股板块分析功能
- [ ] 开发Web界面
- [ ] 支持实时数据推送

## 贡献

欢迎提交Issue和Pull Request来改进这个A股分析工具！