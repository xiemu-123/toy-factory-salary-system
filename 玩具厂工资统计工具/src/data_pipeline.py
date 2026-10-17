# -*- coding: utf-8 -*-
"""
第 2 步：数据清洗管道
从数据库读取原始数据，清洗后关联员工/工序信息，返回干净的明细表。
"""
import re
import pandas as pd
from .database import query, get_conn


def parse_date(value):
    """把各种写法的日期统一成 pandas 时间戳；无法解析返回 NaT。"""
    if pd.isna(value):
        return pd.NaT
    s = str(value).strip()
    # 中文：7月3日 -> 2024-07-03
    m = re.match(r'^(\d{1,2})月(\d{1,2})日$', s)
    if m:
        s = '2024-%02d-%02d' % (int(m.group(1)), int(m.group(2)))
    # 紧凑数字：20240703
    if re.match(r'^\d{8}$', s):
        s = '%s-%s-%s' % (s[:4], s[4:6], s[6:])
    # 月-日-年：07-02-2024
    m = re.match(r'^(\d{2})-(\d{2})-(\d{4})$', s)
    if m:
        s = '%s-%s-%s' % (m.group(3), m.group(1), m.group(2))
    # 统一分隔符
    s = s.replace('.', '-').replace('/', '-')
    return pd.to_datetime(s, errors='coerce')


def load_and_clean() -> pd.DataFrame:
    """
    从数据库读取原始生产记录，做清洗，关联员工和工序信息。
    返回：清洗后的明细 DataFrame。
    """
    # ---- 从数据库读原始数据 ----
    prod = query('SELECT * FROM production_records')
    employees = query('SELECT * FROM employees')
    processes = query('SELECT * FROM processes')

    print('========== 清洗前 ==========')
    print('记录数:', len(prod))
    print('缺失值统计:\n', prod.isna().sum().to_string())
    print('重复行数:', prod.duplicated().sum())

    # ---- 1. 日期格式统一 ----
    prod['record_date'] = prod['record_date'].apply(parse_date)
    bad_dates = prod['record_date'].isna().sum()

    # ---- 2. 缺失值处理 ----
    prod['good_qty'] = pd.to_numeric(prod['good_qty'], errors='coerce').fillna(0)
    prod['bad_qty'] = pd.to_numeric(prod['bad_qty'], errors='coerce').fillna(0)

    # ---- 3. 删除重复记录 ----
    before = len(prod)
    prod = prod.drop_duplicates(subset=['record_date', 'emp_id', 'proc_id'])
    removed_dup = before - len(prod)

    # ---- 4. 关联员工表、工序表 ----
    prod = prod.merge(employees[['emp_id', 'name', 'team', 'shift']],
                      on='emp_id', how='left')
    prod = prod.merge(processes[['proc_id', 'name', 'price']],
                      on='proc_id', how='left', suffixes=('', '_proc'))

    # 整理列
    prod = prod.rename(columns={
        'record_date': '日期',
        'emp_id': '员工编号',
        'name': '姓名',
        'team': '班组',
        'shift': '班次',
        'proc_id': '工序编号',
        'name_proc': '工序名称',
        'good_qty': '合格数量',
        'bad_qty': '不良数量',
        'price': '工序单价',
    })
    prod = prod[['日期', '员工编号', '姓名', '班组', '班次',
                 '工序编号', '工序名称', '合格数量', '不良数量', '工序单价']]
    prod = prod.sort_values(['日期', '员工编号']).reset_index(drop=True)

    print('\n========== 清洗后 ==========')
    print('记录数:', len(prod), '（删除重复 %d 条）' % removed_dup)
    print('日期解析失败:', bad_dates)
    print('关联后缺失单价:', prod['工序单价'].isna().sum())
    return prod


if __name__ == '__main__':
    clean = load_and_clean()
    print('\n清洗后前 5 行预览:')
    print(clean.head().to_string(index=False))
