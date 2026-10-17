# -*- coding: utf-8 -*-
"""
第 1 步：生成模拟数据并写入 SQLite 数据库
运行：python -m src.gen_data
输出：data/toy_factory.db（含 employees、processes、production_records 三张表）
说明：生产记录里故意放了"缺失值、重复记录、日期格式不统一"，用于后面数据清洗演示。
"""
import random
import pandas as pd
from .database import init_db, insert_employees, insert_processes, insert_production

random.seed(42)  # 固定随机种子，保证每次生成结果一样


def main():
    # 初始化数据库（建表）
    init_db()

    # ---------- 1. 员工表 ----------
    employees = pd.DataFrame([
        ['E001', '张伟', '装配班', '白班'],
        ['E002', '李娜', '装配班', '白班'],
        ['E003', '王强', '装配班', '夜班'],
        ['E004', '赵敏', '装配班', '夜班'],
        ['E005', '陈杰', '包装班', '白班'],
        ['E006', '刘洋', '包装班', '白班'],
        ['E007', '周丽', '包装班', '夜班'],
        ['E008', '吴磊', '包装班', '夜班'],
    ], columns=['emp_id', 'name', 'team', 'shift'])
    insert_employees(employees)

    # ---------- 2. 工序表（含工序单价） ----------
    processes = pd.DataFrame([
        ['P01', '焊接', 0.50],
        ['P02', '装配', 0.80],
        ['P03', '检验', 0.40],
        ['P04', '包装', 0.30],
    ], columns=['proc_id', 'name', 'price'])
    insert_processes(processes)

    # ---------- 3. 生产记录（原始、含脏数据） ----------
    dates = ['2024-07-01', '2024-07-02', '2024-07-03', '2024-07-04', '2024-07-05']
    records = []
    for d in dates:
        for _, emp in employees.iterrows():
            k = random.randint(1, 2)
            for proc in processes.sample(k).itertuples(index=False):
                good = random.randint(80, 200)
                bad = random.randint(0, 12)
                records.append([
                    d, emp['emp_id'], proc.proc_id, good, bad
                ])

    prod = pd.DataFrame(records, columns=[
        'record_date', 'emp_id', 'proc_id', 'good_qty', 'bad_qty'
    ])

    # ---- 故意制造脏数据 ----
    # (1) 日期格式不统一
    alt_formats = {
        0: '2024/7/1',
        1: '2024.7.1',
        2: '07-02-2024',
        3: '7月3日',
        4: '20240703',
    }
    for idx, val in alt_formats.items():
        prod.loc[idx, 'record_date'] = val

    # (2) 缺失值
    prod.loc[6, 'good_qty'] = None
    prod.loc[10, 'good_qty'] = None
    prod.loc[8, 'emp_id'] = None

    # (3) 重复记录
    dup = prod.iloc[[0, 12, 20]].copy()
    prod = pd.concat([prod, dup], ignore_index=True)

    insert_production(prod)

    print('已生成数据库')
    print('员工 %d 人，工序 %d 道，生产记录 %d 条（含脏数据）' % (
        len(employees), len(processes), len(prod)))


if __name__ == '__main__':
    main()
