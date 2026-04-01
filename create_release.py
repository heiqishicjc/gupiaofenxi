#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Release 创建工具

自动创建 A股分析工具的 GitHub Release
"""

import sys
import os
import requests
import json
from datetime import datetime

# 添加 src 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.__version__ import __version__, __release_date__, __description__


def get_github_token():
    """获取 GitHub Token"""
    # 从环境变量获取
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        # 从文件获取（安全存储）
        token_file = os.path.join(os.path.expanduser('~'), '.github_token')
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()
    
    return token


def get_repo_info():
    """获取仓库信息"""
    # 从 Git 配置获取
    import subprocess
    
    # 获取远程仓库 URL
    result = subprocess.run(
        'git remote get-url origin',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ 无法获取远程仓库信息")
        return None
    
    remote_url = result.stdout.strip()
    
    # 解析仓库信息
    # 格式: https://github.com/username/repo.git
    # 或: git@github.com:username/repo.git
    
    if 'github.com' in remote_url:
        if remote_url.startswith('https://'):
            parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
        else:
            parts = remote_url.replace('git@github.com:', '').replace('.git', '').split('/')
        
        if len(parts) == 2:
            return {
                'owner': parts[0],
                'repo': parts[1]
            }
    
    return None


def create_release(version, changelog_content, draft=False, prerelease=False):
    """创建 GitHub Release"""
    
    token = get_github_token()
    if not token:
        print("❌ 未找到 GitHub Token")
        print("💡 请设置 GITHUB_TOKEN 环境变量或创建 ~/.github_token 文件")
        return False
    
    repo_info = get_repo_info()
    if not repo_info:
        print("❌ 无法获取仓库信息")
        return False
    
    owner = repo_info['owner']
    repo = repo_info['repo']
    
    # API 端点
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    # 请求头
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 请求数据
    data = {
        'tag_name': f'v{version}',
        'name': f'A股分析工具 v{version}',
        'body': changelog_content,
        'draft': draft,
        'prerelease': prerelease
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            release_info = response.json()
            print(f"✅ Release 创建成功!")
            print(f"   版本: v{version}")
            print(f"   标题: {release_info['name']}")
            print(f"   URL: {release_info['html_url']}")
            return True
        else:
            print(f"❌ Release 创建失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def generate_changelog(version):
    """生成变更日志内容"""
    
    # 获取最近的提交信息
    import subprocess
    
    # 获取上一个版本的标签
    result = subprocess.run(
        'git describe --tags --abbrev=0',
        shell=True,
        capture_output=True,
        text=True
    )
    
    previous_tag = result.stdout.strip() if result.returncode == 0 else None
    
    # 获取提交信息
    if previous_tag:
        log_command = f'git log {previous_tag}..HEAD --oneline'
    else:
        log_command = 'git log --oneline --max-count=20'
    
    result = subprocess.run(log_command, shell=True, capture_output=True, text=True)
    commits = result.stdout.strip().split('\n') if result.returncode == 0 else []
    
    # 生成变更日志
    changelog = f"# A股分析工具 v{version}\n\n"
    changelog += f"**发布日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    changelog += "## 变更内容\n\n"
    
    # 分类提交信息
    features = []
    fixes = []
    docs = []
    other = []
    
    for commit in commits:
        if not commit:
            continue
            
        # 解析提交信息
        hash_part = commit[:7]
        message = commit[8:]
        
        if message.startswith('feat:'):
            features.append(f"- {message[5:].strip()}")
        elif message.startswith('fix:'):
            fixes.append(f"- {message[4:].strip()}")
        elif message.startswith('docs:'):
            docs.append(f"- {message[5:].strip()}")
        else:
            other.append(f"- {message.strip()}")
    
    # 添加分类内容
    if features:
        changelog += "### 新增功能\n"
        changelog += '\n'.join(features) + '\n\n'
    
    if fixes:
        changelog += "### 修复问题\n"
        changelog += '\n'.join(fixes) + '\n\n'
    
    if docs:
        changelog += "### 文档更新\n"
        changelog += '\n'.join(docs) + '\n\n'
    
    if other:
        changelog += "### 其他变更\n"
        changelog += '\n'.join(other) + '\n\n'
    
    # 添加下载和使用说明
    changelog += "## 下载和使用\n\n"
    changelog += "### 安装方式\n"
    changelog += "```bash\n"
    changelog += "# 从 GitHub 下载\n"
    changelog += "git clone https://github.com/heiqishicjc/gupiaofenxi.git\n"
    changelog += "cd gupiaofenxi\n"
    changelog += "pip install -r requirements_minimal.txt\n"
    changelog += "```\n\n"
    
    changelog += "### 快速开始\n"
    changelog += "```python\n"
    changelog += "python simple_analyze.py\n"
    changelog += "```\n\n"
    
    changelog += "## 技术支持\n\n"
    changelog += "如有问题请访问项目页面或提交 Issue。\n"
    
    return changelog


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='创建 GitHub Release')
    parser.add_argument('--version', type=str, default=__version__, help='版本号')
    parser.add_argument('--draft', action='store_true', help='创建草稿 Release')
    parser.add_argument('--prerelease', action='store_true', help='创建预发布版本')
    parser.add_argument('--changelog', type=str, help='自定义变更日志文件')
    
    args = parser.parse_args()
    
    print("=== A股分析工具 GitHub Release 创建 ===")
    print(f"版本: v{args.version}")
    print(f"仓库: heiqishicjc/gupiaofenxi")
    
    # 生成变更日志
    if args.changelog and os.path.exists(args.changelog):
        with open(args.changelog, 'r', encoding='utf-8') as f:
            changelog_content = f.read()
    else:
        changelog_content = generate_changelog(args.version)
    
    print("\n📝 变更日志预览:")
    print("-" * 50)
    print(changelog_content[:500] + "..." if len(changelog_content) > 500 else changelog_content)
    print("-" * 50)
    
    # 确认创建
    confirm = input("\n确认创建 Release？(y/n): ").strip().lower()
    
    if confirm not in ['y', 'yes', '是']:
        print("👋 取消创建")
        return 0
    
    # 创建 Release
    success = create_release(
        version=args.version,
        changelog_content=changelog_content,
        draft=args.draft,
        prerelease=args.prerelease
    )
    
    if success:
        print(f"\n🎉 Release 创建流程完成!")
        print("下一步操作:")
        print("1. 检查 Release 页面")
        print("2. 更新项目文档")
        print("3. 通知用户更新")
    else:
        print("\n❌ Release 创建失败")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())