# -*- coding: utf-8 -*-
"""
单元测试：数据清洗和工资计算的正确性
运行：pytest tests/ -v
体现"配合测试"能力。
"""
import pandas as pd
from src.data_pipeline import parse_date, load_and_clean
from src.reports import compute_salary


def test_parse_date_normal():
    """测试常规日期格式解析。"""
    assert parse_date('2024-07-01') == pd.Timestamp('2024-07-01')
    assert parse_date('2024/7/1') == pd.Timestamp('2024-07-01')


def test_parse_date_chinese():
    """测试中文日期格式。"""
    assert parse_date('7月3日') == pd.Timestamp('2024-07-03')


def test_parse_date_compact():
    """测试紧凑数字格式。"""
    assert parse_date('20240703') == pd.Timestamp('2024-07-03')


def test_parse_date_invalid():
    """测试无效日期返回 NaT。"""
    assert pd.isna(parse_date('不存在的日期'))
    assert pd.isna(parse_date(None))


def test_load_and_clean():
    """测试清洗后数据完整性。"""
    df = load_and_clean()
    # 清洗后应该有这些列
    expected_cols = ['日期', '员工编号', '姓名', '班组', '班次',
                     '工序编号', '工序名称', '合格数量', '不良数量', '工序单价']
    assert list(df.columns) == expected_cols
    # 不应该有空的日期
    assert df['日期'].notna().all()
    # 不应该有空的工序单价
    assert df['工序单价'].notna().all()


def test_salary_calculation():
    """测试工资计算正确性。"""
    # 构造测试数据：1名员工，合格100件，单价0.5元
    test_df = pd.DataFrame([{
        '员工编号': 'E001', '姓名': '测试', '班组': '装配班', '班次': '白班',
        '合格数量': 100, '不良数量': 5, '计件工资': 100 * 0.5,
    }])
    salary = compute_salary(test_df)
    assert salary.iloc[0]['工资合计'] == 50.0
    assert salary.iloc[0]['合格数量'] == 100


def test_bad_rate():
    """测试不良率计算。"""
    test_df = pd.DataFrame([{
        '员工编号': 'E001', '姓名': '测试', '班组': '装配班', '班次': '白班',
        '合格数量': 95, '不良数量': 5, '计件工资': 50.0,
    }])
    salary = compute_salary(test_df)
    # 不良率 = 5 / (95 + 5) = 5%
    assert abs(salary.iloc[0]['不良率'] - 0.05) < 0.001
