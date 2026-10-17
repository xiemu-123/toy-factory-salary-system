# 玩具厂计件工资统计与生产日报系统

一个完整的 Python 全栈小项目：从数据采集、清洗、计算到前后端分离的 Web 查询系统。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 编程语言 | Python 3.10+ | 主力开发语言 |
| 数据库 | SQLite | 轻量级关系型数据库，零配置 |
| 后端框架 | FastAPI | 提供 RESTful API 接口 |
| 前端框架 | Streamlit | 快速搭建数据可视化页面 |
| 数据处理 | pandas | 数据清洗、分组统计、报表生成 |
| 测试框架 | pytest | 单元测试 |

## 项目结构

```
玩具厂工资统计工具/
├─ data/
│  └─ toy_factory.db          # SQLite 数据库（运行后生成）
├─ src/
│  ├─ __init__.py
│  ├─ config.py               # 全局配置（数据库路径、API端口等）
│  ├─ database.py             # 数据库连接、建表、读写
│  ├─ gen_data.py            # 生成模拟数据并写入数据库
│  ├─ data_pipeline.py        # 数据清洗管道
│  ├─ reports.py              # 工资计算、报表统计
│  ├─ api/
│  │  ├─ __init__.py
│  │  └─ main.py             # FastAPI 后端接口
│  └─ app.py                  # Streamlit 前端页面
├─ tests/
│  ├─ __init__.py
│  └─ test_pipeline.py        # 单元测试
├─ output/
│  └─ 报表.xlsx               # 运行后生成的报表
├─ requirements.txt           # 依赖清单
└─ README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库并生成模拟数据

```bash
python -m src.gen_data
```

### 3. 启动后端 API（新开一个终端）

```bash
uvicorn src.api.main:app --reload
```

启动后访问 http://127.0.0.1:8000/docs 可以看到自动生成的 API 文档。

### 4. 启动前端页面（再开一个终端）

```bash
streamlit run src/app.py
```

浏览器自动打开 http://localhost:8501 即可使用。

### 5. 运行单元测试

```bash
pytest tests/ -v
```

## API 接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/records` | GET | 生产明细查询（支持日期/班组/班次筛选） |
| `/api/salary` | GET | 个人工资条汇总 |
| `/api/daily` | GET | 班组日报 |
| `/api/process-stats` | GET | 工序产量与不良率统计 |
| `/api/summary` | GET | 顶部指标汇总 |

## 核心功能

1. **数据建模**：员工表、工序表、生产记录表三表关联，体现数据库设计思维
2. **数据清洗**：统一日期格式、处理缺失值、去重，保证数据质量
3. **工资计算**：按"合格数量 × 工序单价"自动计算计件工资
4. **报表统计**：个人工资条、班组日报、工序统计，一键导出 Excel
5. **前后端分离**：FastAPI 提供数据接口，Streamlit 做可视化展示
6. **单元测试**：覆盖数据清洗和工资计算的核心逻辑
