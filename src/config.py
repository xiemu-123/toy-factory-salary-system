# -*- coding: utf-8 -*-
"""
全局配置：数据库路径、输出目录、API端口等
所有模块统一从这里读配置，方便切换环境（开发/测试/生产）。
"""
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库（SQLite 文件）
DB_PATH = BASE_DIR / 'data' / 'toy_factory.db'

# 输出目录
OUTPUT_DIR = BASE_DIR / 'output'

# API 配置
API_HOST = '127.0.0.1'
API_PORT = 8000

# 确保目录存在
DB_PATH.parent.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
