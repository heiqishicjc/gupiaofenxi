# 版本控制指南

## 📚 语义化版本规范 (SemVer)

遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/) 规范：

### 版本格式：`主版本号.次版本号.修订号`
- **主版本号 (MAJOR)**: 不兼容的 API 修改
- **次版本号 (MINOR)**: 向下兼容的功能性新增
- **修订号 (PATCH)**: 向下兼容的问题修正

### 版本号示例
- `1.0.0` - 第一个稳定版本
- `1.0.1` - 修复 bug
- `1.1.0` - 新增功能
- `2.0.0` - 重大更新，可能不兼容

## 🚀 版本发布流程

### 1. 开发阶段
```bash
# 在功能分支开发
git checkout -b feature/new-indicator
git add .
git commit -m "feat: 添加新的技术指标"
```

### 2. 测试阶段
```bash
# 合并到开发分支
git checkout develop
git merge feature/new-indicator
python -m pytest tests/ -v
```

### 3. 发布准备
```bash
# 更新版本号
python update_version.py --minor

# 更新变更日志
python update_changelog.py
```

### 4. 发布版本
```bash
# 创建标签
git tag -a v1.1.0 -m "版本 1.1.0: 新增技术指标功能"

# 推送到 GitHub
git push origin main --tags

# 创建 GitHub Release
python create_release.py
```

## 📊 版本号管理规则

### 何时增加主版本号
- API 不兼容的修改
- 重大架构变更
- 删除已弃用功能

### 何时增加次版本号
- 新增功能
- 改进现有功能
- 新增技术指标

### 何时增加修订号
- 修复 bug
- 性能优化
- 文档更新

## 🔧 版本控制工具

### 1. 版本配置文件
项目根目录的 `pyproject.toml` 或 `__version__.py` 文件

### 2. Git 标签
每个发布版本对应一个 Git 标签

### 3. GitHub Releases
使用 GitHub Releases 功能管理版本发布

## 📝 提交信息规范

### 提交信息格式
```
类型(范围): 描述

详细描述（可选）

BREAKING CHANGE: 不兼容变更说明（可选）
```

### 提交类型
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### 提交示例
```bash
git commit -m "feat(indicators): 添加乖离率指标计算"
git commit -m "fix(data): 修复数据获取时的网络错误"
git commit -m "docs: 更新使用指南和示例"
```

## 🔄 分支管理策略

### 主要分支
- `main` - 稳定版本分支
- `develop` - 开发分支
- `feature/*` - 功能分支
- `hotfix/*` - 紧急修复分支

### 分支工作流
```
feature/new-feature → develop → main (发布)
                    ↓
               hotfix/bug-fix
```

## 📋 版本发布检查清单

### 发布前检查
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 变更日志已填写
- [ ] 版本号已更新
- [ ] 代码审查完成

### 发布后操作
- [ ] 创建 Git 标签
- [ ] 推送到 GitHub
- [ ] 创建 Release
- [ ] 更新依赖说明
- [ ] 通知用户

## 🛠️ 自动化工具

### 版本管理脚本
- `update_version.py` - 版本号更新
- `create_release.py` - 创建发布
- `changelog_generator.py` - 生成变更日志

### CI/CD 集成
GitHub Actions 自动运行测试和发布流程

## 💡 最佳实践

1. **定期发布** - 不要积累太多变更
2. **语义化版本** - 明确版本含义
3. **详细变更日志** - 记录所有重要变更
4. **测试覆盖** - 确保版本质量
5. **回滚计划** - 准备应急方案

## 📞 问题解决

### 常见问题
1. **版本冲突** - 使用语义化版本避免
2. **依赖问题** - 明确版本依赖关系
3. **发布错误** - 使用自动化工具减少错误

### 获取帮助
- 查看 GitHub Releases 文档
- 参考语义化版本规范
- 在项目 Issues 中提问

现在您可以按照这个指南管理您的 A股分析工具版本了！