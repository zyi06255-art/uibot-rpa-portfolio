# UiBot RPA + AI 知识库项目

> **企业级 RPA 自动化 | AI 知识库冷热分层架构 | UiBot + Python + MySQL + OCR**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/RPA-UiBot-orange)]()
[![Python](https://img.shields.io/badge/Python-3.8+-green)]()

---

## 概览

本仓库展示 **2 个企业级 RPA 项目** + 一套**自研 AI 知识库冷热分层架构**。核心亮点是将 AI 编程助手的知识库从混乱的单文件重构为三级缓存体系，量化提升 80%。

---

## 🏆 知识库冷热分层架构

借鉴 CPU L1/L2/L3 Cache 思想，将知识库分为三级：

| 层级 | 文件 | 数据量 | 命中率 | 查询行数 |
|------|------|--------|--------|----------|
| **L1 热** | `CLAUDE.md` (600行) | 55 个已验证命令 | **95%** | 22~54 行 |
| **L2 冷** | `uibot-api-full.md` (300行) | 26 模块 + 行号缓存 | 5% | ~15 行（缓存后） |
| **L3 源** | `D:\references\` (24文件) | 全量官方文档 | 兜底 | ~200 行 |

### V1 → V6 演进

```
467行混乱单文件 → 三层分架+导航 → 白名单拆分+去重 → 冷热分流+路由表 → 去版本号 → 行号缓存
```

### 量化效果

| 指标 | 改前 | 改后 | 提升 |
|------|------|------|------|
| 平均检索 | ~200 行/次 | ~40 行/次 | **-80%** |
| 最差检索 | 467 行 | 66 行 | **-86%** |
| 冷查询二次命中 | ~200 行 | ~15 行 | **省 90% token** |
| 新项目部署 | 重写全部 | **≤5 分钟** | 49KB 便携包 |

详见 → [knowledge-base/](knowledge-base/) · [架构设计文档](docs/knowledge-base-architecture.md)

---

## 📁 项目

### 01 — 资金日报自动化（旗舰）

企业级 RPA，自动从 4 家银行 Excel 流水中提取数据、清洗、入库，生成每日资金日报。

**亮点**：
- **自适应解析**：4 家银行格式不同但零硬编码分支，动态表头探测 + 列映射
- **容错 + 幂等**：每个节点 3 次重试 + 状态表追踪，断点续传
- **技术栈**：UiBot UB 方言 + Python + MySQL

| 文件 | 说明 |
|------|------|
| [PDF识别.py](projects/04-pdf-ocr/PDF识别.py) | 双引擎 PDF 识别主流程 |
| [ocr_paddle.py](projects/04-pdf-ocr/ocr_paddle.py) | PaddleOCR + OpenCV 红章去除 |
| [Python流程块.py](projects/01-daily-fund-report/Python流程块.py) | 环境初始化 + 重试机制 |

→ [项目详情](projects/01-daily-fund-report/)

### 04 — PDF OCR 识别系统

多策略 PDF 文字提取：数字 PDF 用 PyMuPDF 直接提取，扫描件用 PaddleOCR。支持承兑汇票、发票等。

**亮点**：
- **智能类型检测**：前 3 页文字量自动判断 PDF 类型
- **双引擎**：PyMuPDF (数字) + PaddleOCR (扫描)，自动切换
- **OCR 评估**：量化评估识别准确率，对比 Ground Truth
- **技术栈**：PyMuPDF + PaddleOCR + OpenCV + PIL

→ [项目详情](projects/04-pdf-ocr/)

---

## 🛠 技术栈

```
RPA 平台:  UiBot Community Edition (UB 方言 .task + Python .py)
数据库:    MySQL (pymysql), Excel
OCR:       PaddleOCR, PyMuPDF (fitz), OpenCV
AI 助手:   Claude Code + 自定义知识库
核心模式:  3 次重试 + 幂等检查, 自适应解析
```

---

## 🎯 面试官看这里

> "我把 AI 编程助手的知识库从 467 行混乱单文件重构为三级缓存架构。L1 热数据自动加载秒回，L2 冷路由按需精准跳行，L3 源文件做行号缓存。平均查询从 200 行降到 40 行，命中率 95%，冷查询二次命中省 90% token。49KB portable 包 5 分钟部署到新项目。"

**推荐审计的核心代码**：
- [knowledge-base/CLAUDE.md](knowledge-base/CLAUDE.md) — 600行知识索引，三重标签体系
- [projects/01-daily-fund-report/CLAUDE.md](projects/01-daily-fund-report/CLAUDE.md) — 自适应解析 + 容错模式
- [projects/04-pdf-ocr/PDF识别.py](projects/04-pdf-ocr/PDF识别.py) — 数字/扫描 PDF 双策略识别

---

## 快速开始

```bash
pip install -r requirements.txt

# 部署知识库：将 knowledge-base/ 复制到 UiBot 项目根目录即可
```

---

## 📂 目录结构

```
├── README.md
├── knowledge-base/          # 便携知识库 (49KB)
│   ├── CLAUDE.md            # L1 热知识
│   ├── uibot-api-full.md   # L2 冷路由
│   └── settings.json
├── projects/
│   ├── 01-daily-fund-report/   # 资金日报
│   └── 04-pdf-ocr/             # PDF OCR 识别
├── docs/
│   └── knowledge-base-architecture.md
├── scripts/
│   └── generate_docs.py
└── .github/workflows/
    └── validate-kb.yml
```

## 📝 License

MIT
