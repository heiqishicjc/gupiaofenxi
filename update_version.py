#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本号更新工具

用于管理 A股分析工具的版本号更新
"""

import sys
import os
import re
import argparse
from datetime import datetime

# 添加 src 目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.__version__ import __version__, __version_info__


def parse_version(version_str):
    """解析版本字符串"""
    return tuple(map(int, version_str.split('.')))


def format_version(version_tuple):
    """格式化版本元组"""
    return '.'.join(map(str, version_tuple))


def update_version_file(major=False, minor=False, patch=True):
    """更新版本文件"""
    version_file = os.path.join('src', '__version__.py')
    
    # 读取当前版本
    current_version = parse_version(__version__)
    
    # 计算新版本
    if major:
        new_version = (current_version[0] + 1, 0, 0)
        change_type = "主版本"
    elif minor:
        new_version = (current_version[0], current_version[1] + 1, 0)
        change_type = "次版本"
    elif patch:
        new_version = (current_version[0], current_version[1], current_version[2] + 1)
        change_type = "修订版本"
    else:
        new_version = current_version
        change_type = "无变化"
    
    new_version_str = format_version(new_version)
    
    # 读取文件内容
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新版本信息
    content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{new_version_str}"',
        content
    )
    
    content = re.sub(
        r'__version_info__ = \([^)]+\)',
        f'__version_info__ = {new_version}',
        content
    )
    
    # 更新发布日期
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(
        r'__release_date__ = "[^"]+"',
        f'__release_date__ = "{today}"',
        content
    )
    
    # 写入文件
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return new_version_str, change_type


def update_setup_py(version):
    """更新 setup.py 中的版本号"""
    setup_file = 'setup.py'
    
    if not os.path.exists(setup_file):
        return False
    
    with open(setup_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新版本号
    content = re.sub(
        r'version="[^"]+"',
        f'version="{version}"',
        content
    )
    
    with open(setup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def create_git_tag(version, message=None):
    """创建 Git 标签"""
    if not message:
        message = f"版本 {version}: A股分析工具更新"
    
    tag_name = f"v{version}"
    
    # 检查是否已存在该标签
    import subprocess
    result = subprocess.run(
        f'git tag -l "{tag_name}"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print(f"⚠️  标签 {tag_name} 已存在，跳过创建")
        return False
    
    # 创建标签
    result = subprocess.run(
        f'git tag -a {tag_name} -m "{message}"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ 创建 Git 标签: {tag_name}")
        return True
    else:
        print(f"❌ 创建标签失败: {result.stderr}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='A股分析工具版本管理')
    parser.add_argument('--major', action='store_true', help='增加主版本号')
    parser.add_argument('--minor', action='store_true', help='增加次版本号')
    parser.add_argument('--patch', action='store_true', help='增加修订号（默认）')
    parser.add_argument('--set', type=str, help='设置特定版本号')
    parser.add_argument('--tag', action='store_true', help='创建 Git 标签')
    parser.add_argument('--message', type=str, help='标签消息')
    
    args = parser.parse_args()
    
    print("=== A股分析工具版本管理 ===")
    print(f"当前版本: {__version__}")
    
    if args.set:
        # 设置特定版本
        if not re.match(r'^\d+\.\d+\.\d+$', args.set):
            print("❌ 版本号格式错误，应为 X.Y.Z")
            return 1
        
        new_version = args.set
        change_type = "手动设置"
        
        # 更新版本文件
        version_file = os.path.join('src', '__version__.py')
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(
            r'__version__ = "[^"]+"',
            f'__version__ = "{new_version}"',
            content
        )
        
        version_tuple = tuple(map(int, new_version.split('.')))
        content = re.sub(
            r'__version_info__ = \([^)]+\)',
            f'__version_info__ = {version_tuple}',
            content
        )
        
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    else:
        # 自动递增版本
        new_version, change_type = update_version_file(
            major=args.major,
            minor=args.minor,
            patch=not (args.major or args.minor)
        )
    
    print(f"新版本: {new_version} ({change_type})")
    
    # 更新 setup.py
    if update_setup_py(new_version):
        print("✅ 更新 setup.py")
    
    # 创建 Git 标签
    if args.tag or args.message:
        message = args.message or f"版本 {new_version}: A股分析工具更新"
        create_git_tag(new_version, message)
    
    print(f"\n🎉 版本更新完成!")
    print(f"下一步操作:")
    print(f"1. 提交版本变更: git commit -am 'chore: 更新版本到 {new_version}'")
    print(f"2. 推送标签: git push origin main --tags")
    print(f"3. 在 GitHub 创建 Release")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())