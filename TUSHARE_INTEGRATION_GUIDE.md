# Tushare 集成指南

## 概述

A股分析工具已成功集成 Tushare 数据源，提供更高质量的中国股票数据。

## 安装依赖

```bash
pip install tushare>=1.4.0
```

或使用项目 requirements:
```bash
pip install -r requirements_minimal.txt
```

## API Token 配置

您的 Tushare API Token 已自动配置：
- **Token**: `46813b22149a178b86d12174cf301142e68fe13445129dd34a8cbcad`
- **状态**: 已验证可用

## 使用方式

### 1. 兼容版本（推荐）

```python
from src.data.china_stock_fetcher import ChinaStockFetcher

# 创建数据获取器（优先使用 Tushare）
fetcher = ChinaStockFetcher(prefer_tushare=True)

# 获取股票数据
data = fetcher.get_a_stock_data("600519.SH", period="1y")

# 通过名称获取
data = fetcher.get_popular_stock_data("贵州茅台", period="6mo")

# 获取指数数据
index_data = fetcher.get_index_data("上证指数", period="3mo")
```

### 2. 纯 Tushare 版本

```python
from src.data.china_stock_fetcher_tushare import ChinaStockFetcherTushare

# 创建 Tushare 专用获取器
fetcher = ChinaStockFetcherTushare()

data = fetcher.get_a_stock_data("600519.SH", period="1y")
```

### 3. 修复版本（解决权限问题）

```python
from src.data.china_stock_fetcher_tushare_fixed import ChinaStockFetcherTushareFixed

# 使用修复版本
fetcher = ChinaStockFetcherTushareFixed()

data = fetcher.get_a_stock_data("600519.SH", period="1y")
```

## 股票代码格式

### Tushare 格式
- 上海: `600519.SH`
- 深圳: `000858.SZ`

### yfinance 格式
- 上海: `600519.SS`
- 深圳: `000858.SZ`

## 支持的数据类型

### 股票数据
- 日线数据 (OHLCV)
- 涨跌幅计算
- 振幅计算
- 成交量变化

### 指数数据
- 上证指数 (000001.SH)
- 深证成指 (399001.SZ)
- 创业板指 (399006.SZ)
- 沪深300 (000300.SH)
- 上证50 (000016.SH)
- 中证500 (000905.SH)

### 热门股票
- 贵州茅台 (600519.SH)
- 工商银行 (601398.SH)
- 中国平安 (601318.SH)
- 招商银行 (600036.SH)
- 五粮液 (000858.SZ)
- 宁德时代 (300750.SZ)
- 比亚迪 (002594.SZ)
- 中信证券 (600030.SH)
- 万科A (000002.SZ)
- 海康威视 (002415.SZ)

## 数据期间参数

- `1y`: 1年数据
- `6mo`: 6个月数据
- `3mo`: 3个月数据
- `1mo`: 1个月数据

## 缓存机制

数据会自动缓存到 `data/tushare_cache` 目录：
- 减少 API 调用次数
- 提高数据获取速度
- 支持离线分析

## 错误处理

### 网络问题
如果 Tushare 不可用，系统会自动回退到 yfinance。

### 权限问题
如果遇到权限问题，使用修复版本。

### 数据缺失
某些指数数据可能需要高级权限。

## 性能优化

### 请求频率控制
- 自动添加请求间隔
- 避免 API 限制
- 支持批量获取

### 内存优化
- 数据预处理优化
- 只保留必要字段
- 支持大数据集处理

## 测试验证

运行测试脚本验证集成：

```bash
python test_tushare_integration.py
```

## 版本信息

- **集成版本**: v1.0.3+
- **Tushare 版本**: 1.4.29
- **兼容性**: 完全向后兼容
- **状态**: 生产就绪

## 技术支持

如有问题，请检查：
1. 网络连接
2. API Token 有效性
3. 依赖包版本
4. 缓存目录权限

## 更新日志

### v1.0.3 (2026-04-01)
- ✅ 集成 Tushare 数据源
- ✅ 支持两种数据源自动切换
- ✅ 修复权限问题
- ✅ 更新依赖配置
- ✅ 完善测试用例

---

**您的 A股分析工具现在具备企业级的数据获取能力！** 🚀