#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息文件

管理 A股分析工具的版本信息
"""

# 版本信息
__version__ = "1.3.0"
__version_info__ = (1, 3, 0)

# 版本元数据
__author__ = "heiqishicjc"
__email__ = "heiqishicjc@hotmail.com"
__description__ = "A股股票分析工具 - Python-based stock analysis tool for Chinese A-share market"
__url__ = "https://github.com/heiqishicjc/gupiaofenxi"

# 版本发布日期
__release_date__ = "2026-04-10"

# 兼容性信息
__python_requires__ = ">=3.8"
__license__ = "MIT"


def get_version():
    """获取完整版本信息"""
    return __version__


def get_version_info():
    """获取版本信息元组"""
    return __version_info__


def get_version_string():
    """获取格式化的版本字符串"""
    return f"A股分析工具 v{__version__}"


def check_compatibility(required_version):
    """
    检查版本兼容性
    
    Args:
        required_version: 要求的版本号，格式如 "1.0.0"
        
    Returns:
        bool: 是否兼容
    """
    try:
        from packaging import version
        current = version.parse(__version__)
        required = version.parse(required_version)
        return current >= required
    except ImportError:
        # 如果没有 packaging 库，使用简单比较
        current_parts = list(map(int, __version__.split('.')))
        required_parts = list(map(int, required_version.split('.')))
        
        # 填充到相同长度
        max_len = max(len(current_parts), len(required_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        required_parts.extend([0] * (max_len - len(required_parts)))
        
        return current_parts >= required_parts


if __name__ == "__main__":
    # 命令行版本信息输出
    print(f"版本: {get_version_string()}")
    print(f"发布日期: {__release_date__}")
    print(f"作者: {__author__}")
    print(f"项目地址: {__url__}")