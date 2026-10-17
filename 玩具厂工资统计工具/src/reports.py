# -*- coding: utf-8 -*-
"""
第 3 步：工资计算 + 报表统计 + 导出 Excel
运行：python -m src.reports
输出：output/报表.xlsx
"""
import pandas as pd
from .data_pipeline import load_and_clean
from .config import OUTPUT_DIR


def compute_salary(df: pd.DataFrame) -> pd.DataFrame:
    """按员工汇总工资条。"""
    salary = (df.groupby(['员工编号', '姓名', '班组', '班次'], as_index=False)
              .agg(合格数量=('合格数量', 'sum'),
                   不良数量=('不良数量', 'sum'),
                   工资合计=('计件工资', 'sum')))
    salary['不良率'] = salary['不良数量'] / (salary['合格数量'] + salary['不良数量'])
    return salary


def compute_daily(df: pd.DataFrame) -> pd.DataFrame:
    """按日期+班组汇总日报。"""
    daily = (df.groupby(['日期', '班组'], as_index=False)
             .agg(合格数量=('合格数量', 'sum'),
                  不良数量=('不良数量', 'sum'),
                  工资合计=('计件工资', 'sum')))
    daily['不良率'] = daily['不良数量'] / (daily['合格数量'] + daily['不良数量'])
    return daily


def compute_proc_stat(df: pd.DataFrame) -> pd.DataFrame:
    """按工序汇总产量与不良率。"""
    proc = (df.groupby(['工序编号', '工序名称'], as_index=False)
            .agg(合格数量=('合格数量', 'sum'),
                 不良数量=('不良数量', 'sum'),
                 工资合计=('计件工资', 'sum')))
    proc['不良率'] = proc['不良数量'] / (proc['合格数量'] + proc['不良数量'])
    return proc


def build_reports():
    clean = load_and_clean()

    # 计算计件工资
    clean['计件工资'] = clean['合格数量'] * clean['工序单价']
    clean['总产量'] = clean['合格数量'] + clean['不良数量']

    salary = compute_salary(clean)
    daily = compute_daily(clean)
    proc_stat = compute_proc_stat(clean)

    # 导出 Excel
    out = OUTPUT_DIR / '报表.xlsx'
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        clean.to_excel(w, sheet_name='明细', index=False)
        salary.to_excel(w, sheet_name='个人工资条', index=False)
        daily.to_excel(w, sheet_name='班组日报', index=False)
        proc_stat.to_excel(w, sheet_name='工序统计', index=False)

    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    print('\n========== 个人工资条 ==========')
    print(salary.to_string(index=False))
    print('\n已导出报表:', out)
    return clean, salary, daily, proc_stat


if __name__ == '__main__':
    build_reports()
