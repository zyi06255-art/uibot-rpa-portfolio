# UiBot RPA + AI Knowledge Base Portfolio

> **企业级 RPA 自动化项目组合 | AI 知识库冷热分层架构 | UiBot + Python + MySQL + OCR**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Projects](https://img.shields.io/badge/Projects-7-blue)]()
[![Platform](https://img.shields.io/badge/RPA-UiBot-orange)]()
[![Python](https://img.shields.io/badge/Python-3.8+-green)]()
[![AI](https://img.shields.io/badge/AI-Claude_Code-purple)]()

---

## 概览 Overview

本仓库展示了 **7 个企业级 RPA（机器人流程自动化）项目**，基于来也科技 UiBot 平台开发，覆盖财务自动化、文档 OCR 识别、发票查验、数据处理等场景。同时包含一套**自研的 AI 知识库冷热分层架构**——大幅提升 LLM 编程助手在 RPA 开发中的效率。

> This repository showcases **7 enterprise-grade RPA projects** built on the Laiye UiBot platform, alongside a **novel AI knowledge base architecture** that boosts LLM-assisted RPA development efficiency by 80%.

---

## 🏆 核心创新：知识库冷热分层架构

> Core Innovation: The AI Knowledge Base Cold-Hot Layered Architecture

这是本仓库**最独特的知识资产**——将 AI 编程助手的知识库从一张 467 行全扫描大表，重构为借鉴 CPU L1/L2/L3 Cache 思想的**三级缓存体系**。

| 层级 | 文件 | 数据量 | 命中率 | 查询行数 |
|------|------|--------|--------|----------|
| **L1 热数据** | `CLAUDE.md` (600行) | 55 个已验证命令 | **95%** | 22~54 行 |
| **L2 冷路由** | `uibot-api-full.md` (300行) | 26 模块 + 行号索引 | 5% | 路由30行 + 精准跳15行 |
| **L3 源文件** | `D:\references\` (24文件) | 全量函数签名 | 兜底 | ~200 行 |

### 量化效果 Quantifiable Results

| 指标 | 改造前 (V1) | 改造后 (V6) | 提升 |
|------|-----------|-----------|------|
| 平均检索行数 | ~200 行/次 | ~40 行/次 | **-80%** |
| 最差检索行数 | 467 行 (全文件扫描) | 66 行 | **-86%** |
| 冷查询二次命中 | ~200+行 | ~15行 | **省 90% token** |
| 热路径命中率 | ~50% | **95%** | +45% |
| 新项目部署 | 重写全部 | ≤5 分钟 | **49KB 便携包** |

### V1 → V6 演进路线 Evolution Path

```
V1 (467行混乱单文件) → V2 (三层分架+导航) → V3 (白名单拆4表+去重+CDbl修复)
  → V4 (冷热分流+26模块路由表) → V5 (D:\references去版本号) → V6 (行号缓存持久化)
```

详见 → [knowledge-base/](knowledge-base/) 和 [docs/knowledge-base-architecture.md](docs/knowledge-base-architecture.md)

---

## 📁 项目索引 Project Index

### 🔵 企业 RPA 自动化 Enterprise RPA

| # | 项目 Project | 描述 Description | 关键技术 Key Skills |
|---|-------------|-----------------|-------------------|
| 01 | [资金日报](projects/01-daily-fund-report/) | 4 银行流水自动抓取、解析、入库 | MySQL, 自适应Excel解析, 幂等重试 |
| 02 | [产销存日报](projects/02-production-sales-inventory/) | 每日产销存报表自动生成 | 多步流程编排, HTML报告 |
| 03 | [自动导入收款单](projects/03-auto-receipt-import/) | 端到端收款单导入自动化 | 系统登录, 状态管理, 知识库集成 |

### 🟢 AI + OCR 智能识别 AI + OCR

| # | 项目 Project | 描述 Description | 关键技术 Key Skills |
|---|-------------|-----------------|-------------------|
| 04 | [PDF OCR 识别系统](projects/04-pdf-ocr/) | 多策略 PDF 文字提取 | PyMuPDF, PaddleOCR, OpenCV红章去除 |
| 05 | [发票查验](projects/05-invoice-verification/) | 发票信息自动提取与校验 | OCR + 结构化提取 |

### 🟡 教育/数据处理 Educational

| # | 项目 Project | 描述 Description | 关键技术 Key Skills |
|---|-------------|-----------------|-------------------|
| 06 | [学生成绩管理](projects/06-student-grades/) | 成绩数据自动化处理 | Excel自动化, 数据聚合 |
| 07 | [财务报表分析](projects/07-coursework/) | 财务数据自动整理与分析 | 财务建模, 数据分析 |

---

## 🛠 技术栈 Technical Stack

```
RPA 平台:     UiBot Community Edition (UB 方言 .task + Python .py)
数据库:       MySQL (pymysql), Excel (WPS/Office)
OCR:          PaddleOCR, PyMuPDF (fitz), OpenCV, PIL
文档生成:     python-docx, HTML Templates
AI 助手:      Claude Code + 自定义知识库集成
核心模式:     3 次重试 + 幂等检查, 自适应解析 (零硬编码分支)
```

---

## 📖 知识库便携包 Knowledge Base Portable Package

```
knowledge-base/          ← 49KB，复制到任何 UiBot 项目即用
├── CLAUDE.md            # 热知识: 全局编码规范 + UB方言规则 + 55个已验证命令速查
├── uibot-api-full.md   # 冷路由: 26模块精准跳转 + 行号缓存
├── settings.json        # 权限预授权 (D:\references\ 免弹框)
└── README.md            # 5分钟部署指南
```

**适用于任何 UiBot RPA 项目**：第一章 [全局] 和第二章 [领域] 直接复用，只需修改第三章 [项目] 专属内容。

---

## 🚀 快速开始 Quick Start

### 前置条件 Prerequisites

1. 安装 [来也 UiBot 社区版](https://www.laiye.com/product/uibot)
2. Python 3.8+ with pip
3. MySQL 5.7+ (用于数据库相关项目)

### 安装依赖 Install Dependencies

```bash
pip install -r requirements.txt
```

### 部署知识库 Deploy Knowledge Base

```bash
# 1. 将 UiBot 安装目录下的 references/ 复制到 D:\references\ (一次性)
# 2. 将 knowledge-base/ 文件夹复制到你的 UiBot 项目根目录
# 3. 将 CLAUDE.md 和 uibot-api-full.md 放在项目根目录
# 4. 将 settings.json 放在项目的 .claude/ 目录
```

---

## 🎯 面试官看这里 For Recruiters

### 30 秒电梯演讲

> "我把 AI 编程助手的知识库从一张 467 行全扫描的大表，重构为三级缓存架构。L1 热数据 55 个命令自动加载秒回，L2 冷路由 26 模块按需精准跳行，L3 官方源文件做行号缓存。单次查询从 200 行降到 40 行，命中率 95%，冷查询二次命中省 90% token。整个 49KB portable 包复制到新项目 5 分钟就能用。"

### 核心能力 Key Competencies

- **RPA 架构设计**：独立设计并实现了包含容错、幂等、自适应解析的 RPA 流程框架
- **AI 工程化**：对 LLM 上下文窗口优化有深入理解（冷热分层、行号缓存、标签索引）
- **跨技术栈整合**：UiBot UB 方言 + Python + MySQL + OCR 的混合架构
- **量化思维**：每个改动都有前后数据对比，用数字说话
- **知识沉淀**：将隐性经验转化为可复制的结构化知识库

### 推荐审计的核心代码 Recommended Code Review

| 文件 | 亮点 |
|------|------|
| [knowledge-base/CLAUDE.md](knowledge-base/CLAUDE.md) | 600行知识索引设计，三重标签体系 |
| [projects/01-daily-fund-report/CLAUDE.md](projects/01-daily-fund-report/CLAUDE.md) | 自适应解析 + 容错模式实例化 |
| [projects/04-pdf-ocr/PDF识别.py](projects/04-pdf-ocr/PDF识别.py) | 数字/扫描PDF双策略识别 |
| [projects/04-pdf-ocr/ocr_paddle.py](projects/04-pdf-ocr/ocr_paddle.py) | OpenCV红章去除 + PaddleOCR |

---

## 📂 目录结构 Full Directory Structure

```
uibot-rpa-portfolio/
├── README.md                    # 本文件
├── LICENSE                      # MIT License
├── requirements.txt             # Python 依赖
│
├── docs/                        # 扩展文档
│   └── knowledge-base-architecture.md
│
├── knowledge-base/              # 便携知识库包 (49KB)
│   ├── CLAUDE.md                # L1 热知识
│   ├── uibot-api-full.md       # L2 冷路由
│   ├── settings.json            # 权限配置
│   └── README.md                # 部署说明
│
├── projects/
│   ├── 01-daily-fund-report/    # 资金日报
│   ├── 02-production-sales-inventory/
│   ├── 03-auto-receipt-import/
│   ├── 04-pdf-ocr/
│   ├── 05-invoice-verification/
│   ├── 06-student-grades/
│   └── 07-coursework/
│
├── scripts/                     # 工具脚本
│   └── generate_docs.py
│
└── .github/
    └── workflows/
        └── validate-kb.yml
```

---

## 📝 许可 License

MIT License — 详见 [LICENSE](LICENSE)

---

<p align="center">
  <sub>Built with ❤️ using UiBot + Python + Claude Code | 2026</sub>
</p>
