# ArXiv Paper Adapter 前端功能扩展计划

## 目标
扩展前端页面功能，实现完整的论文管理体验，包括数据浏览、详情查看、统计展示和高级搜索。

## 设计系统
- **Style**: Vibrant & Block-based（活力块状风格）
- **Primary**: #1E40AF（深蓝）
- **Secondary**: #3B82F6（亮蓝）
- **CTA**: #F59E0B（琥珀色）
- **Background**: #F8FAFC（浅灰白）
- **Typography**: Fira Code / Fira Sans（数据仪表盘风格）

---

## Task 1: 后端 API 扩展

### 1.1 添加统计 API
**文件**: `web/backend/main.py`

新增接口：
- `GET /api/stats` - 返回统计数据（论文数量、存储空间、分类分布等）

```python
@app.get("/api/stats")
async def get_stats():
    # 返回论文总数、数据库大小、分类统计等
```

### 1.2 扩展列表 API 支持排序
**文件**: `web/backend/main.py`

修改接口：
- `GET /api/papers` - 添加 `sort_by` 和 `order` 参数

### 1.3 添加删除 API
**文件**: `web/backend/main.py`

新增接口：
- `DELETE /api/papers/{arxiv_id}` - 删除指定论文

### 1.4 批量保存 API
**文件**: `web/backend/main.py`

新增接口：
- `POST /api/papers/batch-save` - 批量保存选中的论文

---

## Task 2: 前端路由配置

### 2.1 安装 Vue Router
**命令**: `cd web/frontend && npm install vue-router@4`

### 2.2 创建路由配置
**文件**: `web/frontend/src/router/index.ts`

路由结构：
- `/` - 首页（搜索页）
- `/papers` - 数据库论文列表
- `/papers/:id` - 论文详情页
- `/stats` - 统计数据页

---

## Task 3: 前端 API 服务扩展

### 3.1 更新 API 服务
**文件**: `web/frontend/src/api.ts`

新增方法：
```typescript
// 统计数据
getStats(): Promise<Stats>

// 删除论文
deletePaper(arxivId: string): Promise<void>

// 批量保存
batchSave(papers: Paper[]): Promise<void>

// 带排序的搜索
searchWithSort(query, maxResults, sortBy, order): Promise<Paper[]>
```

---

## Task 4: 统计数据页面

### 4.1 创建统计页面组件
**文件**: `web/frontend/src/views/StatsView.vue`

功能：
- 论文总数卡片
- 数据库大小卡片
- 分类分布图表（饼图/条形图）
- 最近添加的论文

### 4.2 设计要点
- 使用 Bento Grid 布局
- 统计卡片使用渐变背景
- 图表使用简洁的 SVG 或 Canvas

---

## Task 5: 论文列表页面

### 5.1 创建列表页面组件
**文件**: `web/frontend/src/views/PapersView.vue`

功能：
- 表格形式展示论文数据
- 列：arXiv ID、标题、作者、分类、日期、操作
- 支持排序（点击表头）
- 分页组件
- 搜索过滤

### 5.2 表格设计
- 响应式：移动端转为卡片布局
- 行悬停高亮
- 点击行进入详情页
- 操作列：查看详情、删除

---

## Task 6: 论文详情页面

### 6.1 创建详情页面组件
**文件**: `web/frontend/src/views/PaperDetailView.vue`

功能：
- 完整显示论文所有属性
- 美观的布局设计
- 返回列表按钮
- PDF/arXiv 链接

### 6.2 详情页布局
```
┌─────────────────────────────────────┐
│  返回按钮                            │
├─────────────────────────────────────┤
│  arXiv ID 标签    版本    日期       │
│  论文标题（大字体）                   │
├─────────────────────────────────────┤
│  作者列表                            │
├─────────────────────────────────────┤
│  分类标签                            │
├─────────────────────────────────────┤
│  摘要（完整显示）                     │
├─────────────────────────────────────┤
│  元数据区域                          │
│  - 发布日期                          │
│  - 更新日期                          │
│  - PDF 链接                          │
│  - arXiv 链接                        │
├─────────────────────────────────────┤
│  操作按钮                            │
│  [下载 PDF]  [访问 arXiv]  [删除]    │
└─────────────────────────────────────┘
```

---

## Task 7: 搜索页面改进

### 7.1 更新搜索组件
**文件**: `web/frontend/src/views/HomeView.vue`

新功能：
- 排序选择器（按日期、相关性）
- 分页组件
- 搜索结果列表（不自动保存）
- 每条结果带复选框
- "保存选中" 按钮
- 点击论文可预览详情（模态框或侧边栏）

### 7.2 搜索结果设计
```
┌─────────────────────────────────────┐
│  搜索框                              │
│  排序: [日期 ▼]  顺序: [降序 ▼]      │
├─────────────────────────────────────┤
│  ☐ 论文1  [预览]                     │
│  ☐ 论文2  [预览]                     │
│  ☐ 论文3  [预览]                     │
├─────────────────────────────────────┤
│  已选中 2 篇  [保存选中]              │
├─────────────────────────────────────┤
│  < 1 2 3 4 5 >                       │
└─────────────────────────────────────┘
```

---

## Task 8: 论文预览模态框

### 8.1 创建预览组件
**文件**: `web/frontend/src/components/PaperPreview.vue`

功能：
- 模态框形式显示论文详情
- 快速预览摘要、作者等关键信息
- "保存到数据库" 按钮
- "查看完整详情" 按钮

---

## Task 9: 分页组件

### 9.1 创建分页组件
**文件**: `web/frontend/src/components/Pagination.vue`

功能：
- 显示页码
- 上一页/下一页按钮
- 跳转到指定页
- 显示总数信息

---

## Task 10: 导航组件

### 10.1 创建导航栏组件
**文件**: `web/frontend/src/components/NavBar.vue`

导航项：
- 首页（搜索）
- 数据库
- 统计

---

## Task 11: 更新样式系统

### 11.1 更新全局样式
**文件**: `web/frontend/src/style.css`

更新：
- 新的颜色变量
- Fira Code / Fira Sans 字体
- 表格样式
- 模态框样式
- 分页组件样式

---

## Task 12: 更新 App.vue

### 12.1 集成路由和导航
**文件**: `web/frontend/src/App.vue`

更新：
- 添加 NavBar 组件
- 添加 RouterView
- 布局调整

---

## 文件结构预览

```
web/frontend/src/
├── api.ts                    # API 服务
├── main.ts                   # 入口文件
├── style.css                 # 全局样式
├── App.vue                   # 根组件
├── router/
│   └── index.ts              # 路由配置
├── views/
│   ├── HomeView.vue          # 首页（搜索）
│   ├── PapersView.vue        # 论文列表
│   ├── PaperDetailView.vue   # 论文详情
│   └── StatsView.vue         # 统计页面
└── components/
    ├── NavBar.vue            # 导航栏
    ├── PaperCard.vue         # 论文卡片
    ├── PaperPreview.vue      # 论文预览模态框
    ├── Pagination.vue        # 分页组件
    └── StatsCard.vue         # 统计卡片
```

---

## 实现顺序

1. **Task 1**: 后端 API 扩展（统计、排序、删除、批量保存）
2. **Task 2**: 前端路由配置
3. **Task 3**: API 服务扩展
4. **Task 10**: 导航组件
5. **Task 11**: 更新样式系统
6. **Task 4**: 统计数据页面
7. **Task 5**: 论文列表页面
8. **Task 9**: 分页组件
9. **Task 6**: 论文详情页面
10. **Task 8**: 论文预览模态框
11. **Task 7**: 搜索页面改进
12. **Task 12**: 更新 App.vue
