#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本管理便捷启动脚本

避免输入完整路径，简化版本管理操作
"""

import sys
import os
import subprocess

# 虚拟环境 Python 路径
VENV_PYTHON = os.path.join('venv', 'Scripts', 'python.exe')

def run_command(script, *args):
    """运行指定脚本"""
    if not os.path.exists(VENV_PYTHON):
        print("❌ 虚拟环境未找到，请先创建虚拟环境")
        return False
    
    command = [VENV_PYTHON, script] + list(args)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=== A股分析工具版本管理便捷脚本 ===")
        print("使用方法:")
        print("  python run_version.py version     # 查看版本")
        print("  python run_version.py update      # 更新版本")
        print("  python run_version.py patch       # 增加修订版本")
        print("  python run_version.py minor       # 增加次版本")
        print("  python run_version.py major       # 增加主版本")
        print("  python run_version.py tag         # 创建标签")
        return
    
    command = sys.argv[1]
    
    if command == "version":
        run_command("src/__version__.py")
    
    elif command == "update":
        run_command("update_version.py")
    
    elif command == "patch":
        run_command("update_version.py", "--patch")
    
    elif command == "minor":
        run_command("update_version.py", "--minor")
    
    elif command == "major":
        run_command("update_version.py", "--major")
    
    elif command == "tag":
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "版本更新"
        run_command("update_version.py", "--tag", "--message", message)
    
    else:
        print(f"❌ 未知命令: {command}")
        print("💡 使用 'python run_version.py' 查看帮助")

if __name__ == "__main__":
    main()