# ArXiv Paper Adapter

轻量封装 arxiv.py/feedparser，统一「单篇 / 批量 / 订阅」采集接口。

## 功能特性

- 统一采集接口：单篇、批量搜索、RSS 订阅
- 论文去重：基于 arxiv_id + version
- 版本管理：保留所有版本历史
- 元数据标准化：适配 AI 处理场景
- ArXiv 合规请求：内置请求间隔控制
- 可选存储：SQLite 或无存储模式

## 安装

```bash
uv sync
```

## 核心库使用

```python
from paper_arxiv_adapter import ArxivAdapter, SQLiteBackend

adapter = ArxivAdapter(storage=SQLiteBackend("papers.db"))

# 单篇采集
paper = adapter.fetch("2301.07041v2")

# 批量搜索
papers = adapter.search("machine learning", max_results=10)

# RSS 订阅
adapter.subscribe(category="cs.AI", on_new=lambda p: print(p.title))
```

## 运行 Web 应用

```bash
# 构建前端
cd web/frontend && npm run build

# 启动后端
cd web/backend && uv run uvicorn main:app --reload
```

访问 http://localhost:8000

## 开源协议

MIT License
