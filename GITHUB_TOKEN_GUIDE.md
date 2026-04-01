# GitHub Personal Access Token (Classic) 配置指南

## 🔐 什么是 Personal Access Token？

Personal Access Token (PAT) 是 GitHub 提供的一种安全认证方式，用于替代密码进行 API 调用和 Git 操作。特别是对于启用双重认证 (2FA) 的用户，必须使用 Token 进行认证。

## 📋 获取 Token 的步骤

### 步骤 1: 登录 GitHub
1. 打开 https://github.com 并登录您的账户

### 步骤 2: 进入 Token 设置
1. 点击右上角头像 → **Settings**
2. 在左侧菜单中，滚动到底部 → **Developer settings**
3. 选择 **Personal access tokens** → **Tokens (classic)**

### 步骤 3: 生成新 Token
1. 点击 **Generate new token** → **Generate new token (classic)**
2. 填写 Token 信息：
   - **Note**: `A股分析工具上传` (或其他描述性名称)
   - **Expiration**: 建议选择 30 天或 90 天
   - **Select scopes**: 至少勾选以下权限：
     - ✅ **repo** (全选) - 访问和修改仓库
     - ✅ **workflow** - 如果需要 GitHub Actions

### 步骤 4: 复制 Token
1. 点击 **Generate token**
2. **立即复制 Token**（关闭页面后将无法再次查看）
3. 安全保存 Token（建议使用密码管理器）

## ⚠️ 安全注意事项

- **Token 等同于密码**，请妥善保管
- **不要将 Token 提交到代码仓库**
- **定期更新 Token**，特别是短期 Token
- **使用环境变量或配置文件**存储 Token

## 🔧 在脚本中使用 Token

### 方法 1: 交互式输入（推荐）
```python
import getpass
token = getpass.getpass("请输入 GitHub Token: ")
```

### 方法 2: 环境变量
```bash
# 设置环境变量
export GITHUB_TOKEN=your_token_here
```

```python
import os
token = os.getenv('GITHUB_TOKEN')
```

### 方法 3: 配置文件
创建 `.env` 文件（添加到 .gitignore）：
```
GITHUB_TOKEN=your_token_here
```

## 🚀 Token 认证的 Git 命令

### 使用 Token 推送代码
```bash
# 传统方式（会提示输入用户名和Token）
git push -u origin main

# 或者直接嵌入 URL
git remote set-url origin https://username:token@github.com/username/repo.git
git push -u origin main
```

### 验证 Token 有效性
```bash
# 测试 Token 是否有效
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

## ❌ 常见问题解决

### 问题 1: Token 无效
```
remote: Invalid username or password.
fatal: Authentication failed for 'https://github.com/...'
```
**解决方案**:
- 检查 Token 是否已过期
- 确认 Token 权限包含 repo 权限
- 重新生成 Token

### 问题 2: 权限不足
```
remote: Permission to username/repo.git denied to user.
```
**解决方案**:
- 确认 Token 有足够的权限
- 检查仓库是否属于该用户

### 问题 3: 2FA 用户必须使用 Token
```
remote: Support for password authentication was removed on August 13, 2021.
Please use a personal access token instead.
```
**解决方案**:
- 必须使用 Personal Access Token
- 无法使用密码进行认证

## 🔄 更新和撤销 Token

### 更新 Token
1. 生成新的 Token
2. 更新使用该 Token 的所有地方
3. 撤销旧的 Token

### 撤销 Token
1. 进入 Settings → Developer settings → Personal access tokens
2. 找到要撤销的 Token
3. 点击 **Revoke**

## 📞 获取帮助

如果遇到 Token 相关问题：
1. 查看 [GitHub 官方文档](https://docs.github.com/en/authentication)
2. 检查 Token 权限和过期时间
3. 重新生成 Token
4. 在项目 Issues 中提问

## 💡 最佳实践

1. **为不同用途创建不同 Token**
2. **设置合理的过期时间**
3. **使用最小必要权限原则**
4. **定期审计和更新 Token**
5. **不要在代码中硬编码 Token**

现在您已经了解了如何安全地使用 GitHub Personal Access Token！