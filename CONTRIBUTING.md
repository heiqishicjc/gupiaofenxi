# 贡献指南

欢迎为 A股股票分析工具 项目贡献代码！

## 开发环境设置

1. 克隆仓库
```bash
git clone https://github.com/yourusername/gupiaofenxi.git
cd gupiaofenxi
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements_minimal.txt
```

## 代码规范

- 使用 Python 3.8+ 语法
- 遵循 PEP 8 代码风格
- 为函数和类添加文档字符串
- 使用有意义的变量名

## 提交代码

1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

2. 提交更改
```bash
git add .
git commit -m "描述你的更改"
```

3. 推送分支
```bash
git push origin feature/your-feature-name
```

4. 创建 Pull Request

## 测试

在提交代码前，请确保通过所有测试：
```bash
python -m pytest tests/ -v
```

## 报告问题

如果发现 bug 或有功能建议，请在 Issues 中创建新问题。