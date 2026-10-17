# -*- coding: utf-8 -*-
"""
数据库模块：SQLite 连接、建表、初始化
体现"数据库"能力：用正式的关系型数据库替代 Excel 文件。
"""
import sqlite3
import pandas as pd
from .config import DB_PATH


def get_conn():
    """获取数据库连接（每次调用返回新连接，用完记得 close）。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # 让查询结果可以按列名访问
    return conn


def init_db():
    """创建表（如果不存在）。
    三张核心表，对应原来的 Excel 三个 sheet：
    - employees（员工）：员工编号为主键
    - processes（工序）：工序编号为主键
    - production_records（生产记录）：员工编号、工序编号为外键
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id   TEXT PRIMARY KEY,   -- 员工编号
            name     TEXT NOT NULL,      -- 姓名
            team     TEXT,               -- 班组
            shift    TEXT                -- 班次
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS processes (
            proc_id   TEXT PRIMARY KEY,   -- 工序编号
            name      TEXT NOT NULL,      -- 工序名称
            price     REAL NOT NULL       -- 工序单价（元/件）
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS production_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,       -- 日期（ISO 格式 YYYY-MM-DD）
            emp_id      TEXT,                -- 员工编号（外键 -> employees）
            proc_id     TEXT,                -- 工序编号（外键 -> processes）
            good_qty    INTEGER DEFAULT 0,   -- 合格数量
            bad_qty     INTEGER DEFAULT 0    -- 不良数量
        )
    ''')

    conn.commit()
    conn.close()
    print('数据库初始化完成:', DB_PATH)


def insert_employees(df: pd.DataFrame):
    """批量写入员工表。"""
    conn = get_conn()
    df.to_sql('employees', conn, if_exists='replace', index=False,
              dtype={'emp_id': 'TEXT PRIMARY KEY'})
    conn.close()


def insert_processes(df: pd.DataFrame):
    """批量写入工序表。"""
    conn = get_conn()
    df.to_sql('processes', conn, if_exists='replace', index=False)
    conn.close()


def insert_production(df: pd.DataFrame):
    """批量写入生产记录表。"""
    conn = get_conn()
    df.to_sql('production_records', conn, if_exists='replace', index=False)
    conn.close()


def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """执行查询 SQL，返回 DataFrame。"""
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


if __name__ == '__main__':
    init_db()
