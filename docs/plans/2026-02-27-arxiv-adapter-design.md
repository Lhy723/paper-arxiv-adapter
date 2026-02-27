# ArXiv 论文采集适配器设计文档

## 概述

轻量封装 arxiv.py/feedparser，统一「单篇 / 批量 / 订阅」采集接口，增加论文去重、版本管理、元数据标准化（适配后续 AI 处理），内置 ArXiv 合规请求规则。

## 项目结构

```
paper-arxiv-adapter/
├── src/paper_arxiv_adapter/     # Python 核心库
│   ├── __init__.py
│   ├── adapter.py               # 核心适配器类
│   ├── models.py                # 数据模型
│   ├── storage.py               # 存储抽象
│   ├── dedup.py                 # 去重逻辑
│   ├── version.py               # 版本管理
│   ├── metadata.py              # 元数据标准化
│   └── compliance.py            # ArXiv 合规请求规则
├── web/
│   ├── backend/                 # FastAPI 后端
│   │   ├── main.py              # 应用入口
│   │   ├── routes/              # API 路由
│   │   └── pyproject.toml       # 后端依赖
│   └── frontend/                # Vue 前端
│       ├── src/
│       ├── package.json
│       └── vite.config.ts
├── tests/                       # 测试
├── pyproject.toml               # 核心库依赖
└── README.md
```

## 核心功能

### 1. 统一采集接口

```python
from paper_arxiv_adapter import ArxivAdapter, SQLiteBackend

adapter = ArxivAdapter(storage=SQLiteBackend("papers.db"))

# 单篇采集
paper = adapter.fetch("2301.07041v2")

# 批量搜索
papers = adapter.search("machine learning", max_results=10)

# RSS 订阅（增量更新）
adapter.subscribe(
    category="cs.AI",
    on_new=lambda paper: print(f"新论文: {paper.title}")
)
```

### 2. 去重策略

- **去重键**：`arxiv_id + version` 组合
- 同一 arxiv_id 不同版本视为不同论文

### 3. 版本管理

- 保留所有版本
- 支持版本历史查询
- 增量更新：记录已处理的 `arxiv_id + version`

### 4. 元数据标准化

```python
@dataclass
class Paper:
    arxiv_id: str              # 如 "2301.07041"
    version: str               # 如 "v2"
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]      # ArXiv 分类
    published: datetime
    updated: datetime
    pdf_url: str
    source_url: str
    
    # AI 处理相关字段
    keywords: list[str] | None = None
    summary: str | None = None        # AI 生成的摘要
    embedding: list[float] | None = None  # 向量嵌入
```

### 5. 存储抽象

- 支持 SQLite 存储（默认）
- 支持无存储模式（配置开关）

### 6. ArXiv 合规请求规则

- 请求间隔：≥ 3 秒（可配置）
- User-Agent：标识项目名称和联系方式
- 批量请求：支持分页

## Web API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/papers` | GET | 获取论文列表 |
| `/api/papers/{arxiv_id}` | GET | 获取单篇论文 |
| `/api/papers/{arxiv_id}/versions` | GET | 获取版本历史 |
| `/api/search` | POST | 搜索论文 |
| `/api/subscribe` | POST | 创建订阅 |
| `/api/subscriptions` | GET | 获取订阅列表 |

## 前端功能

- 论文列表展示（支持分类筛选）
- 论文详情页（显示元数据、版本历史）
- 搜索功能
- 订阅管理

## 技术栈

- **核心库**：Python 3.10+, arxiv.py, feedparser
- **后端**：FastAPI, uvicorn
- **前端**：Vue 3, Vite
- **存储**：SQLite
- **依赖管理**：uv

## 开源协议

MIT License
