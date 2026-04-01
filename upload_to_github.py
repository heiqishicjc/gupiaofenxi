#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 上传助手

这个脚本将帮助您将项目上传到 GitHub
"""

import os
import subprocess
import sys

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n🔧 {description}")
    print(f"   命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ 成功")
            if result.stdout:
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ 失败")
            if result.stderr:
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def check_git_config():
    """检查 Git 配置"""
    print("\n📋 检查 Git 配置...")
    
    # 检查用户名
    username_result = run_command("git config user.name", "检查 Git 用户名")
    if not username_result:
        print("   ⚠️  未设置 Git 用户名")
    
    # 检查邮箱
    email_result = run_command("git config user.email", "检查 Git 邮箱")
    if not email_result:
        print("   ⚠️  未设置 Git 邮箱")
    
    return username_result and email_result

def initialize_git_repo():
    """初始化 Git 仓库"""
    print("\n🚀 开始初始化 Git 仓库...")
    
    steps = [
        ("git init", "初始化 Git 仓库"),
        ("git add .", "添加所有文件到暂存区"),
        ("git status", "检查文件状态"),
        ("git commit -m \"初始提交: A股股票分析工具 v1.0\"", "创建初始提交")
    ]
    
    for command, description in steps:
        if not run_command(command, description):
            return False
    
    return True

def check_github_connection():
    """检查 GitHub 连接"""
    print("\n🌐 检查 GitHub 连接...")
    
    # 测试连接到 GitHub
    test_result = run_command("ping -n 1 github.com", "测试网络连接")
    if not test_result:
        print("   ⚠️  无法连接到 GitHub，请检查网络")
        return False
    
    return True

def create_github_repo_instructions():
    """显示创建 GitHub 仓库的说明"""
    print("\n" + "="*60)
    print("📝 手动创建 GitHub 仓库")
    print("="*60)
    
    instructions = """
请按照以下步骤在 GitHub 上创建仓库：

1. 打开 https://github.com 并登录
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: gupiaofenxi
   - Description: A股股票分析工具 - Python-based stock analysis tool
   - Visibility: Public (推荐)
   - 不要勾选 "Initialize this repository with" 的任何选项

4. 点击 "Create repository"
5. 复制提供的 Git 命令，类似：
   git remote add origin https://github.com/您的用户名/gupiaofenxi.git
   git branch -M main
   git push -u origin main

完成后，请运行下一步的推送命令。
    """
    
    print(instructions)

def push_to_github():
    """推送到 GitHub"""
    print("\n📤 准备推送到 GitHub...")
    
    # 首先检查是否已设置远程仓库
    remote_check = run_command("git remote -v", "检查远程仓库设置")
    
    if not remote_check:
        print("\n❌ 未设置远程仓库，请先完成手动创建步骤")
        create_github_repo_instructions()
        return False
    
    # 推送代码
    push_steps = [
        ("git branch -M main", "设置主分支"),
        ("git push -u origin main", "推送到 GitHub")
    ]
    
    for command, description in push_steps:
        if not run_command(command, description):
            print("\n💡 如果推送失败，请检查：")
            print("   1. GitHub 用户名和密码/令牌是否正确")
            print("   2. 网络连接是否正常")
            print("   3. 远程仓库地址是否正确")
            return False
    
    return True

def main():
    """主函数"""
    print("=== A股股票分析工具 - GitHub 上传助手 ===")
    print("本脚本将帮助您将项目上传到 GitHub")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 检查是否是项目根目录
    required_files = ["main.py", "README.md", "requirements.txt"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        print("请确保在项目根目录运行此脚本")
        return
    
    print("✅ 项目结构完整")
    
    # 执行上传步骤
    steps = [
        ("检查 Git 配置", check_git_config),
        ("初始化 Git 仓库", initialize_git_repo),
        ("检查 GitHub 连接", check_github_connection),
        ("推送到 GitHub", push_to_github)
    ]
    
    for step_name, step_function in steps:
        print(f"\n{'='*40}")
        print(f"步骤: {step_name}")
        print('='*40)
        
        if not step_function():
            print(f"\n❌ {step_name} 失败")
            
            if step_name == "推送到 GitHub":
                print("\n💡 请手动完成 GitHub 仓库创建后重试")
                create_github_repo_instructions()
            
            return
    
    print("\n" + "="*60)
    print("🎉 恭喜！项目已成功上传到 GitHub")
    print("="*60)
    print("""
下一步操作建议：

1. 访问您的 GitHub 仓库页面
2. 添加项目描述和标签
3. 启用 GitHub Pages 展示文档
4. 创建第一个 Release

项目链接应该类似：
https://github.com/您的用户名/gupiaofenxi

感谢使用 A股股票分析工具！🚀
    """)

if __name__ == "__main__":
    main()