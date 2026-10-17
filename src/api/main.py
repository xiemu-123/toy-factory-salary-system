# -*- coding: utf-8 -*-
"""
FastAPI 后端：提供 REST 接口
运行：uvicorn src.api.main:app --reload
体现"接口、前后端分离"能力。
"""
from fastapi import FastAPI, Query
from typing import Optional
import pandas as pd

from ..data_pipeline import load_and_clean
from ..reports import compute_salary, compute_daily, compute_proc_stat
from ..config import API_HOST, API_PORT

app = FastAPI(title='玩具厂计件工资 API', version='1.0')


def _get_clean_data() -> pd.DataFrame:
    """内部方法：拿到清洗后的数据并计算工资。"""
    df = load_and_clean()
    df['计件工资'] = df['合格数量'] * df['工序单价']
    df['总产量'] = df['合格数量'] + df['不良数量']
    # 把 NaN 空值全部替换成空字符串，否则 JSON 格式不支持
    df = df.fillna('')
    return df


@app.get('/api/health')
def health_check():
    """健康检查接口。"""
    return {'status': 'ok', 'message': 'API 运行正常'}


@app.get('/api/records')
def get_records(
    start_date: Optional[str] = Query(None, description='开始日期 YYYY-MM-DD'),
    end_date: Optional[str] = Query(None, description='结束日期 YYYY-MM-DD'),
    team: Optional[str] = Query(None, description='班组'),
    shift: Optional[str] = Query(None, description='班次'),
):
    """查询生产明细，支持按日期范围、班组、班次筛选。"""
    df = _get_clean_data()
    df['日期'] = pd.to_datetime(df['日期'])

    if start_date:
        df = df[df['日期'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['日期'] <= pd.to_datetime(end_date)]
    if team:
        df = df[df['班组'] == team]
    if shift:
        df = df[df['班次'] == shift]

    df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
    return df.to_dict(orient='records')


@app.get('/api/salary')
def get_salary():
    """个人工资条汇总。"""
    df = _get_clean_data()
    salary = compute_salary(df)
    return salary.to_dict(orient='records')


@app.get('/api/daily')
def get_daily(team: Optional[str] = Query(None, description='班组')):
    """班组日报。"""
    df = _get_clean_data()
    if team:
        df = df[df['班组'] == team]
    daily = compute_daily(df)
    daily['日期'] = pd.to_datetime(daily['日期']).dt.strftime('%Y-%m-%d')
    return daily.to_dict(orient='records')


@app.get('/api/process-stats')
def get_process_stats():
    """工序产量与不良率统计。"""
    df = _get_clean_data()
    proc = compute_proc_stat(df)
    return proc.to_dict(orient='records')


@app.get('/api/summary')
def get_summary():
    """顶部指标汇总（供前端 dashboard 使用）。"""
    df = _get_clean_data()
    total_qty = int(df['合格数量'].sum())
    total_bad = int(df['不良数量'].sum())
    total_salary = round(float(df['计件工资'].sum()), 2)
    bad_rate = round(total_bad / (total_qty + total_bad) * 100, 2) if (total_qty + total_bad) else 0
    return {
        '记录条数': len(df),
        '总合格数量': total_qty,
        '总计件工资': total_salary,
        '整体不良率': bad_rate,
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
