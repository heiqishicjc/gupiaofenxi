# GitHub 上传指南

本指南将帮助您将 A股股票分析工具 项目上传到 GitHub。

## 📋 准备工作

### 1. 检查 Git 配置
确保 Git 已正确配置您的用户名和邮箱：

```bash
git config --global user.name "您的GitHub用户名"
git config --global user.email "您的GitHub邮箱"
```

### 2. GitHub 账户准备
- 确保您有 GitHub 账户
- 记住您的 GitHub 用户名和密码（或访问令牌）

## 🚀 上传步骤

### 步骤 1: 初始化 Git 仓库

在项目根目录执行：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件到暂存区
git add .

# 创建初始提交
git commit -m "初始提交: A股股票分析工具 v1.0"
```

### 步骤 2: 在 GitHub 创建新仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - **Repository name**: `gupiaofenxi` (或您喜欢的名称)
   - **Description**: "A股股票分析工具 - Python-based stock analysis tool for Chinese A-share market"
   - **Visibility**: Public (推荐) 或 Private
   - **Initialize this repository with**: 不要勾选任何选项

### 步骤 3: 连接到远程仓库

复制 GitHub 提供的命令，类似：

```bash
# 添加远程仓库
git remote add origin https://github.com/您的用户名/gupiaofenxi.git

# 验证远程仓库
git remote -v
```

### 步骤 4: 推送代码到 GitHub

```bash
# 推送代码到 GitHub
git push -u origin main

# 如果遇到错误，可能需要设置上游分支
git branch -M main
git push -u origin main
```

## 🔐 认证方式

### 方式 1: 个人访问令牌 (推荐)

1. 在 GitHub 设置中生成 Personal Access Token
2. 使用令牌代替密码：

```bash
git push -u origin main
# 用户名: 您的GitHub用户名
# 密码: 您的访问令牌
```

### 方式 2: SSH 密钥

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 将公钥添加到 GitHub
cat ~/.ssh/id_ed25519.pub
# 复制输出内容到 GitHub SSH keys 设置

# 使用 SSH 地址添加远程仓库
git remote set-url origin git@github.com:您的用户名/gupiaofenxi.git
```

## 📁 项目文件结构说明

```
gupiaofenxi/
├── .github/workflows/     # GitHub Actions 自动化
├── src/                   # 源代码
│   ├── data/             # 数据获取模块
│   ├── indicators/       # 技术指标模块
│   ├── visualization/    # 可视化模块
│   └── utils/           # 工具函数
├── tests/                # 测试文件
├── docs/                # 文档
├── data/                # 数据目录 (在.gitignore中)
├── venv/                # 虚拟环境 (在.gitignore中)
├── requirements.txt     # 完整依赖
├── requirements_minimal.txt # 最小依赖
├── main.py              # 主程序
├── setup.py            # 打包配置
├── README.md           # 项目说明
├── CONTRIBUTING.md     # 贡献指南
└── .gitignore          # Git忽略文件
```

## 🛠️ 常见问题解决

### 问题 1: 推送被拒绝
```bash
# 如果远程仓库有文件，需要先拉取
git pull origin main --allow-unrelated-histories
# 然后再次推送
git push -u origin main
```

### 问题 2: 认证失败
- 检查用户名和密码/令牌是否正确
- 如果是 2FA 用户，必须使用访问令牌

### 问题 3: 大文件上传
如果遇到大文件问题，可以安装 Git LFS：
```bash
git lfs install
git lfs track "*.csv"
git add .gitattributes
git add .
git commit -m "添加 Git LFS 支持"
```

## 🌟 上传后的操作

### 1. 设置项目描述
在 GitHub 仓库页面添加：
- 项目描述
- 主题标签 (python, stock-analysis, a-share, china-stocks)
- README 徽章

### 2. 创建 Releases
```bash
# 创建标签
git tag -a v1.0.0 -m "版本 1.0.0"
git push origin v1.0.0
```

### 3. 启用 GitHub Pages
在 Settings → Pages 中启用，用于展示文档。

## 📞 获取帮助

如果遇到问题，可以：
1. 查看 GitHub 官方文档
2. 在项目 Issues 中提问
3. 搜索相关错误信息

## 🎯 成功标志

上传成功后，您应该能在 GitHub 上看到：
- ✅ 所有代码文件
- ✅ README.md 正确显示
- ✅ 提交历史
- ✅ 项目结构完整

现在就开始上传您的 A股分析工具吧！🚀