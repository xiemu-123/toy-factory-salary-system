# -*- coding: utf-8 -*-
"""
Streamlit 前端页面（调用后端 API 获取数据）
运行（在项目根目录）：
    1. 先启动后端：uvicorn src.api.main:app --reload
    2. 再启动前端：streamlit run src/app.py
"""
import requests
import pandas as pd
import streamlit as st

# 后端 API 地址
API_BASE = 'http://127.0.0.1:8000'

st.set_page_config(page_title='玩具厂计件工资统计', layout='wide')


@st.cache_data(ttl=300)
def fetch_summary():
    """获取顶部指标。"""
    r = requests.get(f'{API_BASE}/api/summary')
    return r.json()


@st.cache_data(ttl=300)
def fetch_records(start_date=None, end_date=None, team=None, shift=None):
    """获取生产明细，支持筛选。"""
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    if team:
        params['team'] = team
    if shift:
        params['shift'] = shift
    r = requests.get(f'{API_BASE}/api/records', params=params)
    return pd.DataFrame(r.json())


@st.cache_data(ttl=300)
def fetch_daily():
    """获取班组日报。"""
    r = requests.get(f'{API_BASE}/api/daily')
    return pd.DataFrame(r.json())


@st.cache_data(ttl=300)
def fetch_proc_stats():
    """获取工序统计。"""
    r = requests.get(f'{API_BASE}/api/process-stats')
    return pd.DataFrame(r.json())


# ---------- 页面标题 ----------
st.title('玩具厂计件工资统计与生产日报')

# 健康检查
try:
    health = requests.get(f'{API_BASE}/api/health', timeout=2).json()
    if health.get('status') == 'ok':
        st.sidebar.success('后端 API 已连接')
    else:
        st.sidebar.warning('后端 API 异常')
except Exception:
    st.sidebar.error('无法连接后端 API，请先运行：uvicorn src.api.main:app --reload')
    st.stop()

# ---------- 侧边栏筛选 ----------
with st.sidebar:
    st.header('筛选条件')
    all_records = fetch_records()
    dates = pd.to_datetime(all_records['日期']).dt.date.unique()
    min_d, max_d = min(dates), max(dates)

    drange = st.date_input('日期范围', value=(min_d, max_d),
                           min_value=min_d, max_value=max_d)
    teams = st.multiselect('班组', sorted(all_records['班组'].dropna().unique()))
    shifts = st.multiselect('班次', sorted(all_records['班次'].dropna().unique()))

# 应用筛选（单班组/单班次，多选时取并集）
team_filter = teams[0] if teams else None
shift_filter = shifts[0] if shifts else None

f = fetch_records(
    start_date=drange[0].strftime('%Y-%m-%d') if isinstance(drange, tuple) else None,
    end_date=drange[1].strftime('%Y-%m-%d') if isinstance(drange, tuple) else None,
    team=team_filter,
    shift=shift_filter,
)

# ---------- 顶部指标 ----------
summary = fetch_summary()
c1, c2, c3, c4 = st.columns(4)
c1.metric('记录条数', summary['记录条数'])
c2.metric('总合格数量', summary['总合格数量'])
c3.metric('总计件工资', f"¥{summary['总计件工资']:,.2f}")
c4.metric('整体不良率', f"{summary['整体不良率']:.2f}%")

# ---------- 图表 ----------
st.subheader('每日计件工资')
daily_df = fetch_daily()
if not daily_df.empty:
    daily_df['日期'] = pd.to_datetime(daily_df['日期'])
    chart_data = daily_df.groupby(daily_df['日期'].dt.date)['工资合计'].sum()
    st.bar_chart(chart_data)

st.subheader('各工序合格数量')
proc_df = fetch_proc_stats()
if not proc_df.empty:
    st.bar_chart(proc_df.set_index('工序名称')['合格数量'])

# ---------- 明细 ----------
st.subheader('生产明细')
st.dataframe(f, use_container_width=True, hide_index=True)

st.download_button(
    '导出筛选结果为 CSV',
    f.to_csv(index=False).encode('utf-8-sig'),
    file_name='筛选明细.csv', mime='text/csv')
