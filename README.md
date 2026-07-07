# UiBot RPA + AI 知识库项目

> **企业级 RPA 自动化 | AI 知识库冷热分层架构 | UiBot + Python + MySQL + OCR**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/RPA-UiBot-orange)]()
[![Python](https://img.shields.io/badge/Python-3.8+-green)]()

---

## 我做了什么

把 AI 编程助手（Claude Code）在 UiBot RPA 平台上的开发效率提升了 **80%**，核心手段是自研了一套**知识库冷热分层架构**——借鉴 CPU L1/L2/L3 Cache 设计思想，把 467 行混乱的单文件重构为三级缓存体系。

同时用这套体系开发了 2 个实际落地的企业级 RPA 项目。

---

## 🏆 知识库冷热分层架构

> 这是整个项目最有价值的智力产出，也是面试中最能拉开差距的讲点。

### 架构设计

```
L1 热数据 (CLAUDE.md, 600行)
  └─ 55 个高频命令, 每次对话自动加载, 95% 命中率
      └─ 未命中 ↓
L2 冷路由 (uibot-api-full.md, 300行)
  └─ 26 模块精准跳转 + 行号缓存, 二次命中省 90% token
      └─ 未命中 ↓
L3 源文件 (D:\references\, 24文件)
  └─ 全量官方文档, 首次读全文件, 自动写回行号到 L2
```

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 为什么不把 300 个命令都放热路径？ | 只放高频 55 个 | 热路径每次对话全量加载，塞太多反而拖慢 90% 的日常查询 |
| 行号缓存放哪？ | 持久化到 L2 文件 | 不依赖短期记忆（上下文），重启对话、复制到新项目仍有效 |
| D:\references 为什么是一级目录？ | 去 UiBot 版本号依赖 | 路径从 105 字符降到 25 字符，实现真正 portable |
| 白名单为什么拆成 4 张表？ | 按功能域分表 | AI 扫表成本 O(n) → O(n/4)，查 Split 只进字符串表不碰其他 3 张 |

### V1 → V6 演进

```
V1: 467行混乱单文件 → V2: 三层分架+导航索引 → V3: 白名单拆4表+去重+矛盾修复
  → V4: 冷热分流+26模块路由表 → V5: 去版本号 → V6: 行号缓存持久化
```

### 量化效果（每个改动都有前后对比数据）

| 指标 | 改前 (V1) | 改后 (V6) | 提升 |
|------|-----------|----------|------|
| 平均检索行数 | ~200 行/次 | ~40 行/次 | **-80%** |
| 最差检索行数 | 467 行 | 66 行 | **-86%** |
| 冷查询二次命中 | ~200 行 | ~15 行 | **省 90% token** |
| 热路径命中率 | ~50% | **95%** | — |
| 新项目部署 | 重写全部 | ≤5 分钟 | 49KB 便携包 |

### 核心代码

| 文件 | 看点 |
|------|------|
| [knowledge-base/CLAUDE.md](knowledge-base/CLAUDE.md) | 600行知识索引设计：三重标签体系、4张分类速查小表、交叉引用去重 |
| [knowledge-base/uibot-api-full.md](knowledge-base/uibot-api-full.md) | 26模块冷路由表：路径+行号精准跳转，不重复抄文档 |
| [docs/knowledge-base-architecture.md](docs/knowledge-base-architecture.md) | 完整架构设计文档（含面试讲解提纲） |

---

## 📁 落地项目

### 资金日报自动化

企业银行流水 RPA，4 家银行格式不同但**零硬编码分支**，ETL 全自动入库。

**技术问题 + 解决思路**：

| 遇到的坑 | 怎么解决的 |
|----------|-----------|
| 4 家银行 Excel 格式各不相同 | 动态表头探测：扫描前30行按关键字命中数打分，自动匹配列映射 |
| 流程中断后数据重复 | 状态表 + 幂等检查：每个节点先查是否已完成，3 次重试 |
| MySQL 连接隔离导致变量不共享 | 放弃 `SET @seq`，改用子查询 COUNT 计数生成序号 |
| 同日多笔交易顺序不确定 | 用 business_no（按流水时间+主键编排）保证余额递进正确 |

→ [查看全部代码](projects/01-daily-fund-report/)

### PDF OCR 识别系统

多策略 PDF 文字提取，自动判断 PDF 类型走最优引擎。

**技术问题 + 解决思路**：

| 遇到的坑 | 怎么解决的 |
|----------|-----------|
| 数字 PDF 和扫描件混在一起 | 前 3 页文字量自动检测：≥50字符走 PyMuPDF，<50 走 PaddleOCR |
| 扫描件红章干扰 OCR | OpenCV 颜色过滤 + 形态学操作去除红章，识别率提升 12% |
| PaddleOCR 内存泄漏 | 每 10 页重建 OCR 实例，防止长时间运行 OOM |
| Windows oneDNN 冲突 | 启动时禁用 `FLAGS_use_mkldnn`，否则线程池异常 |

→ [查看全部代码](projects/04-pdf-ocr/)

---

## 🛠 技术栈

```
RPA:       UiBot (UB 方言 .task + Python .py + apa_runtime)
数据库:    MySQL, Excel (WPS/Office)
OCR:       PaddleOCR, PyMuPDF (fitz), OpenCV, PIL
AI 工具:   Claude Code + 自定义知识库
核心模式:  3次重试+幂等检查, 自适应解析, 冷热分层缓存
```

---

## 💡 面试亮点（30 秒）

> "我把 AI 编程助手的知识库从 467 行混乱单文件重构为三级缓存架构。不是简单拆分文件，而是按访问频率做数据分级——热数据自动加载秒回，冷数据按需精准跳行。每个改动都有前后数据对比，平均查询从 200 行降到 40 行，命中率 95%，冷查询二次命中省 90% token。"

---

## 📂 目录

```
├── README.md
├── knowledge-base/                  # 知识库冷热分层架构（核心）
├── projects/
│   ├── 01-daily-fund-report/        # 资金日报 RPA
│   └── 04-pdf-ocr/                  # PDF OCR 识别
├── docs/
│   └── knowledge-base-architecture.md
└── scripts/
    └── generate_docs.py
```
